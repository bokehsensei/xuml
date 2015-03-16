import copy
from contextlib import ContextDecorator

class Machines(set):
    def process_all_events(self):
        while any([machine.queues.has_events() for machine in self]):
            copy_self = copy.copy(self)
            for machine in copy_self:
                machine.run()

class StateMachineInterface(object):
    def send(self, event, *args, **kwargs):
        raise NotImplemented('StateMachineInterface is not directly usable')

class Queues(object):
    '''
        A Queues objet provides a tuple of event queues for a given state machine:
        one external and one internal.
        Internal events must always be dispatched first.
        So the internal events queue must be empty before a given external event is processed.
    '''

    def __init__(self):
        self.external = []
        self.internal = []

    def has_events(self):
        return any([self.external, self.internal])

    def add_external_event(self, event):
        '''
        Saves the event for later processing.
        This is meant to be overloaded by a child class to provide a specific queue implementation.
        For instance, a thread-safe queue could be used by a multithreaded state machine implementation.
        '''
        self.external.append(event)

    def add_internal_event(self, event):
        '''
        Saves the internal event for later processing.
        This is meant to be overloaded by a child class to provide a specific queue implementation.
        For instance, a thread-safe queue could be used by a multithreaded state machine implementation.
        '''
        self.internal.append(event)

    def get_event(self):
        if self.internal:
            return self.internal.pop(0)
        if self.external:
            return self.external.pop(0)
        raise NoMoreEvents

class StateMachine(object):
    machine_pool = None
    queues_type = None
    event_transitions = None

    def validate_transitions(self):
        for event, transition in self.event_transitions.items():
            for old_state, new_state in transition.items():
                # old_state can be None
                if old_state:
                    getattr(self, old_state)
                getattr(self, new_state)

    def __init__(self, initial_state=None):
        self.validate_transitions()
        self.queues = self.queues_type()
        if initial_state:
            getattr(self, initial_state)
        self._current_state = initial_state

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        old_state = self._current_state
        self._current_state = new_state
        self.set_state(old_state, new_state)

    def set_state(self, old_state, new_state):
        '''
        Provide an implementation in a derived class if you wish to track each state transition

        Params:
        old_state:  the previous current state when the event was received
        new_state:  the new current state (i.e. the value returned by 'self.current_state')

        Note that 'set_state' is called right before the call to the new_state method is made
        '''
        pass
    def send(self, event_name, *args, **kwargs):
        '''
        send is used for communications between state machines.

        Params:
        event_name:     a string whose value has been declared by a call to add_event_transitions.
        args, kwargs:   a generic function signature

        If event has not been declared via a call add_event_transitions, send will raise a ValueError exception
        '''
        if event_name not in self.event_transitions.keys():
            raise ValueError('Unknown event "{}" sent to {}'.format(event_name, str(self)))

        if isinstance(self.machine_pool, Machines):
            self.machine_pool.add(self)
        else:
            raise AttributeError('This event cannot be processed outside valid a ManagedState context')
        self.queues.add_external_event((event_name, args, kwargs))

    def send_internal(self, event_name, *args, **kwargs):
        if event_name not in event_transitions.keys():
            raise ValueError('Unknown event_name "{}" sent to {}'.format(event_name, str(self)))
        self.queues.add_internal_event( (event_name, args, kwargs) )

    def run(self):
        while self.queues.has_events():
            event, args, kwargs = self.queues.get_event()
            try:
                state_name = self.event_transitions[event][self.current_state]
            except KeyError as e:
                raise Exception('No transition from {} via {}'.format(self.current_state, event))
            self.current_state = state_name
            getattr(self, state_name)(*args, **kwargs)


class ManagedState(ContextDecorator):
    def __init__(self, name=''):
        self.name = name
        self.pool = Machines()
        self.queues_type = Queues

    def __enter__(self):
        StateMachine.machine_pool = self.pool
        StateMachine.queues_type = self.queues_type

    def __exit__(self, exc_type, exc, exc_tb):
        StateMachine.machine_pool.process_all_events()
        StateMachine.machine_pool = None
