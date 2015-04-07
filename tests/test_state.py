from unittest import TestCase
from xuml.state import StateMachine
from xuml.synchronous.managed_state import SynchronousManagedState

class TestState(TestCase):

    def test_basic(test):
        class A(StateMachine):

            event_transitions = {
                'ping': { 'foo': 'bar'},
                'pong': { 'bar': 'foo'}
            }
            
            def __init__(self):
                self.time = []
                super().__init__('bar')

            def set_state(self, old_state, new_state):
                self.time.append((old_state, new_state))

            def foo(self):
                pass

            def bar(self):
                pass


        expected_time = [('bar', 'foo'), ('foo', 'bar'), ('bar', 'foo')]
        with SynchronousManagedState() as global_state:
            a = global_state.new(A)
            a.send('pong')
            a.send('ping')
            a.send('pong')
        test.assertEqual(a.time, expected_time)
