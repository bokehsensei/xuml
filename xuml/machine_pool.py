from threading import Thread, Event
from copy import copy

from xuml.synchronous.machines import SynchronousMachines
from xuml.state import StateMachine
from xuml.synchronous.managed_state import SynchronousManagedState
from xuml.local_proxy import LocalProxy
from xuml.load_balancer import LoadBalancer

class MachinePool(SynchronousMachines):
    def __init__(self, thread_pool=None):
        self.thread_pool = thread_pool
        self.load_balancer = LoadBalancer(self)
        self.add(self.load_balancer)
        self.thread = Thread(name='MachinePool', target = self.run)
        self.close_event = Event()

    def run(self):
        while not self.close_event.is_set():
            self.process_all_events()
            self.close_event.wait()
        self.process_all_events() # bug!

    def new(self, klass, *args, **kwargs):
        return LocalProxy(self.load_balancer, klass, *args, **kwargs)

    def __enter__(self):
        StateMachine.machines = self
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        print('about to set close_event')
        self.close_event.set()
        print('close_event is set')
        self.thread.join()
        print('thread is joined')
