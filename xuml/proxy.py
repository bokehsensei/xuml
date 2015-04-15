
class Proxy(Proxy):
    def __init__(self, machine):
        self.machine = machine
        self.queue = None

    def send(self, event_name, *args, **kwargs):
        self.queue.put((event_name, args, kwargs))
