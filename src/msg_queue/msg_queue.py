from dataclasses import dataclass
from threading import Lock

@dataclass
class Message():
    message: str
    phone: str

class MessageQueue:
    '''
        Class representing Message Queue where
        Generator provides Messages and Senders retrieve
        them for processing.

        Made a component with the intention that it could 
        potentially be adapted to work with RabbitMQ or 
        similar message queueing tool if the simulation 
        needed to scale out.
    '''

    def __init__(self):
        '''
            Create queue and lock for avoiding 
            concurrency errors
        '''
        self._queue = []
        self.q_lock = Lock()

    def length(self) -> int:
        '''
            Return current length of queue
        '''
        return len(self._queue)
    
    def push(self, msg: Message):
        '''
            Add a message to the queue
        '''

        if type(msg) != Message or msg == None:
            raise ValueError("Message pushed to queue is not of type `Message`")
        
        with self.q_lock:
            self._queue.append(msg)

    def pull(self) -> Message | None:
        '''
            If available, retrieve a message from queue.
        '''
        with self.q_lock:
            if self.length() > 0:
                return self._queue.pop(0)
        return None
