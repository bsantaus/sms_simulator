import random
import time
import httpx
import json
from typing import Optional

from msg_queue.msg_queue import Message, MessageQueue

def _check_range(val, min, max) -> bool:
    return val >= min and val <= max

class MonitorService():
    '''
        Serves as the interface between Senders and the 
        Monitor backend API.
    '''

    def __init__(
            self,
            url: str = None
    ):
        '''
            Validates Monitor API URL if provided
        '''
        if url:
            attempts = 3
            while attempts > 0:
                attempts -= 1
                try:
                    chk = httpx.get(url)
                    if chk.status_code == 200:
                        self.url = url
                        return
                except Exception as e:
                    time.sleep(1)
            raise Exception("Monitor API not available!")
        else:
            self.url = None    

    def report_message(self, message: Message, result: bool, delay: float):
        '''
            Updates Monitor API with recently processed message result
            and delay
        '''
        if self.url:
            res = httpx.post(self.url + "/message", json={
                "message": message.message,
                "phone": message.phone,
                "success": result,
                "delay": delay
            })

            if res.status_code != 200:
                raise Exception(f"Error reporting to Monitor API: {json.loads(res.content)}")

class Sender():
    '''
        Represents an individual message Sender 
        with specified configuration values for 
        failure rate and mean delay
    '''

    def __init__(
        self,
        queue: Optional[MessageQueue] = None,
        mean_delay: Optional[float] = 1,
        fail_rate: Optional[float] = 0.1,
        monitor_url: Optional[str] = None,
    ):
        '''
            Validates configuration for delay and failure rate,
            then sets up MonitorService for reporting.
        '''
        self._validate_config(mean_delay, fail_rate)
        self.mean_delay = mean_delay
        self.fail_rate = fail_rate
        self.finish_consuming = False # used to tell Sender to stop checking Queue
        self.queue = queue

        self.monitor = MonitorService(monitor_url)

    def _validate_config(self, mean_delay: float, fail_rate: float):
        '''
            Validate delay and fail rate values are in appropriate ranges.
        '''

        if mean_delay < 0:
            raise ValueError("Mean delay must be >= 0!")
        
        if not _check_range(fail_rate, 0, 1):
            raise ValueError("Fail Rate must be in range [0,1]")
        
    def _validate_message(self, msg: Message):
        '''
            Validate message is valid and sendable.
        '''

        if not _check_range(len(msg.message), 1, 100):
            raise ValueError("Message length must be in range [0,100])!")
        
        if not len(msg.phone) == 10:
            raise ValueError("Phone number must contain 10 digits!")

    def send_message(
        self,
        msg: Message
    ) -> bool:
        '''
            Wait for a random number of seconds in range, 
            then determine if message is sent or failed.
        '''
        self._validate_message(msg)
        
        delay = random.uniform(0, 2 * self.mean_delay)
        time.sleep(delay)
        result = not (random.random() <= self.fail_rate)

        return result, delay
    
    def pull_message(self) -> Message | None:
        '''
            Retrieve Message from MessageQueue if one 
            is available
        '''
        if self.queue:
            return self.queue.pull()
        else:
            print("No Message Queue Available!")
    
    def report_result(self, message: Message, result: bool, delay: float):
        '''
            Report message result to Monitor
        '''
        self.monitor.report_message(message, result, delay)

    def consume_messages(self):
        '''
            Until told to stop, pull and send 
            messages from MessageQueue.

            Report results to Monitor API as they happen.
        '''

        while not self.finish_consuming:
            message = self.pull_message()

            if message:
                result, delay = self.send_message(message)
                self.report_result(message, result, delay)
            else:
                time.sleep(self.mean_delay)