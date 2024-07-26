import random
import string
from typing import Optional

from msg_queue.msg_queue import Message, MessageQueue

MAX_STRING_LEN = 100
MIN_STRING_LEN = 1
PHONE_LEN = 10

class Generator():

    def __init__(
            self, 
            queue: Optional[MessageQueue] = None, 
            num_messages: Optional[int] = 1000):
        self.num_messages = num_messages
        self.queue = queue
    
    @property
    def num_messages(self):
        return self._num_messages

    @num_messages.setter
    def num_messages(self, value: int):
        if value < 0:
            raise ValueError("Number of messages must be non-negative!")
        self._num_messages = value

    def create_random_string(self) -> str:
        string_len = random.randint(MIN_STRING_LEN, MAX_STRING_LEN)
        return "".join([random.choice(string.printable) for _ in range(string_len)])

    def create_random_phone_number(self) -> str:
        return "".join([random.choice(string.digits) for _ in range(PHONE_LEN)])

    def generate_message(self) -> Message:
        return Message(
            message=self.create_random_string(),
            phone=self.create_random_phone_number()
        )

    def start_generating(self):
        for _ in range(self.num_messages):
            self.push_message(self.generate_message())
    
    def push_message(self, message: Message):
        if self.queue:
            self.queue.push(message)
        else:
            print("No Message Queue Available!")
