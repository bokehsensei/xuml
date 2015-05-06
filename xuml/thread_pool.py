from multiprocessing import Process, cpu_count, Queue
from random import choice

from xuml.machine_pool import MachinePool
from xuml.state import StateMachine
from xuml.event import Event
from xuml.proxy import proxy

class ProcessLoadBalancer(StateMachine):
    event_transitions = {
        'available': {
            'FULL':                     'add_to_available',
            'NOT_FULL':                 'add_to_available'
        },
        'not_full': {
            'add_to_available':         'NOT_FULL',
            'allocate':                 'NOT_FULL',
            'remove_from_available':    'NOT_FULL'
        },
        'full': {
            'remove_from_available':    'FULL',
            'delegate_or_fail':         'FULL'
        },
        'not_available': {
            'FULL':                     'remove_from_available',
            'NOT_FULL':                 'remove_from_available'
        },
        'new': {
            'FULL':                     'delegate_or_fail',
            'NOT_FULL':                 'allocate'
        }
    }

    def __init__(self, pool=None):
        self.available = []
        self.not_available = []
        super().__init__(pool, 'NOT_FULL')

    def FULL(self, pool):
        pass
        #print('{} is FULL!'.format(str(self)))

    def NOT_FULL(self):
        pass
        #print('{} is NOT FULL!'.format(str(self)))

    def add_to_available(self, load_balancer_id):
        self.available.append(load_balancer_id)
        self.send_internal('not_full')

    def remove_from_available(self, load_balancer_id):
        self.available.discard(load_balancer_id)
        if self.available:
            self.send_internal('not_full')
        else:
            self.send_internal('full')

    def delegate_or_fail(self):
        self.send_internal('full')

    def allocate(self, klass, *args, **kwargs):
        machine_pool_load_balancer = proxy(self, choice(self.available))
        machine_pool_load_balancer.send('new', klass, *args, **kwargs)
        self.send_internal('not_full')


class ThreadPool(object):
    '''
    ThreadPool is the equivalent of an OS process.
    It is a collection of MachinePool objects.
    '''

    def __init__(self, num_threads=None):
        num_threads = num_threads or cpu_count()
        if num_threads < 1:
            raise ValueError('num_threads must be 1 or more')
        self.id = id(self)
        self.machine_pools = dict()
        self.load_balancer_id = None
        load_balancer = None
        for i in range(num_threads):
            pool = MachinePool(self)
            self.machine_pools[pool.id] = pool
            if i == 0:
                load_balancer = pool.allocate(ProcessLoadBalancer)
                self.load_balancer_id = load_balancer.id
            pool.create_load_balancer(self.load_balancer_id)
        self.queue = Queue()
        self.process = Process(name='ThreadPool({})'.format(self.id), target=self.run)

    def start(self):
        self.process.start()
        #print('Started {}.'.format(self.process.name))

    def stop(self):
        self.queue.put(None)
        self.process.join()
        #print('Stopped {}.'.format(self.process.name))

    def launch_threads(self):
        for pool in self.machine_pools.values():
            pool.start()

    def kill_threads(self):
        for pool in self.machine_pools.values():
            pool.stop()

    def run(self):
        self.launch_threads()
        while True:
            event = self.queue.get()
            if not event:
                break
            if event.destination.machine_pool_id not in self.machine_pools:
                raise ValueError('Invalid event: {}'.format(event))
            self.machine_pools[event.destination.machine_pool_id].queue.put(event)
        for pool in self.machine_pools.values():
            pool.queue.join()
        self.kill_threads()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.stop()

    def new(self, klass, *args, **kwargs):
        self.queue.put(Event(self.id, self.load_balancer_id, 'new', [klass]+[arg for arg in args], kwargs))
