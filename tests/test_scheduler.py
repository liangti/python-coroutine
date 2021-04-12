"""Tests for Scheduler"""
from uuid import uuid1

from src.task import GetTid, NewTask, KillTask, WaitTask, ReadWait, WriteWait
from src.scheduler import Scheduler


def test_simple_multitask():
    """Validate multitask scheduling by Scheduler"""
    bucket = []
    def _foo():
        for i in range(10):
            bucket.append(i)
            yield

    scheduler = Scheduler()
    scheduler.new(_foo())
    scheduler.new(_foo())
    scheduler.mainloop()

    expect_bucket = []
    for i in range(10):
        expect_bucket.append(i)
        expect_bucket.append(i)
    assert bucket == expect_bucket


def test_get_tid():
    """Validate GetTid system call returns task id"""
    tids = []
    def _foo():
        mytid = yield GetTid()
        tids.append(mytid)
        for i in range(5):
            yield i

    scheduler = Scheduler()
    scheduler.new(_foo())
    scheduler.new(_foo())
    scheduler.mainloop()

    # can we do better than hard code?
    assert tids == [4, 5]


def test_new_task():
    """Validate NewTask system call create new task in scheduler"""
    bucket = []
    def child():
        for i in range(5):
            bucket.append(i)
            yield i
    def parent():
        _ = yield NewTask(child())

    scheduler = Scheduler()
    scheduler.new(parent())
    scheduler.mainloop()

    assert bucket == [0, 1, 2, 3, 4]


def test_kill_task():
    """Validate KillTask system call kill right task"""
    bucket = []
    def child():
        for i in range(5):
            bucket.append(i)
            yield i

    def parent():
        new_tid = yield NewTask(child())
        # kill non existed task
        success = yield KillTask(100000)
        assert success is False
        # kill existed task
        success = yield KillTask(new_tid)
        assert success is True

    scheduler = Scheduler()
    scheduler.new(parent())
    scheduler.mainloop()

    # child coroutine stops at first iteration
    assert bucket == [0, 1]


def test_wait_for_task():
    """Validate WaitFor system call wait for child task to finish"""
    end_flag = int(uuid1())
    bucket = []
    def child():
        for i in range(5):
            bucket.append(i)
        yield i

    def parent():
        new_tid = yield NewTask(child())
        yield WaitTask(new_tid)
        bucket.append(end_flag)

    scheduler = Scheduler()
    scheduler.new(parent())
    scheduler.mainloop()

    # child task should finish and end flag should be
    # added to the end of the list
    expect_bucket = [0, 1, 2, 3, 4]
    expect_bucket.append(end_flag)
    assert bucket == expect_bucket


def test_wait_for_io():
    """Validate ReadWait/WriteWait wait for file descriptor to be available"""
    bucket = []
    file_obj = None
    def read():
        bucket.append(0)
        yield ReadWait(file_obj)
        bucket.append(1)

    def write():
        bucket.append(2)
        yield WriteWait(file_obj)
        bucket.append(3)

    with open('README.md', 'a+') as handler:
        file_obj = handler

        scheduler = Scheduler()
        scheduler.new(read())
        scheduler.new(write())
        scheduler.mainloop()

    assert bucket == [0, 2, 1, 3]