import threading
from queue import Queue, Empty
from collections import namedtuple

from xuml.synchronous.machines import SynchronousMachines
from xuml.state import StateMachine
from xuml.load_balancer import LoadBalancer
from xuml.event import Event

class MachinePool(SynchronousMachines):
    def __init__(self, thread_pool=None):
        Id = namedtuple('Id', ['machine_pool', 'thread_pool_id'])
        self._id = Id(id(self), getattr(thread_pool, '_id', None))
        self.thread_pool = thread_pool
        self.queue = Queue()
        self.stop = threading.Event()

    def __str__(self):
        return 'MachinePool({})'.format(self._id)

    def run(self, block=True):
        while True:
            try:
                event = self.queue.get(block)
            except Empty as e:
                break
            self.queue.task_done()
            if event:
                if isinstance(event, list):
                    for evt in event:
                        if evt.destination not in self.keys():
                            raise ValueError('This event was sent to the wrong address: {}'.format(evt))
                        self[evt.destination].queues.external.append((evt.event_name, evt.args, evt.kwargs))
                elif isinstance(event, tuple):
                    if event.destination in self.keys():
                        self[event.destination].queues.external.append((event.event_name, event.args, event.kwargs))
                    else:
                        raise ValueError('This event was sent to the wrong address: {}'.format(event))
                else:
                    raise ValueError('Invalid event type for {}'.format(event))
                self.process_all_events()
            if block and self.stop.is_set():
                break

    def run_once(self):
        self.stop.set()
        self.run()

    def flush_all_events(self):
        self.run(False)

    def new(self, klass,  *args, **kwargs):
        self.queue.put(Event(self._id, self.load_balancer._id, 'new', [klass]+[arg for arg in args], kwargs))

    def _enter(self):
        StateMachine.machines = self
        self.load_balancer = LoadBalancer(self)
        self[self.load_balancer._id] = self.load_balancer
        self.stop.clear()
        self.thread = threading.Thread(name=str(self), target = self.run)

    def __enter__(self):
        self._enter()
        self.thread.start()
        return self

    def _exit(self):
        self.stop.set()
        self.queue.put(None)

    def __exit__(self, exc_type, exc, exc_tb):
        self._exit()
        self.thread.join()
        self.flush_all_events() # there may still be events queued at this point
        del self[self.load_balancer._id]
        self.load_balancer = None
