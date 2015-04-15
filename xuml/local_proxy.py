from xuml.state import StateMachineInterface
from xuml.local_proxy_internal_state import LocalProxyInternalState

class LocalProxy(StateMachineInterface):
    def __init__(self, load_balancer, klass, *args, **kwargs):
        self.event_transitions = klass.event_transitions
        self.load_balancer = load_balancer
        self.local_events = []
        self.remote_proxy = None
        self.internal = LocalProxyInternalState(self, load_balancer)
        self.internal.send('create', klass, *args, **kwargs)

    def enqueue_local_events(self, event, *args, **kwargs):
        self.local_events.append((event, args, kwargs))

    send = enqueue_local_events
