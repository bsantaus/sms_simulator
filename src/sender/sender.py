import random
import time
from typing import Optional

from common.message import Message

def _check_range(val, min, max):
    return val >= min and val <= max

def _validate_inputs(msg, mean_delay, fail_rate):
    if not _check_range(len(msg.message), 1, 100):
        raise ValueError("Message length must be in range [0,100])!")
    
    if not len(msg.phone) == 10:
        raise ValueError("Phone number must contain 10 digits!")

    if mean_delay < 0:
        raise ValueError("Mean delay must be >= 0!")
    
    if not _check_range(fail_rate, 0, 1):
        raise ValueError("Fail Rate must be in range [0,1]")

def send_message(
    msg: Message,
    mean_delay: Optional[float] = 1,
    fail_rate: Optional[float] = 0.1
):
    _validate_inputs(msg, mean_delay, fail_rate)
    
    delay = random.uniform(0, 2 * mean_delay)
    time.sleep(delay)

    return not (random.random() <= fail_rate)
