from unittest import TestCase, skip
from threading import active_count, enumerate, Event

from xuml.machine_pool import MachinePool
from xuml.state import StateMachine
from xuml.proxy import proxy

class Z(StateMachine):
    event_transitions = {
        'press': { 'buzz': 'buzz' }
    }

    def __init__(self, pool=None):
        super().__init__(pool, 'buzz')
        self.timeline = []
        self.new(X, self.id)

    def buzz(self):
        self.timeline.append('B')

class X(StateMachine):
    event_transitions = {
        'foo': { 'bar': 'bar' }
    }

    def __init__(self, z_id, pool=None):
        super().__init__(pool, 'bar')

        z = proxy(self, z_id)
        z.send('press')

    def bar(self): pass


class TestProxy(TestCase):

    def test_proxy(self):
        with MachinePool() as pool:
            pool.new(Z) # Z will create X

        self.assertEqual(len(pool), 2) # Z + X
