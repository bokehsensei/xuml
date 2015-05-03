from unittest import TestCase
from multiprocessing import active_children

from xuml.thread_pool import ThreadPool

class TestThreadPool(TestCase):

    def test_basic(self):
        process = ThreadPool()
        self.assertEqual(len(active_children()), 1)
        process.stop()
        self.assertFalse(active_children())

