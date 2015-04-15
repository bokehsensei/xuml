from unittest import TestCase
from threading import active_count, enumerate

from xuml.machine_pool import MachinePool
from xuml.state import StateMachine

class TestMachinePool(TestCase):

    def setUp(self):
        class Foo(StateMachine):
            event_transitions = {
                'ping': { 'pong': 'pong' }
            }

            def __init__(self): super().__init__('pong')

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

    def test_as_context_manager(self):
        with MachinePool() as mp:
            threads = enumerate()
            self.assertEqual(threads[1].name, 'MachinePool')
            self.assertEqual(2, active_count())
            machine = mp.new(self.Foo)
            machine.send('ping')
        self.assertEqual(1, active_count())
