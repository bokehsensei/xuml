from xuml.machines import Machines
import copy

class SynchronousMachines(Machines):
    def has_events(self):
        return any([machine.queues.has_events() for machine in self.values()])

    def process_all_events(self):
        while self.has_events():
            copy_self = copy.copy(self)
            for machine in copy_self.values():
                machine.run()
