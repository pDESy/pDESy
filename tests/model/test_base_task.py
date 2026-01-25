#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for BaseTask.

This module contains unit tests for the BaseTask class and related functionality.
"""

import pytest

from pDESy.model.base_task import BaseTask, BaseTaskDependency, BaseTaskState
from pDESy.model.base_worker import BaseWorker


def test_init():
    """Test initialization of BaseTask."""
    task = BaseTask("task")
    assert task.name == "task"
    assert len(task.ID) > 0
    assert task.default_work_amount == 10.0
    assert task.input_task_id_dependency_set == set()
    assert task.due_time == -1
    assert task.allocated_team_id_set == set()
    assert task.allocated_workplace_id_set == set()
    assert task.target_component_id is None
    assert task.default_progress == 0.0
    assert task.fixing_allocating_worker_id_set is None
    assert task.fixing_allocating_facility_id_set is None
    assert task.additional_work_amount == 0.0
    assert task.est == 0.0
    assert task.eft == 0.0
    assert task.lst == -1.0
    assert task.lft == -1.0
    assert task.remaining_work_amount == task.default_work_amount * (
        1.0 - task.default_progress
    )
    assert task.actual_work_amount == task.default_work_amount * (
        1.0 - task.default_progress
    )
    assert task.state == BaseTaskState.NONE
    assert task.allocated_worker_facility_id_tuple_set == set()

    w = BaseWorker("a")

    tb = BaseTask(
        "task_b1",
        remaining_work_amount=0.0,
        state=BaseTaskState.FINISHED,
        state_record_list=["a"],
        fixing_allocating_worker_id_set={"aaa", "bbb"},
        fixing_allocating_facility_id_set={"ccc", "ddd"},
        allocated_worker_facility_id_tuple_set={(w.ID, None)},
        allocated_worker_facility_id_tuple_set_record_list=[{(w.ID, None)}],
        additional_task_flag=True,
    )
    assert tb.fixing_allocating_worker_id_set == {"aaa", "bbb"}
    assert tb.fixing_allocating_facility_id_set == {"ccc", "ddd"}
    assert tb.remaining_work_amount == 0.0
    assert tb.state == BaseTaskState.FINISHED
    assert tb.allocated_worker_facility_id_tuple_set_record_list == [{(w.ID, None)}]
    assert tb.additional_task_flag is True


def test_str():
    """Test string representation of BaseTask."""
    print(BaseTask("task"))


def test_add_input_task():
    """Test adding an input task dependency."""
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task2.add_input_task(task1)
    assert task2.input_task_id_dependency_set == {(task1.ID, BaseTaskDependency.FS)}


def test_initialize():
    """Test initialization/reset of BaseTask."""
    task = BaseTask("task")
    task.est = 2.0
    task.eft = 10.0
    task.lst = 3.0
    task.lft = 11.0
    task.remaining_work_amount = 7
    task.actual_work_amount = 6
    task.state = BaseTaskState.READY
    task.additional_task_flag = True
    task.allocated_worker_facility_id_tuple_set = {(BaseWorker("w1").ID, None)}
    task.initialize()
    assert task.est == 0.0
    assert task.eft == 0.0
    assert task.lst == -1.0
    assert task.lft == -1.0
    assert task.remaining_work_amount == task.default_work_amount * (
        1.0 - task.default_progress
    )
    assert task.actual_work_amount == task.default_work_amount * (
        1.0 - task.default_progress
    )
    assert task.state == BaseTaskState.NONE
    assert task.additional_task_flag is False
    assert task.allocated_worker_facility_id_tuple_set == set()

    task = BaseTask("task", default_progress=0.2)
    task.initialize()
    assert task.state == BaseTaskState.NONE

    task = BaseTask("task", default_progress=1.0)
    task.initialize()
    assert task.state == BaseTaskState.FINISHED


def test_auto_task():
    """Test auto_task property of BaseTask."""
    auto_task_instance = BaseTask("a", auto_task=True)
    assert auto_task_instance.auto_task is True
    assert auto_task_instance.state == BaseTaskState.NONE


def test_get_state_from_record():
    """Test getting state from state record."""
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    assert task1.get_state_from_record(0) == BaseTaskState.NONE
    assert task1.get_state_from_record(1) == BaseTaskState.READY
    assert task1.get_state_from_record(2) == BaseTaskState.WORKING
    assert task1.get_state_from_record(3) == BaseTaskState.FINISHED
    assert task1.get_state_from_record(4) == BaseTaskState.FINISHED


def test_remove_insert_absence_time_list():
    """Test removing and inserting absence time list for BaseTask."""
    w = BaseTask("w1", "----")
    w.remaining_work_amount_record_list = [3, 2, 1, 1, 1, 0]
    aa = BaseWorker("aa")
    bb = BaseWorker("bb")
    cc = BaseWorker("cc")
    dd = BaseWorker("dd")
    ee = BaseWorker("ee")
    ff = BaseWorker("ff")

    w.allocated_worker_facility_id_tuple_set_record_list = [
        (aa.ID, None),
        (bb.ID, None),
        (cc.ID, None),
        (dd.ID, None),
        (ee.ID, None),
        (ff.ID, None),
    ]
    w.state_record_list = [0, 1, 2, 3, 4, 5]

    absence_time_list = [3, 4]
    w.remove_absence_time_list(absence_time_list)
    assert w.allocated_worker_facility_id_tuple_set_record_list == [
        (aa.ID, None),
        (bb.ID, None),
        (cc.ID, None),
        (ff.ID, None),
    ]
    assert w.state_record_list == [0, 1, 2, 5]
    assert w.remaining_work_amount_record_list == [3, 2, 1, 0]

    w.insert_absence_time_list(absence_time_list)
    assert w.allocated_worker_facility_id_tuple_set_record_list == [
        (aa.ID, None),
        (bb.ID, None),
        (cc.ID, None),
        (cc.ID, None),
        (cc.ID, None),
        (ff.ID, None),
    ]
    assert w.state_record_list == [0, 1, 2, 1, 1, 5]
    assert w.remaining_work_amount_record_list == [3, 2, 1, 1, 1, 0]


def test_get_time_list_for_gantt_chart():
    """Test getting time lists for Gantt chart visualization."""
    w = BaseTask("w1", "----")
    w.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(1, 1)]
    assert working_time_list == [(2, 1)]

    w.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.READY,
        BaseTaskState.READY,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(1, 2)]
    assert working_time_list == [(0, 0)]

    w.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(0, 0)]
    assert working_time_list == [(1, 1)]

    # for backward
    w.state_record_list = [
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.READY,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(2, 2), (7, 1)]
    assert working_time_list == [(1, 1), (5, 2)]


@pytest.fixture(name="dummy_task")
def fixture_dummy_task():
    """Fixture for a dummy BaseTask.

    Returns:
        BaseTask: A dummy task instance.
    """
    return BaseTask("dummy_task")


def test_print_mermaid_diagram(dummy_task):
    """Test the print_mermaid_diagram method.

    Args:
        dummy_task (BaseTask): The dummy task fixture.
    """
    dummy_task.print_mermaid_diagram(
        subgraph=True,
    )


def test_get_gantt_mermaid_steps_data(dummy_task):
    """Test the get_gantt_mermaid_steps_data method.

    Args:
        dummy_task (BaseTask): The dummy task fixture.
    """
    dummy_task.state_record_list = [0, 1, 2, 2, -1, -1]
    assert dummy_task.get_gantt_mermaid_steps_data() == [f"{dummy_task.name}:2,4"]
    assert dummy_task.get_gantt_mermaid_steps_data(range_time=(0, 5)) == [
        f"{dummy_task.name}:2,4"
    ]
    assert dummy_task.get_gantt_mermaid_steps_data(range_time=(0, 2)) == [
        f"{dummy_task.name}:2,2"
    ]
    assert dummy_task.get_gantt_mermaid_steps_data(range_time=(3, 5)) == [
        f"{dummy_task.name}:3,4"
    ]
    assert dummy_task.get_gantt_mermaid_steps_data(range_time=(0, 1)) == []
    assert dummy_task.get_gantt_mermaid_steps_data(range_time=(4, 5)) == []
