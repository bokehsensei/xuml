from queue import Queue

class ThreadProxy(Proxy):
    def __init__(self, machine):
        self.queue = Queue()
        super().__init__(machine)
