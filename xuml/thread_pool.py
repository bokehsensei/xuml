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
        self.machine_pools = dict()
        self.process = Process(target=self.run, args=(pool_pipe,))
        self._id = id(self)
        self.process.start()
        print('Started {}.'.format(self.process.name))

    def under_capacity(self):
        pass

    def run(self, pipe):
        one_pool = MachinePool(self)
        self.machine_pools[one_pool._id] = one_pool
        _ = pipe.recv()
        for pool in self.machine_pools:
            pool.close_event.set()
            pool.thread.join()
