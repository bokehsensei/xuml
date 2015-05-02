from unittest import TestCase, skip

from xuml.state import StateMachine
from xuml.machine_pool import MachinePool

class A(StateMachine):
    event_transitions = {
        'create':   {
            None:   'Off'
        },
        'on':   {
            'Off':    'On'
        },
        'off':  {
            'On':     'Off'
        }
    }

    def __init__(self):
        super().__init__('Off')

    def On(self): pass

    def Off(self): pass

class TestLoadBalancer(TestCase):

    def test_load_balancer(self):
        machine_pool = MachinePool()
        lb = machine_pool.load_balancer
        self.assertEqual(len(machine_pool.keys()), 1)
        self.assertEqual(lb.current_state, 'under_capacity')
        lb.send('new', A)
        lb.send('new', A)
        lb.send('new', A)
        lb.run()
        self.assertEqual(lb.current_state, 'under_capacity')
        self.assertEqual(len(machine_pool.keys()), 4)
