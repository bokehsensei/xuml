from unittest import TestCase
from xuml.state import StateMachine
from xuml.thread_runner import ThreadManagedState

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
        with ThreadManagedState():
            a = A()
            a.send('pong')
            a.send('ping')
            a.send('pong')
        test.assertEqual(a.time, expected_time)

    def test_three(test):
        class A(StateMachine):
            event_transitions = {
                'switch_on':    {
                    'off':  'on',
                },
                'switch_off': {
                    'on':   'off',
                }
            }

            def __init__(self):
                super().__init__('off')
                self.b = None
                self.c = None
                self.counter = 0
                self.limit = 10000

            def init(self, b, c):
                self.b = b
                self.c = c

            def on(self):
                self.counter += 1
                if self.counter < self.limit:
                    self.b.send('on')

            def off(self):
                self.counter += 1
                if self.counter < self.limit:
                    self.c.send('off')

        class B(StateMachine):
            event_transitions = {
                'on': { 'switch_off': 'switch_off' }
            }

            def __init__(self, a):
                self.a = a
                super().__init__('switch_off')

            def switch_off(self):
                self.a.send('switch_off')

        class C(StateMachine):
            event_transitions = {
                'off': { 'switch_on': 'switch_on' }
            }

            def __init__(self, a):
                self.a = a
                super().__init__('switch_on')

            def switch_on(self):
                self.a.send('switch_on')

        with ThreadManagedState():
            a = A()
            b = B(a)
            c = C(a)
            a.init(b,c)

            a.send('switch_on')

        test.assertEqual(a.counter, 10000)
