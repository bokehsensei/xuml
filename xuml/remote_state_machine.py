from .state import StateMachine, StateMachineInterface
from multiprocessing import Queue

class ProxyInternalState(StateMachine):
    event_transitions = {
        'error': { 
            'allocating':   'error',
        },
        'create': {
            None:           'allocating'
        },
        'successfully_allocated': {
            'allocating':   'created',
        }
    }

    def __init__(self, proxy, load_balancer):
        self.proxy = proxy
        self.load_balancer = load_balancer
        self.queue = Queue()
        super().__init__()

    def error(self, message):
        raise Exception(message)
    
    def allocating(self, klass, args, kwargs):
        self.load_balancer.send('new', self.queue, klass, args, kwargs)

    def created(self, remote_machine_queue):
        self.proxy.remote_machine_queue = remote_machine_queue
        self.proxy.remote_machine_queue.put(self.proxy.locals_events)
        del self.proxy.local_events
        self.proxy.send = self.proxy.forward_events

class Proxy(StateMachineInterface):
    def __init__(self, load_balancer, klass, *args, **kwargs):
        self.event_transitions = klass.event_transitions
        self.load_balancer = load_balancer
        self.local_events = []
        self.remote_machine_queue = None
        self.internal = ProxyInternalState(self, load_balancer)
        self.internal.send('create', klass, *args, **kwargs)

    def enqueue_local_events(self, event, *args, **kwargs):
        self.local_events.append((event, args, kwargs))

    def forward_events(self, event, *args, **kwargs):
        self.remote_machine_queue.put((event, args, kwargs))

    send = enqueue_local_events


class LoadBalancer:
    def __init__(self):
        pass

    def new(klass, *args, **kwargs):
        # TODO: validate that args, kwargs are pickleable
        return Proxy(klass, args, kwargs)

