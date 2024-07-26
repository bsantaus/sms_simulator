import random
import time
from typing import Optional

from msg_queue.msg_queue import Message, MessageQueue

def _check_range(val, min, max) -> bool:
    return val >= min and val <= max
class Sender():

    def __init__(
        self,
        queue: Optional[MessageQueue] = None,
        mean_delay: Optional[float] = 1,
        fail_rate: Optional[float] = 0.1
    ):
        self._validate_config(mean_delay, fail_rate)
        self.mean_delay = mean_delay
        self.fail_rate = fail_rate
        self.finish_consuming = False
        self.queue = queue

    def _validate_config(self, mean_delay: float, fail_rate: float):

        if mean_delay < 0:
            raise ValueError("Mean delay must be >= 0!")
        
        if not _check_range(fail_rate, 0, 1):
            raise ValueError("Fail Rate must be in range [0,1]")
        
    def _validate_message(self, msg: Message):
        if not _check_range(len(msg.message), 1, 100):
            raise ValueError("Message length must be in range [0,100])!")
        
        if not len(msg.phone) == 10:
            raise ValueError("Phone number must contain 10 digits!")

    def send_message(
        self,
        msg: Message
    ) -> bool:
        self._validate_message(msg)
        
        delay = random.uniform(0, 2 * self.mean_delay)
        time.sleep(delay)

        return not (random.random() <= self.fail_rate)
    
    def pull_message(self) -> Message | None:
        if self.queue:
            return self.queue.pull()
        else:
            print("No Message Queue Available!")
    
    def report_result(self, result):
        pass

    def consume_messages(self):
        while not self.finish_consuming:
            result = self.send_message(self.pull_message())
            self.report_result(result)
