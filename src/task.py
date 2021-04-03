"""Task"""

# pylint: disable=too-few-public-methods

class SystemCall():
    """System Call"""
    def control(self, current_task, current_scheduler):
        """Set SystemCall current state"""
        self.task = current_task
        self.scheduler = current_scheduler

    def handle(self):
        """Handle SystemCall"""


class Task():
    """Task Object"""
    taskid = 0
    def __init__(self, target):
        """Task init"""
        Task.taskid += 1
        self.tid = Task.taskid
        self.target = target
        self.sendval = None

    def run(self):
        """Task run"""
        return self.target.send(self.sendval)


class GetTid(SystemCall):
    """Get current task ID system call"""
    def handle(self):
        """GetTid handle method"""
        self.task.sendval = self.task.tid
        self.scheduler.schedule(self.task)


class NewTask(SystemCall):
    """Create new task system call"""
    def __init__(self, target):
        """Init"""
        self.target = target

    def handle(self):
        """NewTask handle method"""
        tid = self.scheduler.new(self.target)
        self.task.sendval = tid
        self.scheduler.schedule(self.task)


class KillTask(SystemCall):
    """Kill an existed task system call"""
    def __init__(self, tid):
        """Init"""
        self.tid = tid

    def handle(self):
        """KillTask handle method
        Send True if task existed, else False"""
        task = self.scheduler.taskmap.get(self.tid, None)
        if task:
            # end the generator
            task.target.close()
            self.task.sendval = True
        else:
            self.task.sendval = False

        # put task which call KillTask back to schedule queue
        self.scheduler.schedule(self.task)


class WaitTask(SystemCall):
    """Wait for a task to finish system call"""
    def __init__(self, tid):
        """Init"""
        self.tid = tid

    def handle(self):
        """WaitTask handle method.
        Put original task back to scheduler queue if wait for task
        finished"""
        finished = self.scheduler.wait_for_exit(self.task, self.tid)
        self.task.sendval = finished
        if finished:
            self.scheduler.schedule(self.task)
