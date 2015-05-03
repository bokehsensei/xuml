from functools import singledispatch

from xuml.event import Event

class StateMachineInterface(object):
    '''
    This abstract base class describes how any client code, including possibly another state machine,
    sees an instance of a state machine it wants to talk to.

    Each derived implementation must provide a class-field "event_transitions" which is a dictionary.
    The keys of "event_transitions" are the valid events that can be processed by an instance of this class.
    The values are a dictionary of state transitions.
    Each transition is a key-value pair where the key is the current state and the value the new state.
    Each state must be a method of the class

    For example:

    class MyAbstractStateMachine(StateMachineInterface):
        event_transitions= {
            "make_me_a_sandwich": {
                "watching_tv":      "making_a_sandwich",
                "mowing_the_lawn":  "bitch_about_work",
                },

            "thanks": {
                "making_a_sandwich": "you're welcome",
            },
        }

    '''
    event_transitions = dict()

    def _validate_transitions(self):
        for event, transition in self.event_transitions.items():
            for old_state, new_state in transition.items():
                # old_state can be None
                if old_state:
                    getattr(self, old_state)
                getattr(self, new_state)

    def send(self, event_name, *args, **kwargs):
        '''
        send is used for communications between state machines.

        Params:
        event_name:     a string whose value has been declared by a call to add_event_transitions.
        args, kwargs:   a generic function signature

        If event is not declared in event_transitions, send will raise a ValueError exception
        '''
        if event_name not in self.event_transitions.keys():
            raise ValueError('Unknown event "{}" sent to {}'.format(event_name, str(self)))

    def send_many(self, events):
        '''
        Equivalent of 'send' that takes a list of events instead of a single event.
        Each event is a tuple (event_name, args, kwargs)
        '''
        for event in events:
            self.send(*event)

    def send_event(self, event):
        self.send(event.event_name, *event.args, **event.kwargs)
