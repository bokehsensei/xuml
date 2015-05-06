from xuml.state_machine_interface import StateMachineInterface
from xuml.event import Event

def proxy(source, destination):
    '''
    source is an instance of a StateMachine.
    destination is an instance of the Id of a remote StateMachine.
    Returns a queue
    TODO: add caching
    '''
    if destination in source.pool:
        return source.pool[destination]
    elif (source.pool.thread_pool and (destination.machine_pool_id in source.pool.thread_pool.machine_pools)):
        return Proxy(source, destination, source.pool.thread_pool.machine_pools[destination.machine_pool_id].queue)
    else:
        raise ValueError('Machine is in a different process. Not implemented yet!')


class Proxy(StateMachineInterface):

    def __init__(self, source, destination, queue):
        self.source = source
        self.id = destination
        self.queue = queue

    def send(self, event_name, *args, **kwargs):
        self.queue.put(Event(self.source, self.id, event_name, args, kwargs))
