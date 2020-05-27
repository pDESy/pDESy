#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.component import Component
from pDESy.model.task import Task
import datetime


def test_init():
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
        depending_component_list=[c1],
        depended_component_list=[c2],
        targeted_task_list=[task],
    )
    assert c.name == "c"
    assert c.ID == "xx88xx"
    assert c.error_tolerance == 0.1
    assert c.error == 0.0
    assert c.depending_component_list == [c1]
    assert c.depended_component_list == [c2]
    assert c.targeted_task_list == [task]


def test_extend_child_component_list():
    c = Component("c", error_tolerance=0.1)
    assert c.depended_component_list == []
    c1 = Component("c1")
    c2 = Component("c2")
    c.extend_child_component_list([c1, c2])
    assert c.depended_component_list == [c1, c2]
    assert c1.depending_component_list == [c]
    assert c2.depending_component_list == [c]


def test_append_child_component():
    c = Component("c", error_tolerance=0.1)
    assert c.depended_component_list == []
    c1 = Component("c1")
    c2 = Component("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    assert c.depended_component_list == [c1]
    assert c1.depended_component_list == [c2]
    assert c2.depending_component_list == [c1]
    assert c1.depending_component_list == [c]


def test_extend_targeted_task_list():
    c = Component("c", error_tolerance=0.1)
    assert c.depended_component_list == []
    task1 = Task("task1")
    task2 = Task("task2")
    c.extend_targeted_task_list([task1, task2])


def test_append_targeted_task():
    c = Component("c", error_tolerance=0.1)
    assert c.depended_component_list == []
    task = Task("task1")
    assert task.target_component_list == []
    c.append_targeted_task(task)
    assert c.targeted_task_list == [task]
    assert task.target_component_list == [c]


def test_initialize():
    c = Component("c", error_tolerance=0.1)
    c.error += 1
    assert c.error == 1
    c.initialize()
    assert c.error == 0


def test_update_error_value():
    c = Component("c")
    c.update_error_value(0.9, 1.0, seed=32)  # seed==32 -> rand()=0.85
    assert c.error == 0.0
    c.update_error_value(0.4, 0.5, seed=32)  # seed==32 -> rand()=0.85
    assert c.error == 0.5
    c.update_error_value(0.4, 0.5)


def test_str():
    print(Component("c1"))


def test_create_data_for_gantt_plotly():
    c = Component("c")
    task1 = Task("task1")
    task2 = Task("task2")
    c.extend_targeted_task_list([task1, task2])

    # Set test case (start time = 0, finish time = 5)
    task1.start_time_list = [0, 2]
    task1.ready_time_list = [0, 2]
    task1.finish_time_list = [3, 5]
    task2.start_time_list = [1]
    task2.ready_time_list = [2]
    task2.finish_time_list = [5]
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)

    # timedelta = 1day
    timedelta = datetime.timedelta(days=1)
    df = c.create_data_for_gantt_plotly(init_datetime, timedelta)
    assert df[0]["Start"] == (init_datetime + 0 * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[0]["Finish"] == (init_datetime + (5 + 0.9) * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[0]["Type"] == "Component"
