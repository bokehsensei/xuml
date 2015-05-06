from xuml.state import StateMachine
from xuml.proxy import proxy

class LoadBalancer(StateMachine):
    event_transitions = {
        'new':              {
            'NOT_FULL':   'allocate',
            'FULL':  'error_max_capacity'
        },

        'full':  {
            'allocate':             'notify_over',
            'notify_over':        'FULL',
            'error_max_capacity':   'FULL',
        },

        'delete_machine':   {
            'FULL':  'notify_under',
            'notify_under':     'deleting',
            'NOT_FULL':   'deleting',
        },

        'not_full':   {
            'deleting':         'NOT_FULL',
            'allocate':         'NOT_FULL',
            'notify_under':     'NOT_FULL'
        },
    }

    def __init__(self, machine_pool, thread_pool_load_balancer_id, capacity=None, pool=None):
        super().__init__(pool, 'notify_under')
        self.pool = machine_pool
        self.capacity = capacity
        self.thread_pool_load_balancer = proxy(self, thread_pool_load_balancer_id)
        self.notify_under()

    def NOT_FULL(self):
        #print('{} NOT FULL')
        pass

    def allocate(self, klass, *args, **kwargs):
        self.pool.allocate(klass, *args, **kwargs)

        if self.capacity and (self.capacity == len(self.pool)):
            self.send_internal('full')
        else:
            self.send_internal('not_full')

    def FULL(self):
        #print('{} FULL')
        pass

    def error_max_capacity(self, client, klass, *args, **kwargs):
        client.send('error')

    def deleting(self, machine):
        self.pool.remove(machine)

    def notify_over(self):
        self.thread_pool_load_balancer.send('not_available', self.id)
        self.send_internal('full')

    def notify_under(self):
        self.thread_pool_load_balancer.send('available', self.id)
        self.send_internal('not_full')
