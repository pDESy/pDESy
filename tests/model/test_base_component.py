#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_base_component."""

import pytest

from pDESy.model.base_component import BaseComponent, BaseComponentState
from pDESy.model.base_task import BaseTask
from pDESy.model.base_workplace import BaseWorkplace


def test_init():
    """test_init."""
    c1 = BaseComponent("c1")
    assert c1.name == "c1"
    assert len(c1.ID) > 0
    assert c1.error_tolerance == 0.0
    assert c1.error == 0.0

    task = BaseTask("task")
    c = BaseComponent(
        "c",
        ID="xx88xx",
        child_component_id_set={c1.ID},
        targeted_task_id_list=[task.ID],
        space_size=2.0,
        state=BaseComponentState.FINISHED,
        state_record_list=["aa"],
        error_tolerance=0.1,
        error=0.0,
        placed_workplace_id=BaseWorkplace("t").ID,
        placed_workplace_id_record=["fff"],
    )
    assert c.name == "c"
    assert c.ID == "xx88xx"
    assert c.child_component_id_set == {c1.ID}
    assert c.targeted_task_id_list == [task.ID]
    assert c.space_size == 2.0
    assert c.placed_workplace_id_record == ["fff"]
    assert c.error_tolerance == 0.1
    assert c.error == 0.0


def test_extend_child_component_list():
    """test_extend_child_component_list."""
    c = BaseComponent("c")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.extend_child_component_list([c1, c2])
    assert c.child_component_id_set == {c1.ID, c2.ID}


def test_append_child_component():
    """test_append_child_component."""
    c = BaseComponent("c")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    assert c.child_component_id_set == {c1.ID}
    assert c1.child_component_id_set == {c2.ID}


def test_extend_targeted_task_list():
    """test_extend_targeted_task_list."""
    c = BaseComponent("c")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    c.extend_targeted_task_list([task1, task2])
    assert c.targeted_task_id_list == [task1.ID, task2.ID]
    assert task1.target_component_id == c.ID
    assert task2.target_component_id == c.ID


def test_update_error_value():
    """test_update_error_value."""
    c = BaseComponent("c")
    c.update_error_value(0.9, 1.0, seed=32)  # seed==32 -> rand()=0.85
    assert c.error == 0.0
    c.update_error_value(0.4, 0.5, seed=32)  # seed==32 -> rand()=0.85
    assert c.error == 0.5
    c.update_error_value(0.4, 0.5)


def test_append_targeted_task():
    """test_append_targeted_task."""
    c = BaseComponent("c")
    task = BaseTask("task1")
    assert task.target_component_id is None
    c.append_targeted_task(task)
    assert c.targeted_task_id_list == [task.ID]
    assert task.target_component_id == c.ID


def test_initialize():
    """test_initialize."""
    c = BaseComponent("c", error_tolerance=0.1)
    c.error += 1
    assert c.error == 1
    c.initialize()
    assert c.error == 0


def test_str():
    """test_str."""
    print(BaseComponent("c1"))


def test_remove_insert_absence_time_list():
    """test_remove_insert_absence_time_list."""
    w = BaseComponent("w1", "----")
    w.placed_workplace_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w.state_record_list = [0, 1, 2, 3, 4, 5]

    absence_time_list = [0, 1]
    w.remove_absence_time_list(absence_time_list)
    assert w.placed_workplace_id_record == ["cc", "dd", "ee", "ff"]
    assert w.state_record_list == [2, 3, 4, 5]

    w.insert_absence_time_list(absence_time_list)
    assert w.placed_workplace_id_record == [None, None, "cc", "dd", "ee", "ff"]
    assert w.state_record_list == [
        BaseComponentState.NONE,
        BaseComponentState.READY,
        2,
        3,
        4,
        5,
    ]


def test_get_time_list_for_gantt_chart():
    """test_get_time_list_for_gantt_chart."""
    w = BaseComponent("w1", "----")
    w.state_record_list = [
        BaseComponentState.NONE,
        BaseComponentState.READY,
        BaseComponentState.WORKING,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(1, 1)]
    assert working_time_list == [(2, 1)]

    w.state_record_list = [
        BaseComponentState.NONE,
        BaseComponentState.READY,
        BaseComponentState.READY,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(1, 2)]
    assert not working_time_list

    w.state_record_list = [
        BaseComponentState.NONE,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert not ready_time_list
    assert working_time_list == [(1, 1)]

    # for backward
    w.state_record_list = [
        BaseComponentState.FINISHED,
        BaseComponentState.WORKING,
        BaseComponentState.READY,
        BaseComponentState.READY,
        BaseComponentState.FINISHED,
        BaseComponentState.WORKING,
        BaseComponentState.WORKING,
        BaseComponentState.READY,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(2, 2), (7, 1)]
    assert working_time_list == [(1, 1), (5, 2)]


@pytest.fixture(name="dummy_component")
def fixture_dummy_component():
    """fixture_dummy_component."""
    return BaseComponent("dummy_component")


def test_print_mermaid_diagram(dummy_component):
    """Test the print_mermaid_diagram method."""
    dummy_component.print_mermaid_diagram(
        subgraph=True,
    )
