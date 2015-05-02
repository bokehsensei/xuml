from xuml.process_proxy import ProcessProxy
from xuml.state import StateMachine

class LoadBalancer(StateMachine):
    event_transitions = {
        'new':              {
            'under_capacity':   'allocate',
            'at_max_capacity':  'error_max_capacity'
        },

        'max_reached':  {
            'allocate':             'notify_over',
            'notify_over':        'at_max_capacity',
            'error_max_capacity':   'at_max_capacity',
        },

        'delete_machine':   {
            'at_max_capacity':  'notify_under',
            'notify_under':     'deleting',
            'under_capacity':   'deleting',
        },

        'spare_capacity':   {
            'deleting':         'under_capacity',
            'allocate':         'under_capacity',
        },
    }

    def __init__(self, machine_pool, thread_pool_load_balancer=None, capacity=None):
        self.machine_pool = machine_pool
        self.capacity = capacity
        self.thread_pool_load_balancer = thread_pool_load_balancer
        super().__init__('under_capacity')
        self.under_capacity()

    def under_capacity(self):
        if self.thread_pool_load_balancer:
            self.thread_pool_load_balancer.send('available', self)

    def allocate(self, klass, *args, **kwargs):
        machine = klass(*args, **kwargs)
        self.machine_pool[machine._id] = machine

        if self.capacity and (self.capacity == len(self.machine_pool)):
            self.send_internal('max_reached')
        else:
            self.send_internal('spare_capacity')

    def at_max_capacity(self):
        pass

    def error_max_capacity(self, client, klass, *args, **kwargs):
        client.send('error')

    def deleting(self, machine):
        self.machine_pool.remove(machine)

    def notify_over(self):
        self.thread_pool_load_balancer.send('machine_pool_at_max_capacity', self)

    def notify_under(self):
        self.thread_pool_load_balancer.send('machine_pool_under_capacity', self)
