class AbstractQueuesError(NotImplementedError):
    def __init__(self):
        super().__init__("Only Queues-derived classes are allowed")

class AbstractStateMachineInterface(NotImplementedError):
    def __init__(self):
        super().__init__('StateMachineInterface is not directly usable')

class AbstractMachines(NotImplementedError):
    def __init__(self):
        super().__init__('Machines is an abstract class, you must use an object that derives from it')

class InvalidContext(AttributeError):
    def __init__(self):
        super().__init__('This event cannot be processed outside valid a ManagedState context')

class InvalidEvent(ValueError):
    def __init__(self, event_name, state_machine):
        super().__init__('Unknown event_name "{}" sent to {}'.format(event_name, str(state_machine)))

class NoTransition(ValueError):
    def __init__(self, current_state, event):
        super().__init__('No transition from {} via {}'.format(current_state, event))

class MachinesTypeError(TypeError):
    def __init__(self, machines):
        super().__init__('Expected subtype of Machines, instead got type {}'.format(type(machines)))

class QueuesTypeError(TypeError):
    def __init__(self, queues_type):
        super().__init__('Expected subtype of Queues, instead got type {}'.format(queues_type))

class StateMachineTypeError(TypeError):
    def __init__(self, state_machine_type):
        super().__init__('Expected subtype of StateMachineInterface, instead got type {}'.format(state_machine_type))
