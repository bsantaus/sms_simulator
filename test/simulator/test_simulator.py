import pytest
from unittest.mock import MagicMock

import time
import threading

from simulator import *

def test_adjust_senders():

    custom_sender = SenderSettings(mean_delay=0.1, fail_rate=0.5)
    cfg_no_change = SimulatorConfig(
        num_senders = 1,
        sender_settings=[custom_sender]
    )

    tst_config = adjust_senders(cfg_no_change)

    assert tst_config.num_senders == 1
    assert len(tst_config.sender_settings) == 1
    assert tst_config.sender_settings[0] == custom_sender

    cfg_adjust_num = SimulatorConfig(
        num_senders=1,
        sender_settings=[custom_sender, custom_sender, custom_sender]
    )

    tst_config = adjust_senders(cfg_adjust_num)

    assert tst_config.num_senders == 3
    assert len(tst_config.sender_settings) == 3
    for i in range(len(tst_config.sender_settings)):
        assert tst_config.sender_settings[i] == custom_sender
    
    cfg_add_default_senders = SimulatorConfig(
        num_senders=2,
        sender_settings=[]
    )

    tst_config = adjust_senders(cfg_add_default_senders)

    assert tst_config.num_senders == 2
    assert len(tst_config.sender_settings) == 2
    for i in range(len(tst_config.sender_settings)):
        assert tst_config.sender_settings[i] == SenderSettings()

def test_set_cfg_from_file():
    with open("tst.json", "w") as test_config_file:
        json.dump({
            "num_messages": 100,
            "num_senders": 2,
            "monitor_update_interval": 1.1,
            "sender_settings": [
                {
                    "mean_delay": 0.2,
                    "fail_rate": 0.1
                },
                {
                    "mean_delay": 0.5,
                    "fail_rate": 0.4
                }
            ]
        }, test_config_file)

    test_config = set_config_from_file(SimulatorConfig(), filepath="tst.json")

    assert test_config.num_messages == 100
    assert test_config.num_senders == 2
    assert test_config.monitor_update_interval == 1.1
    assert len(test_config.sender_settings) == 2
    assert test_config.sender_settings[0].mean_delay == 0.2
    assert test_config.sender_settings[0].fail_rate == 0.1
    assert test_config.sender_settings[1].mean_delay == 0.5
    assert test_config.sender_settings[1].fail_rate == 0.4


    with open("tst_type_error.json", "w") as test_config_file:
        json.dump({
            "num_messages": 100,
            "num_senders": 2,
            "monitor_update_interval": "abc",
        }, test_config_file)

    with pytest.raises(ValueError):
        set_config_from_file(SimulatorConfig, "tst_type_error.json")
    
    with open("tst_bad_json.json", "w") as test_config_file:
        test_config_file.write("abc")

    with pytest.raises(json.decoder.JSONDecodeError):
        set_config_from_file(SimulatorConfig, "tst_bad_json.json")

def test_process_arguments():
    with open("tst.json", "w") as test_config_file:
        json.dump({
            "num_messages": 100,
            "num_senders": 2,
            "monitor_update_interval": 1.1,
            "sender_settings": [
                {
                    "mean_delay": 0.2,
                    "fail_rate": 0.1
                },
                {
                    "mean_delay": 0.5,
                    "fail_rate": 0.4
                }
            ]
        }, test_config_file)

    cases = [
        ([], SimulatorConfig(), None),
        (["-h"], None, SystemExit),
        (["-m", "10", "-S", "1", "-s", "1,1", "-u", "1.0"], 
         SimulatorConfig(
            num_messages=10,
            num_senders=1,
            sender_settings=[SenderSettings(mean_delay=1, fail_rate=1)],
            monitor_update_interval=1.0
         ), 
         None
        ),
        (["-m", "10", "-h"], None, SystemExit),
        (["-m", "10", "-m", "10"], None, SystemExit),
        (["-s", "0.1,0.1", "-s", "0.2,0.2"], SimulatorConfig(
            sender_settings=[
                SenderSettings(mean_delay=0.1, fail_rate=0.1),
                SenderSettings(mean_delay=0.2, fail_rate=0.2),
            ]
        ), None),
        (["-c", "tst.json"], SimulatorConfig(
            num_messages=100,
            num_senders=2,
            sender_settings=[
                SenderSettings(mean_delay=0.2, fail_rate=0.1),
                SenderSettings(mean_delay=0.5, fail_rate=0.4)
            ],
            monitor_update_interval=1.1
        ), None),
        (["-m", "23", "-c", "tst.json", "-S", "3"], SimulatorConfig(
            num_messages=100,
            num_senders=3,
            sender_settings=[
                SenderSettings(mean_delay=0.2, fail_rate=0.1),
                SenderSettings(mean_delay=0.5, fail_rate=0.4)
            ],
            monitor_update_interval=1.1
        ), None),
        (["-a"], None, SystemExit),
        (["-m"], None, SystemExit),
        (["-m", "abc"], None, SystemExit),
        (["-s", "1,1,1"], None, SystemExit)
    ]

    for args, expected_config, expected_exit in cases:
        if expected_exit is not None:
            with pytest.raises(expected_exit):
                config = process_arguments(args)
        else:
            print(args)
            config = process_arguments(args)
            assert config == expected_config

def test_launch_monitor():
    import multiprocessing
    import subprocess
    import httpx

    api_proc, monitor_proc = launch_monitor(SimulatorConfig())
    time.sleep(0.2)
    passed = False

    try:
        assert type(api_proc) == multiprocessing.Process
        assert type(monitor_proc) == subprocess.Popen
        assert api_proc.is_alive()

        interval_res = httpx.get("http://localhost:8000/interval")
        
        assert interval_res.status_code == 200
        assert json.loads(interval_res.content)["interval"] == 1

        passed = True
    except AssertionError as e:
        err = e
    finally:
        monitor_proc.kill()
        api_proc.kill()
        if not passed:
            raise err
        