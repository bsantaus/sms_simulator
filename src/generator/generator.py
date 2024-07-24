import random
import string

from dataclasses import dataclass

@dataclass
class Message():
    message: str
    phone: str

def create_random_string():
    string_len = random.randint(1, 100)
    return "".join([random.choice(string.printable) for _ in range(string_len)])

def create_random_phone_number():
    return "".join([random.choice(string.digits) for _ in range(10)])

def generate_message():
    return Message(
        message=create_random_string(),
        phone=create_random_phone_number()
    )

