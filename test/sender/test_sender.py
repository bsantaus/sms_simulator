import pytest
import time

from sender.sender import send_message
from common.message import Message

def test_send_message_instant():

    start = time.time()

    result = send_message(
        msg=Message(message="not random", phone="5555555555"),
        mean_delay=0,
        fail_rate=0)

    assert round(time.time()- start) == 0
    assert type(result) == bool
    assert result == True


def test_send_message_delays():

    start = time.time()

    for _ in range(20):
        _ = send_message(
            msg=Message(message="not random", phone="5555555555"),
            mean_delay=0.05,
            fail_rate=0
        )
    
    # on average, messages take 0.05s to process, allow for some variance
    assert time.time() - start > 0.5 and time.time() - start < 1.5

def test_send_message_results():


    test_rates = [(0, 100, 100), (0.2, 70, 90), (0.5, 35, 65), (0.8, 10, 30), (1, 0, 0)]

    for rate, low_bound, high_bound in test_rates:
        successes = 0

        for _ in range(100):
            successes = successes + 1 if send_message(
                msg=Message(message="not random", phone="5555555555"),
                mean_delay=0,
                fail_rate=rate
            ) else successes

        assert successes >= low_bound
        assert successes <= high_bound
    
def test_send_message_invalid_params():

    phone_short_msg = Message(message="fake message", phone="12345")
    phone_long_msg = Message(message="fake message", phone="123456789AB")

    with pytest.raises(ValueError):
        _ = send_message(phone_short_msg)

    with pytest.raises(ValueError):
        _ = send_message(phone_long_msg)

    
    text_short_msg = Message(message="", phone="1234567890")
    text_long_msg = Message(message=["a" for _ in range(101)], phone="1234567890")

    with pytest.raises(ValueError):
        _ = send_message(text_short_msg)

    with pytest.raises(ValueError):
        _ = send_message(text_long_msg)


    valid_msg = Message(message="fake message", phone="1234567890")

    # fail rate cannot be negative
    with pytest.raises(ValueError):
        _ = send_message(valid_msg, fail_rate=-1)

    # fail rate cannot be greater than 1
    with pytest.raises(ValueError):
        _ = send_message(valid_msg, fail_rate=3)
    
    # delay cannot be negative
    with pytest.raises(ValueError):
        _ = send_message(valid_msg, mean_delay=-1)
