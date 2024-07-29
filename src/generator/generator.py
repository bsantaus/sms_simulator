import random
import string
from typing import Optional

from msg_queue.msg_queue import Message, MessageQueue

MAX_STRING_LEN = 100
MIN_STRING_LEN = 1
PHONE_LEN = 10

class Generator():
    '''
        Class representing a Message Generator

        Creates Messages for Senders to send and puts them
        into a MessageQueue
    '''

    def __init__(
            self, 
            queue: Optional[MessageQueue] = None, 
            num_messages: Optional[int] = 1000
    ):
        '''
            Initialize Generator class with number of messages
            to generate and a MessageQueue in which to put them
        '''
        self.num_messages = num_messages
        self.queue = queue
    
    @property
    def num_messages(self):
        '''
            Number of messages to be sent
        '''
        return self._num_messages

    @num_messages.setter
    def num_messages(self, value: int):
        '''
            Setter for number of messages

            Use `setter` because we can do input validation
        '''
        if value < 0:
            raise ValueError("Number of messages must be non-negative!")
        self._num_messages = value

    def create_random_string(self) -> str:
        '''
            Create random string for message from printable
            characters

            Strings must be at least 1 and at most 100 characters.
        '''
        string_len = random.randint(MIN_STRING_LEN, MAX_STRING_LEN)
        return "".join([random.choice(string.printable) for _ in range(string_len)])

    def create_random_phone_number(self) -> str:
        '''
            Create random phone number for message

            Phone numbers (in the US) are 10 digits long.

            Phone number validation left out for simulation.
        '''
        return "".join([random.choice(string.digits) for _ in range(PHONE_LEN)])

    def generate_message(self) -> Message:
        '''
            Create Message with random string and random phone number
        '''
        return Message(
            message=self.create_random_string(),
            phone=self.create_random_phone_number()
        )

    def start_generating(self):
        '''
            Create Messages and push them onto the 
            MessageQueue for Senders
        '''
        for _ in range(self.num_messages):
            self.push_message(self.generate_message())
    
    def push_message(self, message: Message):
        '''
            Push message onto Queue if one is available
        '''
        if self.queue:
            self.queue.push(message)
        else:
            print("No Message Queue Available!")
