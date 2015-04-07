from .exceptions import AbstractQueuesError

class Queues(object):
    '''
        Abstract base class Queues provides a tuple of event queues for a given state machine:
        one external and one internal.
        This class is meant to be overloaded by a child class to provide a specific queue implementation.
        Internal events must always be dispatched first.
        So the internal events queue must be empty before a given external event is processed.
    '''

    def has_events(self):
        raise AbstractQueuesError()

    def add_external_event(self, event):
        '''
        Saves an external event for later processing.
        '''
        raise AbstractQueuesError()

    def add_internal_event(self, event):
        '''
        Saves an internal event for later processing.
        '''
        raise AbstractQueuesError()

    def get_event(self):
        '''
        Return the next event to be processed.
        Internal events must be processed first, in FIFO order.
        Once internal events have been exhausted, external event can be returned, also in FIFO order.

        if both the external and internal queues are empty, return None
        '''
        raise AbstractQueuesError()
