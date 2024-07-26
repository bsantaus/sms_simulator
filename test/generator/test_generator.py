import pytest
from unittest.mock import MagicMock

from generator.generator import Generator, Message


MAX_STRING_LEN = 100
MIN_STRING_LEN = 1
PHONE_LEN = 10

@pytest.fixture
def default_gen():
    return Generator()

def test_constructor(default_gen):
    assert default_gen.num_messages == 1000

    gen_5 = Generator(5)
    assert gen_5.num_messages == 5

    gen_0 = Generator(0)
    assert gen_0.num_messages == 0

    with pytest.raises(ValueError):
        gen_minus_one = Generator(-1)       

def test_create_random_string(default_gen):
    rand_string = default_gen.create_random_string()

    assert type(rand_string) == str
    assert len(rand_string) >= MIN_STRING_LEN and len(rand_string) <= MAX_STRING_LEN

    rand_string_1 = default_gen.create_random_string()
    assert len(rand_string) >= MIN_STRING_LEN and len(rand_string) <= MAX_STRING_LEN

    assert rand_string != rand_string_1
    assert len(rand_string) != len(rand_string_1)

    # check sequence of characters being generated is not the same even if lengths are different
    assert rand_string[:len(rand_string_1)] != rand_string_1[:len(rand_string)]

def test_create_random_phone_number(default_gen):

    # will not be checking that phone numbers are _valid_ 
    # but will check that they're a correct length
    # (assuming all numbers are in US)

    rand_phone = default_gen.create_random_phone_number()

    assert type(rand_phone) == str
    assert len(rand_phone) == PHONE_LEN

    rand_phone_1 = default_gen.create_random_phone_number()
    assert len(rand_phone_1) == PHONE_LEN

    assert rand_phone != rand_phone_1

def test_generate_message(default_gen):

    message = default_gen.generate_message()

    assert type(message) == Message

    assert type(message.message) == str
    assert len(message.message) >= MIN_STRING_LEN and len(message.message) <= MAX_STRING_LEN

    assert type(message.phone) == str
    assert len(message.phone) == PHONE_LEN

def test_start_generating(default_gen):

    default_gen.push_message = MagicMock()

    default_gen.start_generating()

    assert default_gen.push_message.call_count == default_gen.num_messages
    assert type(default_gen.push_message.call_args[0][0]) == Message

    generate_10 = Generator(10)

    generate_10.push_message = MagicMock()
    generate_10.start_generating()

    assert generate_10.push_message.call_count == 10

    generate_10.push_message.reset_mock()
    generate_10.num_messages = 100

    generate_10.start_generating()
    assert generate_10.push_message.call_count == 100

    generate_0 = Generator(0)

    generate_0.push_message = MagicMock()

    generate_0.start_generating()
    assert generate_0.push_message.call_count == 0