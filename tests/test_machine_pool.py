from unittest import TestCase, skip
from threading import active_count, enumerate

from xuml.machine_pool import MachinePool
from xuml.state import StateMachine

class TestMachinePool(TestCase):

    def setUp(self):
        class Foo(StateMachine):
            event_transitions = {
                'ping': { 'pong': 'ping' },
                'pong': { 'ping': 'pong' }
            }

            def __init__(self):
                self.time = []
                super().__init__('pong')

            def set_state(self, old, new):
                self.time += (old, new)

            def ping(self): pass
            def pong(self): pass

        self.Foo = Foo

    def test_basic(self):
        m = MachinePool()
        m.thread.start()
        self.assertEqual(2, active_count())
        threads = enumerate()
        self.assertEqual(threads[1].name, 'MachinePool')
        m.close_event.set()
        m.thread.join()
        self.assertEqual(1, active_count())

    @skip('too many things not working yet...')
    def test_as_context_manager(self):
        with MachinePool() as mp:
            threads = enumerate()
            self.assertEqual(threads[1].name, 'MachinePool')
            self.assertEqual(2, active_count())
            machine = mp.new(self.Foo)
            self.assertEqual(2, len(mp)) # LoadBalancer + Foo
            machine.send('ping')
            machine.send('pong')
            machine.send('ping')
            machine.send('pong')
        self.assertEqual(1, active_count())
        self.assertEqual(
            machine.time,
            [
                ('pong', 'ping'),
                ('ping', 'pong'),
                ('pong', 'ping'),
                ('ping', 'pong')
            ]
        )
