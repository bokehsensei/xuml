from ..queues import Queues

class SynchronousQueues(Queues):
    '''
        A synchronous implementation of Queues.
        It is one of the simplest implementation of Queues possible.
        Both the external and internal queues are implemented as a list.
        It provides no read/write protection from competing thread, so this implementation is not thread-safe.
        It is meant to be used with a pool of StateMachines dedicated to a single thread.
    '''

    def __init__(self):
        self.external = []
        self.internal = []

    def has_events(self):
        return any([self.external, self.internal])

    def add_external_event(self, event):
        self.external.append(event)

    def add_internal_event(self, event):
        self.internal.append(event)

    def get_event(self):
        if self.internal:
            return self.internal.pop(0)
        if self.external:
            return self.external.pop(0)
        return None

