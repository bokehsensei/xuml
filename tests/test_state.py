from unittest import TestCase
from xuml.state import StateMachine, ManagedState

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
        with ManagedState():
            a = A()
            a.send('pong')
            a.send('ping')
            a.send('pong')
        test.assertEqual(a.time, expected_time)
