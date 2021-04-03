"""Tests for Task"""
from src.task import Task


def test_simple_task():
    """Validate Task can run a simple task"""
    def _foo():
        yield 3
        yield 4

    task = Task(_foo())
    assert task.run() == 3
    assert task.run() == 4