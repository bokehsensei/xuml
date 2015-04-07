from concurrent.futures import ThreadPoolExecutor, wait, Future
from queue import Queue
from os import cpu_count

from .queues import Queues
from .state import StateMachine
from .managed_state import ManagedState
from .machines import Machines


class ThreadSafeQueues(Queues):
    '''
        A Queues objet provides a tuple of event queues for a given state machine:
        one external and one internal.
        Internal events must always be dispatched first.
        So the internal events queue must be empty before a given external event is processed.
    '''

    def __init__(self):
        self.external = Queue()
        self.internal = []

    def has_events(self):
        return any([not self.external.empty(), self.internal])

    def add_external_event(self, event):
        '''
        Saves the event for later processing.
        This is meant to be overloaded by a child class to provide a specific queue implementation.
        For instance, a thread-safe queue could be used by a multithreaded state machine implementation.
        '''
        self.external.put(event)

    def add_internal_event(self, event):
        '''
        Saves the internal event for later processing.
        This is meant to be overloaded by a child class to provide a specific queue implementation.
        For instance, a thread-safe queue could be used by a multithreaded state machine implementation.
        '''
        self.internal.append(event)

    def get_event(self):
        if self.internal:
            return self.internal.pop(0)
        if not self.external.empty():
            return self.external.get()
        raise Exception('no more events')

class ThreadMachines(Machines):
    def __init__(self, max_workers=10):
        self.max_workers = max_workers

    def process_all_events(self):
        with ThreadPoolExecutor(self.max_workers) as executor:
            while True:
                have_events = set(filter(lambda machine: machine.queues.has_events(), self))
                if have_events:
                    set(executor.map(StateMachine.run, have_events)) # set is needed to eagerly wait for the run returns
                else:
                    break

class ThreadManagedState(ManagedState):
    def __init__(self, name='', max_workers=cpu_count()):
        self.name = name
        self.machines = ThreadMachines(max_workers)
        self.queues_type = ThreadSafeQueues
