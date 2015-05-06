from ..managed_state import ManagedState
from .machines import SynchronousMachines
from .queues import SynchronousQueues

class SynchronousManagedState(ManagedState):
    def __init__(self, name=''):
        super().__init__(name)
        self.machines = SynchronousMachines()
        self.queues_type = SynchronousQueues
