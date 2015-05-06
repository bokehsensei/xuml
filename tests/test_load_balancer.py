from unittest import TestCase

from xuml.state import StateMachine
from xuml.thread_pool import ThreadPool

class B(StateMachine): pass

class TestLoadBalancer(TestCase):

    def test_load_balancer(self):
        process = ThreadPool(1)
        self.assertTrue(process.machine_pools)
        pool_id, pool = next(enumerate(process.machine_pools.values()))
        lb = pool.load_balancer
        self.assertEqual(len(pool), 2)
        self.assertEqual(lb.current_state, 'notify_under')
        new_B = ('new', B)
        lb.send(*new_B)
        lb.send_many([new_B for i in range(100)])
        lb.run()
        self.assertEqual(lb.current_state, 'NOT_FULL')
        self.assertEqual(len(pool), 103) # 101 + 1 MachinePool lb + 1 ThreadPool lb
