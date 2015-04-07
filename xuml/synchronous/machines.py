from ..machines import Machines
import copy

class SynchronousMachines(Machines):
    def process_all_events(self):
        while any([machine.queues.has_events() for machine in self]):
            copy_self = copy.copy(self)
            for machine in copy_self:
                machine.run()
