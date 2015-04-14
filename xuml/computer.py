from multiprocessing import cpu_count
from multiprocessing.managers import BaseManager

from xuml.thread_pool import ThreadPool

class Computer(set):

    def boot(self):
        for i in range(cpu_count()):
            self.add(ThreadPool())

    def kill(self):
        for pool in self:
            print('killing {}'.format(pool.process.name))
            pool.pipe.send('stop')
            pool.process.join()
        self.clear()

class ComputerManager(BaseManager):
    def __init__(self, address=None):
        self.computer = Computer()
        super().__init__(address=address or ('127.0.0.1', 50000), authkey=b'foobar')
 
ComputerManager.register('computers')
ComputerManager.register('boot')
ComputerManager.register('kill')
