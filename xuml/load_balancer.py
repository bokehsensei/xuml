from xuml.state import StateMachine

class LoadBalancer(StateMachine):
    event_transitions = {
        'new':              {
            'under_capacity':   'allocate',
            'at_max_capacity':  'at_max_capacity'
        },

        'max_reached':  {
            'allocate':         'at_max_capacity'
        },

        'delete_machine':   {
            'at_max_capacity':  'deleting',
            'allocate':         'deleting',
            'deleting':         'deleting',
        },

        'spare_capacity':   {
            'deleting':         'under_capacity',
            'allocate':         'under_capacity',
        },
    }
    def __init__(self, machines, thread_pool_load_balancer=None, capacity=None):
        self.machines = machines
        self.thread_proxies = dict()
        self.process_proxies = dict()
        self.thread_pool_load_balancer = thread_pool_load_balancer
        super().__init__('under_capacity')
        self.under_capacity()

    def under_capacity(self):
        if self.thread_pool_load_balancer:
            self.thread_pool_load_balancer.send('available', self)

    def allocate(client, klass, *args, **kwargs):
        machine = klass(*args, **kwargs)
        self.machines.add(machine)
        proxy = client.proxy_for(machine)
        distance = Proxy.distance(client, self)
        if distance == 0:
            proxy = machine
        elif distance == 1:
            proxy = ThreadProxy(machine)
            self.thread_proxies[id(machine)] = proxy
        elif distance == 2:
            proxy = ProcessProxy(machine)
            self.process_proxies[id(machine)] = proxy
        else:
            raise ValueError('client is too far!')

        client.send('allocated', proxy)

        if capacity and (capacity == len(self.machines)):
            self.send('max_reached')

    def at_max_capacity(self):
        self.thread_pool_load_balancer.send('machine_pool_at_max_capacity', self)

    def deleting(self, machine):
        self.machines.remove(machines)
