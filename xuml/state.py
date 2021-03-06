from collections import namedtuple

from xuml.state_machine_interface import StateMachineInterface
from xuml.exceptions import InvalidContext, InvalidEvent, NoTransition
from xuml.synchronous.queues import SynchronousQueues

Id = namedtuple('Id', ['machine', 'machine_pool_id'])

class StateMachine(StateMachineInterface):
    queues_type = SynchronousQueues

    def __init__(self, pool, initial_state=None):
        self.pool = pool
        self.id = Id(id(self), getattr(self.pool, 'id'))
        self._validate_transitions()
        self.queues = self.queues_type()
        if initial_state:
            getattr(self, initial_state)
        self._current_state = initial_state
        self.pool[self.id] = self

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
        send is used for communications between state pool.

        Params:
        event_name:     a string whose value has been declared by a call to add_event_transitions.
        args, kwargs:   a generic function signature

        If event has not been declared via a call add_event_transitions, send will raise an InvalidEvent exception
        If send is called outside a with statement with a ManagedState context, it will raise an InvalidContext exception.
        '''
        super().send(event_name, *args, **kwargs)
        self.queues.add_external_event((event_name, args, kwargs))

    def send_internal(self, event_name, *args, **kwargs):
        if event_name not in self.event_transitions:
            raise InvalidEvent(event_name, self)
        self.queues.add_internal_event( (event_name, args, kwargs) )

    def run(self):
        while self.queues.has_events():
            event, args, kwargs = self.queues.get_event()
            try:
                state_name = self.event_transitions[event][self.current_state]
            except KeyError as e:
                raise NoTransition(self.current_state, event)
            self.current_state = state_name
            try:
                getattr(self, state_name)(*args, **kwargs)
            except Exception as e:
                print('Caught exception:\n{} while executing state "{}" for machine {}'.format(
                    e,
                    state_name,
                    self
                ))

    def new(self, klass, *args, **kwargs):
        self.pool.new(klass, *args, **kwargs)
