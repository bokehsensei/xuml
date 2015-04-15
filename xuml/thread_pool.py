from multiprocessing import Pipe, Process
from .machine_pool import MachinePool
from .state import StateMachine

class ThreadPool(StateMachine):
    '''
    ThreadPool is the equivalent of an OS process.
    It is a collection of MachinePool objects.
    '''
    event_transitions = {
        'available':   {
            'under_capacity': 'under_capacity'
        }
    }

    def __init__(self):
        self.pipe, pool_pipe = Pipe()
        self.machine_pools = []
        self.process = Process(target=self.run, args=(pool_pipe,))
        self.process.start()
        print('Started {}.'.format(self.process.name))

    def under_capacity(self):
        pass

    def run(self, pipe):
        self.machine_pools.append(MachinePool(self))
        anything = pipe.recv()
        for pool in self.machine_pools:
            pool.close_event.set()
            pool.thread.join()
