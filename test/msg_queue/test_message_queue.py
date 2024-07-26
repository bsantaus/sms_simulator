import pytest

import threading
import time
import random

from msg_queue.msg_queue import Message, MessageQueue

@pytest.fixture
def queue():
    return MessageQueue()

def test_push_message(queue):

    assert queue.length() == 0

    msg = Message(message="fake message", phone="1234567890")

    queue.push(msg)

    assert queue.length() == 1

    queue.push(msg)

    assert queue.length() == 2

    for _ in range(5):
        queue.push(msg)

    assert queue.length() == 7


def test_pull_message_simple(queue):

    msg = Message(message="fake message", phone="1234567890")

    queue.push(msg)

    msg2 = Message(message="second fake", phone="2345678901")

    queue.push(msg2)

    pulled_msg = queue.pull()
    assert msg.message == pulled_msg.message
    assert msg.phone == pulled_msg.phone

    pulled_msg2 = queue.pull()
    assert msg2.message == pulled_msg2.message
    assert msg2.phone == pulled_msg2.phone

    no_msg = queue.pull()

    assert no_msg == None

def test_pull_multiple_consumers(queue):

    num_test_threads = 20
    num_test_messages = 2000

    thread_consumed_msgs = [[] for _ in range(num_test_threads)]
    threads = []

    def pull_msgs(src, dest):
        msg_pulled = src.pull()
        while msg_pulled != None:
            dest.append(msg_pulled)
            msg_pulled = src.pull()

    for i in range(num_test_messages):
        queue.push(
            Message(
                message=f"{i}",
                phone="1234567890"
            )
        )

    for i in range(num_test_threads):
        threads.append(threading.Thread(target=pull_msgs, args=(queue, thread_consumed_msgs[i])))
        threads[i].start()

    for thread in threads:
        thread.join()

    assert sum([len(tcm) for tcm in thread_consumed_msgs]) == num_test_messages

    msgs_left = [str(i) for i in list(range(num_test_messages))]

    for msg in [m for tcm in thread_consumed_msgs for m in tcm]:
        msgs_left.remove(msg.message)

    assert len(msgs_left) == 0