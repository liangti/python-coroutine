"""Scheduler"""
import select
from queue import Queue

from src.task import Task, SystemCall

class Scheduler:
    """Scheduler"""
    def __init__(self):
        """Scheduler init"""
        self.ready = Queue()
        self.taskmap = {}
        # map tid to task waiting for it to exit
        self.exitwait = {}
        # map fd to task waiting for reading from it
        self.readwait = {}
        # map fd to task waiting for writing from it
        self.writewait = {}

    def new(self, target):
        """New a target to a task"""
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def exit(self, task):
        """Exit a task"""
        del self.taskmap[task.tid]
        # wake up tasks which are waiting for current task to exit
        # and pop current task from exitwait
        for task in self.exitwait.pop(task.tid, []):
            self.schedule(task)

    def wait_for_exit(self, task, waittid):
        """Given a task and another task that it is waiting for,
        return false if wait_task hasn't finished, else true"""
        if waittid in self.taskmap:
            self.exitwait.setdefault(waittid, []).append(task)
            return False

        return True

    def wait_for_read(self, task, fd):
        """Task is waiting for reading from fd"""
        self.readwait[fd] = task

    def wait_for_write(self, task, fd):
        """Task is waiting for writing from fd"""
        self.writewait[fd] = task

    def iopoll(self, timeout=0):
        """Poll system IO"""
        if self.readwait or self.writewait:
            readable, writable, _ = select.select(self.readwait,
                                                  self.writewait,
                                                  [], timeout)
            # pop tasks waiting for readable fd
            for fd in readable:
                self.schedule(self.readwait.pop(fd))
            # pop tasks waiting for writable fd
            for fd in writable:
                self.schedule(self.writewait.pop(fd))

    def iotask(self):
        """Scheduler internal io task"""
        while True:
            if self.ready.empty():
                # if no ready task wait for IO read infinitely
                self.iopoll(None)
            else:
                # else no blocking
                self.iopoll(0)
            yield

    def schedule(self, task):
        """Schedule a task"""
        self.ready.put(task)

    def mainloop(self, exit_no_task=True):
        """Scheduler main loop.
        If `exit_no_task` set to true, when there is no task anymore,
        exit instead of waiting infinitely
        """
        io_task_tid = self.new(self.iotask())
        while self.taskmap:
            task = self.ready.get()

            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    # pass the control to system call
                    result.control(task, self)
                    result.handle()
                    # do not put the task back to the queue
                    continue
            except StopIteration:
                self.exit(task)
                continue
            # when exit_no_task is set and iotask is the only task exit it
            if exit_no_task and len(self.taskmap) == 1 and \
                    task == self.taskmap[io_task_tid]:
                self.exit(task)
                break

            self.schedule(task)