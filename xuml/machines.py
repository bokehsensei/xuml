from xuml.exceptions import AbstractMachines

class Machines(dict):
    def __init__(self, *args, **kwargs):
        self.id = id(self)
        super().__init__(*args, **kwargs)

    def has_events(self):
        raise AbstractMachines()

    def process_all_events(self):
        raise AbstractMachines()
