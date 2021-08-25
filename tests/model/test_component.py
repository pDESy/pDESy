#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_component."""

import datetime

from pDESy.model.base_component import BaseComponentState
from pDESy.model.component import Component
from pDESy.model.task import Task


def test_init():
    """test_init."""
    c1 = Component("c1")
    assert c1.name == "c1"
    assert len(c1.ID) > 0
    assert c1.error_tolerance == 0.0
    assert c1.error == 0.0

    c2 = Component("c2")
    task = Task("task")
    c = Component(
        "c",
        ID="xx88xx",
        error_tolerance=0.1,
        error=0.0,
        child_component_list=[c1],
        parent_component_list=[c2],
        targeted_task_list=[task],
    )
    assert c.name == "c"
    assert c.ID == "xx88xx"
    assert c.error_tolerance == 0.1
    assert c.error == 0.0
    assert c.child_component_list == [c1]
    assert c.parent_component_list == [c2]
    assert c.targeted_task_list == [task]


def test_extend_child_component_list():
    """test_extend_child_component_list."""
    c = Component("c")
    assert c.parent_component_list == []
    c1 = Component("c1")
    c2 = Component("c2")
    c.extend_child_component_list([c1, c2])
    assert c.child_component_list == [c1, c2]
    assert c1.parent_component_list == [c]
    assert c2.parent_component_list == [c]


def test_append_child_component():
    """test_append_child_component."""
    c = Component("c", error_tolerance=0.1)
    assert c.parent_component_list == []
    c1 = Component("c1")
    c2 = Component("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    assert c.child_component_list == [c1]
    assert c1.child_component_list == [c2]
    assert c2.parent_component_list == [c1]
    assert c1.parent_component_list == [c]


def test_extend_targeted_task_list():
    """test_extend_targeted_task_list."""
    c = Component("c")
    assert c.parent_component_list == []
    task1 = Task("task1")
    task2 = Task("task2")
    c.extend_targeted_task_list([task1, task2])
    assert c.targeted_task_list == [task1, task2]
    assert task1.target_component == c
    assert task2.target_component == c


def test_append_targeted_task():
    """test_append_targeted_task."""
    c = Component("c", error_tolerance=0.1)
    assert c.parent_component_list == []
    task = Task("task1")
    assert task.target_component is None
    c.append_targeted_task(task)
    assert c.targeted_task_list == [task]
    assert task.target_component == c


def test_initialize():
    """test_initialize."""
    c = Component("c", error_tolerance=0.1)
    c.error += 1
    assert c.error == 1
    c.initialize()
    assert c.error == 0


def test_update_error_value():
    """test_update_error_value."""
    c = Component("c")
    c.update_error_value(0.9, 1.0, seed=32)  # seed==32 -> rand()=0.85
    assert c.error == 0.0
    c.update_error_value(0.4, 0.5, seed=32)  # seed==32 -> rand()=0.85
    assert c.error == 0.5
    c.update_error_value(0.4, 0.5)


def test_str():
    """test_str."""
    print(Component("c1"))


def test_create_data_for_gantt_plotly():
    """test_create_data_for_gantt_plotly."""
    c = Component("c")
    c.state_record_list = [
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    c.create_data_for_gantt_plotly(init_datetime, timedelta)
