from xuml.state import StateMachine
from xuml.process_proxy import ProcessProxy

class LocalProxyInternalState(StateMachine):
    event_transitions = {
        'error': { 
            'allocating':   'error',
        },
        'create': {
            None:           'allocating'
        },
        'allocated': {
            'allocating':   'created',
        }
    }

    def __init__(self, proxy, load_balancer):
        self.proxy = proxy
        self.load_balancer = load_balancer
        self.process_proxy = ProcessProxy(self)
        super().__init__()

    def error(self, message):
        raise Exception(message)
    
    def allocating(self, klass, *args, **kwargs):
        self.load_balancer.send('new', self.process_proxy, klass, *args, **kwargs)

    def created(self, remote_proxy):
        self.proxy.remote_proxy = remote_proxy
        self.proxy.remote_proxy.send(self.proxy.locals_events)
        del self.proxy.local_events
        self.proxy.send = self.proxy.remote_proxy.send
