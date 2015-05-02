from xuml.state_machine_interface import StateMachineInterface
from xuml.event import Event

class Proxy(StateMachineInterface):

    def __init__(self, source_id, machine_id, local_machine_pool):
        if not machine_id:
            raise ValueError('Cannot create a valid AllocatedProxy object without a StateMachine id')
        if not local_machine_pool:
            raise ValueError('Cannot create a valid AllocatedProxy object without an instance of a MachinePool')
        self.source_id = source_id
        self.machine_id = machine_id
        if machine_id in local_machine_pool.keys():
            self.queue = local_machine_pool[machine_id].queues.external
            self.send = self._send_list_queue
        elif (local_machine_pool.thread_pool and (machine_id.machine_pool_id in local_machine_pool.thread_pool.machine_pools)):
            self.queue = local_machine_pool.thread_pool.machine_pools[machine_id.machine_pool_id].queue
        else:
            raise ValueError('Machine is in a different process. Not implemented yet!')

    def send(self, event_name, *args, **kwargs):
        self.queue.put(Event(self.source_id, self.machine_id, event_name, args, kwargs))

    def _send_list_queue(self, event_name, *args, **kwargs):
        self.queue.append((event_name, args, kwargs))
