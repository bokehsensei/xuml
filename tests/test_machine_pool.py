from unittest import TestCase, skip
from threading import active_count, enumerate
import threading

from xuml.machine_pool import MachinePool
from xuml.state import StateMachine
from xuml.event import Event

class Z(StateMachine):
    event_transitions = {
        'press': { 'buzz': 'buzz' }
    }

    def __init__(self):
        super().__init__('buzz')
        self.timeline = []

    def buzz(self):
        timeline.append('B')

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

    def test_queue(self):
        m = MachinePool()
        m._enter() # simulates entering the context, without starting the thread
        self.assertEqual(len(m), 1)
        create_a_Z_object = Event(None, m.load_balancer._id, 'new', [Z], {})
        m.queue.put(create_a_Z_object)
        m.queue.put([create_a_Z_object, create_a_Z_object, create_a_Z_object])
        m.new(Z)
        m.flush_all_events()
        self.assertEqual(len(m), 6)

    def test_new(self):
        m = MachinePool()
        m._enter() # simulates entering the context, without starting the thread
        m.new(Z)
        m.flush_all_events()
        self.assertEqual(len(m), 2)

    def test_basic(self):
        m = MachinePool()
        m.__enter__()
        self.assertEqual(2, active_count())
        threads = enumerate()
        self.assertTrue(threads[1].name.startswith('MachinePool'))
        m._exit()
        m.thread.join()
        self.assertEqual(1, active_count())

    def test_as_context_mgr(self):
        with MachinePool() as mp:
            self.assertEqual(2, active_count())
            mp.new(self.Foo)

        self.assertEqual(1, len(mp)) # Foo
        self.assertEqual(1, active_count())
        machine = next(iter(mp.values()))
        self.assertEqual(machine.current_state, 'pong')

        with mp:
            mp.new(Z)
            mp.new(self.Foo)

        self.assertEqual(len(mp), 3)
