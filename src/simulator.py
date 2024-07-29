import threading
from multiprocessing import Process
import subprocess
import uvicorn
import sys
import os
import time
import json
import signal
from dataclasses import dataclass, field, asdict
from typing import Optional, List

from generator.generator import Generator
from sender.sender import Sender
from msg_queue.msg_queue import MessageQueue
from monitor.backend.main import app

OPTIONS = ["-h", "-c", "-m", "-s", "-S", "-u"]
monitor = None
api = None

# Signal handler for the end of the simulation
# Cleanly kill processes rather than let the 
# user hit Ctrl-C five times to kill everything.
def finish_handler(signum, frame):
    print("\nExiting...")
    monitor.kill()
    api.kill()
    api.join()

# --- Config Classes ---
@dataclass
class SenderSettings:
    mean_delay: Optional[float] = 0.5
    fail_rate: Optional[float] = 0.5

@dataclass
class SimulatorConfig:
    num_messages: Optional[int] = 1000
    num_senders: Optional[int] = 10
    sender_settings: Optional[list[SenderSettings]] = field(default_factory=list)
    monitor_url: Optional[str] = "http://localhost:8000" # potentially configurable in the future!
    monitor_update_interval: Optional[int] = 1

# --- Helper functions for Simulation Main ---

def print_help_message(code: Optional[int] = 0):
    '''
        Print message on Simulator usage and options.
    '''

    print("SMS Simulator CLI")
    print("Usage: python simulator.py <OPTIONS>")
    print("")
    print("Options:")
    print("\t-h:                            Print this help message and exit")
    print("\t-c  <path/to/config.json>:     Provide path to JSON config file for simulator")
    print("\t                                 Note that any config values set by flags before using this option")
    print("\t                                 will be overwritten, and any flags succeeding loading values")
    print("\t                                 from a config file will overwrite the values from the file.")
    print("\t-m  <num_messages>:            Set 'num_messages' to non-negative integer value number of messages")
    print("\t-s  <mean_delay>,<fail_rate>:  Provide configuration for a single Sender")
    print("\t                               mean_delay: non-negative floating point number")
    print("\t                               fail_rate: floating point number in range [0,1]")
    print("\t                                 The -s option can be repeated multiple times.")
    print("\t                                 If the number of sender configs is more than the provided value for 'num_senders'")
    print("\t                                 then the number of senders will be increased to match.")
    print("\t-S  <num_senders>:             Set 'num_senders' to positive integer value for number of senders.")
    print("\t                                 Senders which are not explicitly provided configuration values will use default")
    print("\t                                 values of 0.5s mean delay and 0.5 failure rate.")
    print("\t-u  <monitor_update_interval>: Set 'monitor_update_interval' to floating point number greater than 0.5")
    sys.exit(code)

def adjust_senders(config: SimulatorConfig):
    '''
        Adjust either num_senders or sender_settings
        to accommodate the 'larger' of the two
    '''
    if config.num_senders < len(config.sender_settings):
        config.num_senders = len(config.sender_settings)
    else:
        gap = config.num_senders - len(config.sender_settings)
        for _ in range(gap):
            config.sender_settings.append(SenderSettings())
    return config

def set_config_from_file(config: SimulatorConfig, filepath: str):
    '''
        Load in configuration values from json file
    '''

    with open(filepath, "r") as cfgfile:
        config_dict = json.load(cfgfile)

    for key in config_dict:
        match key:
            case "num_messages":
                config.num_messages = int(config_dict[key])
            case "num_senders":
                config.num_senders = int(config_dict[key])
            case "monitor_update_interval":
                config.monitor_update_interval = float(config_dict[key])
            case "sender_settings":
                config.sender_settings = [SenderSettings(**obj) for obj in config_dict[key]]
            case _:
                print(f"Unrecognized key in config: {key}! Ignoring...")

    return config

def process_arguments(argv) -> SimulatorConfig:
    '''
        Handle command-line arguments to set config
    '''

    config = SimulatorConfig()

    used_options = []
    option = ""
    i = 0
    while i < len(argv):
        try:
            option = argv[i]

            if option in used_options and option != "-s":
                raise SyntaxError(f"Config value for flag '{option}' already set!")
            if option not in OPTIONS:
                raise SyntaxError(f"Unrecognized flag {option}!")
            if option != "-h" and (i+1 >= len(argv) or argv[i+1] in OPTIONS):
                raise SyntaxError(f"Must provide value for flag {option}!")

            i += 1
            match option:
                case "-h":
                    print_help_message()
                case "-c":
                    filepath = argv[i]
                    if os.path.isfile(filepath):
                        config = set_config_from_file(config, filepath)
                    else:
                        raise ValueError(f"File '{filepath}' does not exist!")
                case "-m":
                    config.num_messages = int(argv[i])
                case "-S": 
                    config.num_senders = int(argv[i])
                case "-s":
                    mean_delay, fail_rate = argv[i].split(",")
                    config.sender_settings.append(SenderSettings(mean_delay=float(mean_delay), fail_rate=float(fail_rate)))
                case "-u":
                    config.monitor_update_interval = float(argv[i])
            
            i += 1
            used_options.append(option)

        except SyntaxError as e:
            print(f"Error while setting configuration values! {e}\n")
            print_help_message(code=1)
        except ValueError as e:
            print(f"Error while setting configuration values! {e}")
            print_help_message(code=1)
        except json.decoder.JSONDecodeError as e:
            print("Error retrieving configuration values from file! {e}")
            print_help_message(code=1)

    return config

def launch_monitor(config: SimulatorConfig) -> tuple[Process, subprocess.Popen]:
    '''
        Launch both front and backend for Monitor component 
        in separate processes
    '''
    
    os.environ["SMS_UPDATE_INTERVAL"] = str(config.monitor_update_interval)
    api_proc = Process(target=uvicorn.run, args=(app,), kwargs={
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "error"
    })
    api_proc.start()

    monitor_dir = str(os.path.dirname(os.path.abspath(__file__))) + "/monitor/frontend"
    monitor_proc = subprocess.Popen(["node", "build"], cwd=monitor_dir)

    return api_proc, monitor_proc

def launch_simulation(
        config: SimulatorConfig, 
        queue: MessageQueue
) -> tuple[list[Sender], list[threading.Thread], threading.Thread]:
    '''
        Launch Generator and requested Senders in their own
        threads to start simulation. All threads reference the 
        same message queue.
    '''

    senders = []
    sender_threads = []

    for sender in config.sender_settings:
        senders.append(Sender(queue, monitor_url=config.monitor_url, **asdict(sender)))
        sender_threads.append(
            threading.Thread(target=senders[-1].consume_messages)
        )
        sender_threads[-1].start()
    
    generator = Generator(queue, config.num_messages)
    
    generator_thread = threading.Thread(target=generator.start_generating)
    generator_thread.start()

    return senders, sender_threads, generator_thread

def main(*args):
    '''
        Main function for Simulator.
        Process command-line arguments then launch all components.
        Set up signal handler at end for easy exit.
    '''

    global monitor, api

    if len(args) == 1:
        print("No configuration options provided! Using default settings...")
        config = SimulatorConfig()
    else:
        config = process_arguments(list(args)[1:])

    config = adjust_senders(config)

    print("Configuration loaded, launching monitor...\n")

    api, monitor = launch_monitor(config)

    print("Simulation Progress Monitor is viewable at http://localhost:3000 !")
    print("Launching simulation... \n")

    message_queue = MessageQueue()

    senders, sender_threads, generator_thread = launch_simulation(config, message_queue)

    print("Simulation started! Waiting for all messages to be consumed...")

    while message_queue.length() > 0:
        time.sleep(0.5)
    
    for sender in senders:
        sender.finish_consuming = True

    for st in sender_threads:
        st.join()

    generator_thread.join()

    print("All messages have been consumed! You can browse the monitor for as long as you please, then use Ctrl+C to finish.")
    signal.signal(signal.SIGINT, finish_handler)

if __name__ == "__main__":
    main(*sys.argv)