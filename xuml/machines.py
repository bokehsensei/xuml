from .exceptions import AbstractMachines

class Machines(dict):

    def has_events(self):
        raise AbstractMachines()

    def process_all_events(self):
        raise AbstractMachines()
