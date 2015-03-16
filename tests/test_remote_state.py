from unittest import TestCase, skip
from xuml.state import ManagedState
#from xuml.remote_state_machine import RemoteStateMachine

class TestState(TestCase):

    @skip('not ready')
    def test_basic(test):
        class A(StateMachine):
            def __init__(self):
                self.time = []
                transitions = {
                    'ping': { 'foo': 'bar'},
                    'pong': { 'bar': 'foo'}
                }
                super().__init__(transitions, 'bar')

            def set_state(self, old_state, new_state):
                self.time.append((old_state, new_state))

            def foo(self):
                pass

            def bar(self):
                pass


        load_balancer = LoadBalancer()
        a = load_balancer.new(A)
        expected_time = [('bar', 'foo'), ('foo', 'bar'), ('bar', 'foo')]
        with ManagedState():
            a.send('pong')
            a.send('ping')
            a.send('pong')
            test.assertEqual(a.time, expected_time)
            a.current_state = 'bar'
            a.time.clear()
