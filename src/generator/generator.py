import random
import string

from dataclasses import dataclass

MAX_STRING_LEN = 100
MIN_STRING_LEN = 1
PHONE_LEN = 10

@dataclass
class Message():
    message: str
    phone: str

class Generator():

    def __init__(self, num_messages=1000):
        self.num_messages = num_messages
    
    @property
    def num_messages(self):
        return self._num_messages

    @num_messages.setter
    def num_messages(self, value):
        if value < 0:
            raise ValueError("Number of messages must be non-negative!")
        self._num_messages = value

    def create_random_string(self):
        string_len = random.randint(MIN_STRING_LEN, MAX_STRING_LEN)
        return "".join([random.choice(string.printable) for _ in range(string_len)])

    def create_random_phone_number(self):
        return "".join([random.choice(string.digits) for _ in range(PHONE_LEN)])

    def generate_message(self):
        return Message(
            message=self.create_random_string(),
            phone=self.create_random_phone_number()
        )

    def start_generating(self):
        for _ in range(self.num_messages):
            self.push_message(self.generate_message())
    
    def push_message(self, message):
        pass
