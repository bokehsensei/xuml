from multiprocessing import Pipe, Process, cpu_count
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

    def stop(self):
        self.pipe.send('')
        self.process.join()

    def run(self, pipe):
        # launch all the threads
        for i in range(cpu_count()):
            pool = MachinePool(self)
            self.machine_pools[pool._id] = pool
            pool.__enter__()

        _ = pipe.recv() # wait for any data to arrive to signal STOP

        # join all the threads
        for pool in self.machine_pools.values():
            pool.__exit__(None, None, None)
