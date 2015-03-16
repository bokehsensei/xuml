from concurrent.futures import ProcessPoolExecutor, wait, Future
import copy
from .state import StateMachine, ManagedState, Machines

class ProcessMachines(Machines):
    def __init__(self, max_workers=10):
        self.max_workers = max_workers

    def process_all_events(self):
        with ProcessPoolExecutor(self.max_workers) as executor:
            while True:
                have_events = set(filter(StateMachine.has_events, self))
                if have_events:
                    set(executor.map(StateMachine.run, have_events)) # set is needed to eagerly wait for the run returns
                else:
                    break

class ProcessManagedState(ManagedState):
    def __init__(self, name='', max_workers=10):
        self.name = name
        self.pool = ProcessMachines(max_workers)
