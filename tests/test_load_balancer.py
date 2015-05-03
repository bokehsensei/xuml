from unittest import TestCase

from xuml.state import StateMachine
from xuml.machine_pool import MachinePool

class B(StateMachine): pass

class TestLoadBalancer(TestCase):

    def test_load_balancer(self):
        pool = MachinePool()
        pool._enter()
        lb = pool.load_balancer
        self.assertEqual(len(pool), 1)
        self.assertEqual(lb.current_state, 'under_capacity')
        new_B = ('new', B)
        lb.send(*new_B)
        lb.send_many([new_B for i in range(100)])
        lb.run()
        self.assertEqual(lb.current_state, 'under_capacity')
        self.assertEqual(len(pool), 102)
