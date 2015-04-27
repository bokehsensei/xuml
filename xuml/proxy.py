from xuml.state_machine_interface import StateMachineInterface

class Proxy(StateMachineInterface):
    def __init__(self, machine):
        self.machine = machine
        self.queue = None

    def send(self, event_name, *args, **kwargs):
        self.queue.put((event_name, args, kwargs))
