from threading import Thread, Event

class MachinePool(object):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        self.thread = Thread(name='MachinePool', target = self.run)
        self.close_event = Event()
        self.count = 0
        self.thread.start()

    def run(self):
        while not self.close_event.is_set():
            self.count+=1
            self.close_event.wait(5)

