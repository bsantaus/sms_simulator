import pytest
from unittest.mock import MagicMock

import time
import threading

from sender.sender import Sender
from msg_queue.msg_queue import Message


@pytest.fixture
def default_sender():
    return Sender()

def test_invalid_sender_config():

    # fail rate cannot be negative
    with pytest.raises(ValueError):
        sdr = Sender(fail_rate=-1)
    # fail rate cannot be greater than 1
    with pytest.raises(ValueError):
        sdr = Sender(fail_rate=2)
    
    # delay cannot be negative
    with pytest.raises(ValueError):
        sdr = Sender(mean_delay=-1)

def test_send_message_instant():

    sdr = Sender(mean_delay=0, fail_rate=0)

    start = time.time()

    success, delay = sdr.send_message(
        msg=Message(message="not random", phone="5555555555"),
    )

    assert round(time.time() - start) == 0
    assert type(success) == bool
    assert success == True
    assert delay == 0


def test_send_message_delays():

    sdr = Sender(mean_delay=0.05, fail_rate=0)

    start = time.time()

    for _ in range(20):
        _ = sdr.send_message(msg=Message(message="not random", phone="5555555555"))
    
    # on average, messages take 0.05s to process, allow for some variance
    assert time.time() - start > 0.5 and time.time() - start < 1.5

def test_send_message_results():
    test_rates = [(0, 100, 100), (0.2, 70, 90), (0.5, 35, 65), (0.8, 10, 30), (1, 0, 0)]

    for rate, low_bound, high_bound in test_rates:
        successes = 0

        sdr = Sender(mean_delay=0, fail_rate=rate)

        for _ in range(100):
            success, _ = sdr.send_message(
                msg=Message(message="not random", phone="5555555555")
            )
            successes += 1 if success else 0

        assert successes >= low_bound
        assert successes <= high_bound
    
def test_send_invalid_message(default_sender):

    phone_short_msg = Message(message="fake message", phone="12345")
    phone_long_msg = Message(message="fake message", phone="123456789AB")

    with pytest.raises(ValueError):
        _ = default_sender.send_message(phone_short_msg)

    with pytest.raises(ValueError):
        _ = default_sender.send_message(phone_long_msg)

    
    text_short_msg = Message(message="", phone="1234567890")
    text_long_msg = Message(message=["a" for _ in range(101)], phone="1234567890")

    with pytest.raises(ValueError):
        _ = default_sender.send_message(text_short_msg)

    with pytest.raises(ValueError):
        _ = default_sender.send_message(text_long_msg)

def test_consume_messages():

    delay = 0.05
    fail_rate = 0.1
    duration = 2

    total_messages_mean = duration / delay
    total_messages_low = total_messages_mean * 0.75
    total_messages_high= total_messages_mean * 1.25

    sdr = Sender(mean_delay=delay, fail_rate=fail_rate)

    sdr.pull_message = MagicMock(return_value=Message(message="valid message", phone="1234567890"))
    sdr.report_result = MagicMock()

    consume_thread = threading.Thread(target=sdr.consume_messages)

    consume_thread.start()

    time.sleep(duration)

    sdr.finish_consuming = True

    consume_thread.join()

    messages_pulled = sdr.pull_message.call_count

    assert messages_pulled >= total_messages_low
    assert messages_pulled <= total_messages_high

    assert sdr.report_result.call_count == messages_pulled

    expected_successes_low = messages_pulled * 0.75
    expected_successes_high = messages_pulled * 1.25

    print(sdr.report_result.call_count)

    results = sdr.report_result.call_args_list
    successes = sum([1 if r[0][0] == True else 0 for r in results])

    assert successes >= expected_successes_low
    assert successes <= expected_successes_high
    

