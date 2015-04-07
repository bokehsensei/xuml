from .exceptions import AbstractMachines

class Machines(set):
    def process_all_events(self):
        raise AbstractMachines()
