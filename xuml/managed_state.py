from contextlib import ContextDecorator

from .state_machine_interface import StateMachineInterface
from .state import StateMachine
from .queues import Queues
from .machines import Machines

class ManagedState(ContextDecorator):
    def __init__(self, name=''):
        self.name = name
        self.machines = None
        self.queues_type = None

    def new(self, state_machine_class, *args, **kwargs):
        if not issubclass(state_machine_class, StateMachineInterface):
            raise StateMachineTypeError(state_machine_class)

        return state_machine_class(*args, **kwargs)

    def __enter__(self):
        if not isinstance(self.machines, Machines):
            raise MachinesTypeError(self.machines)
        if not issubclass(self.queues_type, Queues):
            raise QueuesTypeError(self.queues_type)

        StateMachine.machines = self.machines
        StateMachine.queues_type = self.queues_type
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.machines.process_all_events()
        StateMachine.machines = None
