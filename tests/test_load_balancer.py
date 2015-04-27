from unittest import TestCase, skip

from xuml.state import StateMachine
from xuml.load_balancer import LoadBalancer
from xuml.synchronous.machines import SynchronousMachines
from xuml.local_proxy import LocalProxy

class A(StateMachine):
    event_transitions = {
        'on':   { 'Off':    'On' },
        'off':  { 'On':     'Off' }
    }

    def __init__(self):
        super().__init__('Off')

    def On(self): pass

    def Off(self): pass

class TestLoadBalancer(TestCase):

    def test_load_balancer(self):
        machines = SynchronousMachines()
        lb = LoadBalancer(machines)
        self.assertEqual(lb.current_state, 'under_capacity')

        client = LocalProxy(lb, A)

        client.internal.run()
        self.assertEqual(client.internal.current_state, 'allocating')
        lb.run()
        self.assertEqual(lb.current_state, 'under_capacity')
        import pdb; pdb.set_trace()
