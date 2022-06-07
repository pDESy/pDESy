#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_base_component."""

import datetime

from pDESy.model.base_component import BaseComponent, BaseComponentState
from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_workplace import BaseWorkplace


def test_init():
    """test_init."""
    c1 = BaseComponent("c1")
    assert c1.name == "c1"
    assert len(c1.ID) > 0

    c2 = BaseComponent("c2")
    task = BaseTask("task")
    c = BaseComponent(
        "c",
        ID="xx88xx",
        child_component_list=[c1],
        parent_component_list=[c2],
        targeted_task_list=[task],
        space_size=2.0,
        state=BaseComponentState.FINISHED,
        state_record_list=["aa"],
        placed_workplace=BaseWorkplace("t"),
        placed_workplace_id_record=["fff"],
    )
    assert c.name == "c"
    assert c.ID == "xx88xx"
    assert c.child_component_list == [c1]
    assert c.parent_component_list == [c2]
    assert c.targeted_task_list == [task]
    assert c.space_size == 2.0
    assert c.placed_workplace.name == "t"
    assert c.placed_workplace_id_record == ["fff"]


def test_extend_child_component_list():
    """test_extend_child_component_list."""
    c = BaseComponent("c")
    assert c.parent_component_list == []
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.extend_child_component_list([c1, c2])
    assert c.child_component_list == [c1, c2]
    assert c1.parent_component_list == [c]
    assert c2.parent_component_list == [c]


def test_append_child_component():
    """test_append_child_component."""
    c = BaseComponent("c")
    assert c.parent_component_list == []
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    assert c.child_component_list == [c1]
    assert c1.child_component_list == [c2]
    assert c2.parent_component_list == [c1]
    assert c1.parent_component_list == [c]


def test_set_placed_workplace():
    """test_set_placed_workplace."""
    c = BaseComponent("c")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    workplace = BaseWorkplace("workplace")

    c.set_placed_workplace(workplace, set_to_all_children=False)
    assert c.placed_workplace == workplace
    assert c1.placed_workplace is None
    assert c2.placed_workplace is None

    c.set_placed_workplace(workplace, set_to_all_children=True)
    assert c.placed_workplace == workplace
    assert c1.placed_workplace == workplace
    assert c2.placed_workplace == workplace


def test_is_ready():
    """test_is_ready."""
    c = BaseComponent("c")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    c.extend_targeted_task_list([task1, task2])
    assert c.is_ready() is False

    # case 1
    task1.state = BaseTaskState.READY
    assert c.is_ready() is True

    # case 2
    task2.state = BaseTaskState.WORKING
    assert c.is_ready() is False

    # case 3
    task2.state = BaseTaskState.FINISHED
    assert c.is_ready() is True

    # case 4
    task1.state = BaseTaskState.FINISHED
    task2.state = BaseTaskState.FINISHED
    assert c.is_ready() is False


def test_extend_targeted_task_list():
    """test_extend_targeted_task_list."""
    c = BaseComponent("c")
    assert c.parent_component_list == []
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    c.extend_targeted_task_list([task1, task2])
    assert c.targeted_task_list == [task1, task2]
    assert task1.target_component == c
    assert task2.target_component == c


def test_append_targeted_task():
    """test_append_targeted_task."""
    c = BaseComponent("c")
    assert c.parent_component_list == []
    task = BaseTask("task1")
    assert task.target_component is None
    c.append_targeted_task(task)
    assert c.targeted_task_list == [task]
    assert task.target_component == c


def test_initialize():
    """test_initialize."""
    pass


def test_str():
    """test_str."""
    print(BaseComponent("c1"))


def test_create_data_for_gantt_plotly():
    """test_create_data_for_gantt_plotly."""
    c = BaseComponent("c")
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


def test_remove_absence_time_list():
    """test_remove_absence_time_list."""
    w = BaseComponent("w1", "----")
    w.placed_workplace_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w.state_record_list = [0, 1, 2, 3, 4, 5]

    absence_time_list = [0, 1]
    w.remove_absence_time_list(absence_time_list)
    assert w.placed_workplace_id_record == ["cc", "dd", "ee", "ff"]
    assert w.state_record_list == [2, 3, 4, 5]
