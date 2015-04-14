from xuml.computer import Computer, ComputerManager

class Cloud(object):

    def __init__(self, name=None):
        self.name = name
        self.computers = []
        self.computer_managers = []
        ComputerManager.register('boot',   callable=lambda i: self.computers[i].boot())
        ComputerManager.register('kill',   callable=lambda i: self.computers[i].kill())

    def boot(self):
        address = ('127.0.0.1', 50000)
        for i in range(2):
            mgr = ComputerManager((address[0], address[1]+i))
            self.computers.append(mgr.computer)
            mgr.start()
            mgr.boot(i)

    def kill(self):
        for i, mgr in enumerate(self.computer_managers):
            mgr.kill(i)
            mgr.shutdown()

if __name__ == '__main__':
    Cloud().boot()
