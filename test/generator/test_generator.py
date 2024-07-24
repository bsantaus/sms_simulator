import pytest
from generator.generator import *

MAX_STRING_LEN = 100
MIN_STRING_LEN = 1
PHONE_LEN = 10

def test_create_random_string():
    rand_string = create_random_string()

    assert type(rand_string) == str
    assert len(rand_string) >= MIN_STRING_LEN and len(rand_string) <= MAX_STRING_LEN

    rand_string_1 = create_random_string()
    assert len(rand_string) >= MIN_STRING_LEN and len(rand_string) <= MAX_STRING_LEN

    assert rand_string != rand_string_1
    assert len(rand_string) != len(rand_string_1)

    # check sequence of characters being generated is not the same even if lengths are different
    assert rand_string[:len(rand_string_1)] != rand_string_1[:len(rand_string)]

def test_create_random_phone_number():

    # will not be checking that phone numbers are _valid_ 
    # but will check that they're a correct length
    # (assuming all numbers are in US)

    rand_phone = create_random_phone_number()

    assert type(rand_phone) == str
    assert len(rand_phone) == PHONE_LEN

    rand_phone_1 = create_random_phone_number()
    assert len(rand_phone_1) == PHONE_LEN

    assert rand_phone != rand_phone_1

def test_generate_message():

    message = generate_message()

    assert type(message) == Message

    assert type(message.message) == str
    assert len(message.message) >= MIN_STRING_LEN and len(message.message) <= MAX_STRING_LEN

    assert type(message.phone) == str
    assert len(message.phone) == PHONE_LEN
