
from .state_machine_interface import StateMachineInterface
from .state import StateMachine
from .queues import Queues
from .machines import Machines
from xuml.exceptions import InvalidContext

class ManagedState(object):
    def __init__(self, name=''):
        self.name = name
        self.machines = None
        self.queues_type = None

    def new(self, state_machine_class, *args, **kwargs):
        if not issubclass(state_machine_class, StateMachineInterface):
            raise StateMachineTypeError(state_machine_class)
        if self.machines == None:
            raise InvalidContext()

        kwargs['pool'] = self.machines
        new_machine = state_machine_class(*args, **kwargs)
        self.machines[new_machine.id] = new_machine
        return new_machine

    def __enter__(self):
        if not isinstance(self.machines, Machines):
            raise MachinesTypeError(self.machines)
        if not issubclass(self.queues_type, Queues):
            raise QueuesTypeError(self.queues_type)

        StateMachine.queues_type = self.queues_type
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.machines.process_all_events()
        StateMachine.machines = None
