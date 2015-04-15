from ..managed_state import ManagedState
from .machines import SynchronousMachines
from .queues import SynchronousQueues
from xuml.load_balancer import LoadBalancer

class SynchronousManagedState(ManagedState):
    def __init__(self, name='', thread_pool=None):
        super().__init__(name)
        self.machines = SynchronousMachines()
        self.thread_pool = thread_pool
        self.load_balancer = LoadBalancer(self.machines, thread_pool)
        self.machines.add(self.load_balancer)
        self.queues_type = SynchronousQueues
