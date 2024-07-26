from dataclasses import dataclass
from threading import Lock

@dataclass
class Message():
    message: str
    phone: str

class MessageQueue:

    def __init__(self):
        self._queue = []
        self.q_lock = Lock()

    def length(self) -> int:
        return len(self._queue)
    
    def push(self, msg: Message):

        if type(msg) != Message or msg == None:
            raise ValueError("Message pushed to queue is not of type `Message`")
        
        with self.q_lock:
            self._queue.append(msg)

    def pull(self) -> Message | None:
        with self.q_lock:
            if self.length() > 0:
                return self._queue.pop(0)
        return None
