from multiprocessing import Queue

from xuml.proxy import Proxy

class ProcessProxy(Proxy):
    def __init__(self, machine):
        super().__init__(machine)
        self.queue = Queue()
