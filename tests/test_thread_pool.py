from unittest import TestCase, skip
from multiprocessing import active_children, Queue
from threading import active_count, enumerate
from queue import Empty

from xuml.thread_pool import ThreadPool
from xuml.state import StateMachine

output_q = Queue()

class Boot(StateMachine):
    def __init__(self, pool=None):
        super().__init__(pool)
        self.new(A)
        self.new(A)

class A(StateMachine):
    def __init__(self, pool=None):
        super().__init__(pool)
        self.new(B)
        output_q.put('A')

class B(StateMachine):
    def __init__(self, pool=None):
        super().__init__(pool)
        output_q.put('B')


class TestThreadPool(TestCase):

    def test_basic(self):
        process = ThreadPool()
        process.start()
        self.assertEqual(len(active_children()), 1)
        process.stop()
        self.assertFalse(active_children())

    def test_as_context(self):
        results = []
        with ThreadPool(1) as process:
            self.assertEqual(len(active_children()), 1)
            process.new(Boot)
        while not output_q.empty():
            r = output_q.get()
            results.append(r)

        self.assertEqual(len(results), 4)
        self.assertFalse(active_children())

    def test_run(self):
        process = ThreadPool(19)
        process.launch_threads()
        process.new(Boot)
        event = process.queue.get()
        process.machine_pools[event.destination.machine_pool_id].queue.put(event)
        process.kill_threads()
        results = []
        while not output_q.empty():
            r = output_q.get()
            results.append(r)
        self.assertEqual(len(results), 4)
