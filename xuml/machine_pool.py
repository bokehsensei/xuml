import threading
from queue import Queue, Empty
from collections import namedtuple

from xuml.synchronous.machines import SynchronousMachines
from xuml.state_machine_interface import StateMachineInterface
from xuml.load_balancer import LoadBalancer
from xuml.event import Event

Id = namedtuple('Id', ['machine_pool', 'thread_pool_id'])

class MachinePool(SynchronousMachines):
    def __init__(self, thread_pool=None):
        self.id = Id(id(self), getattr(thread_pool, 'id', None))
        self.queue = Queue()
        self.stop_event = threading.Event()
        self.load_balancer = None
        self.thread_pool = thread_pool

    def __str__(self):
        return 'MachinePool({})'.format(self.id)

    def create_load_balancer(self, thread_pool_load_balancer_id):
        self.load_balancer = self.allocate(LoadBalancer, self, thread_pool_load_balancer_id)

    def allocate(self, klass, *args, **kwargs):
        kwargs['pool'] = self
        machine = klass(*args, **kwargs)
        self[machine.id] = machine
        return machine

    def run(self, block=True):
        while True:
            try:
                event = self.queue.get(block)
                self.queue.task_done()
            except Empty as e:
                break
            if event:
                if isinstance(event, list):
                    for evt in event:
                        if evt.destination not in self:
                            raise ValueError('This event was sent to the wrong address: {}'.format(evt))
                        self[evt.destination].queues.external.append((evt.event_name, evt.args, evt.kwargs))
                elif isinstance(event, tuple):
                    if event.destination in self:
                        self[event.destination].queues.external.append((event.event_name, event.args, event.kwargs))
                    else:
                        raise ValueError('This event was sent to the wrong address: {}'.format(event))
                else:
                    raise ValueError('Invalid event type for {}'.format(event))
                self.process_all_events()
            if block and self.stop_event.is_set():
                break

    def run_once(self):
        self.stop_event.set()
        self.run()

    def flush_all_events(self):
        self.run(False)

    def new(self, klass,  *args, **kwargs):
        if self.load_balancer:
            self.queue.put(Event(self.id, self.load_balancer.id, 'new', [klass]+[arg for arg in args], kwargs))
        else:
            self.allocate(klass, *args, **kwargs)

    def _enter(self):
        self.stop_event.clear()
        self.thread = threading.Thread(name=str(self), target = self.run)

    def start(self):
        self._enter()
        self.thread.start()

    def __enter__(self):
        self.start()
        return self

    def _exit(self):
        self.stop_event.set()
        self.queue.put(None)

    def stop(self):
        self._exit()
        self.thread.join()
        self.flush_all_events() # there may still be events queued at this point

    def __exit__(self, exc_type, exc, exc_tb):
        self.stop()
