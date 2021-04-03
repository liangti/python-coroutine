"""Scheduler"""
from queue import Queue

from src.task import Task, SystemCall

class Scheduler:
    """Scheduler"""
    def __init__(self):
        """Scheduler init"""
        self.ready = Queue()
        self.taskmap = {}
        self.exitwait = {}

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

    def schedule(self, task):
        """Schedule a task"""
        self.ready.put(task)

    def mainloop(self):
        """Scheduler main loop"""
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
            self.schedule(task)