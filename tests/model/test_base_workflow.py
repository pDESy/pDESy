#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for BaseWorkflow.

This module contains unit tests for the BaseWorkflow class and related functionality.
"""

import datetime
import os

import pytest

from pDESy.model.base_task import BaseTask, BaseTaskDependency, BaseTaskState
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_workflow import BaseWorkflow


@pytest.fixture(name="dummy_workflow")
def fixture_dummy_workflow():
    """Fixture for a dummy BaseWorkflow.

    Returns:
        BaseWorkflow: A dummy workflow instance.
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task4 = BaseTask("task4")
    task5 = BaseTask("task5")
    task3.update_input_task_set({task1, task2})
    task5.add_input_task(task3)
    task5.add_input_task(task4)
    w = BaseWorkflow(task_set={task1, task2, task3, task4, task5})
    return w


@pytest.fixture(name="ss_workflow")
def fixture_ss_workflow():
    """Fixture for a simple workflow including StartToStart dependency.

    Returns:
        BaseWorkflow: A workflow with SS and FS dependencies.
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.add_input_task(task1, task_dependency_mode=BaseTaskDependency.SS)
    task3.add_input_task(task1, task_dependency_mode=BaseTaskDependency.FS)
    task3.add_input_task(task2, task_dependency_mode=BaseTaskDependency.SS)
    return BaseWorkflow(task_set={task1, task2, task3})


@pytest.fixture(name="ff_workflow")
def fixture_ff_workflow():
    """Fixture for a simple workflow including FinishToFinish dependency.

    Returns:
        BaseWorkflow: A workflow with FF, FS, and SS dependencies.
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.add_input_task(task1, task_dependency_mode=BaseTaskDependency.FF)
    task3.add_input_task(task1, task_dependency_mode=BaseTaskDependency.FS)
    task3.add_input_task(task2, task_dependency_mode=BaseTaskDependency.SS)
    return BaseWorkflow(task_set={task1, task2, task3})


@pytest.fixture(name="sf_workflow")
def fixture_sf_workflow():
    """Fixture for a simple workflow including StartToFinish dependency.

    Returns:
        BaseWorkflow: A workflow with SF, FS, and SS dependencies.
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.add_input_task(task1, task_dependency_mode=BaseTaskDependency.SF)
    task3.add_input_task(task1, task_dependency_mode=BaseTaskDependency.FS)
    task3.add_input_task(task2, task_dependency_mode=BaseTaskDependency.SS)
    return BaseWorkflow(task_set={task1, task2, task3})


def test_reverse_dependencies(dummy_workflow):
    """Test reversing dependencies in a workflow.

    Args:
        dummy_workflow (BaseWorkflow): The dummy workflow fixture.
    """
    task1 = next(
        (task for task in dummy_workflow.task_set if task.name == "task1"),
        None,
    )
    task2 = next(
        (task for task in dummy_workflow.task_set if task.name == "task2"),
        None,
    )
    task3 = next(
        (task for task in dummy_workflow.task_set if task.name == "task3"),
        None,
    )
    task4 = next(
        (task for task in dummy_workflow.task_set if task.name == "task4"),
        None,
    )
    task5 = next(
        (task for task in dummy_workflow.task_set if task.name == "task5"),
        None,
    )
    assert task1.input_task_id_dependency_set == set()
    assert task2.input_task_id_dependency_set == set()
    assert task3.input_task_id_dependency_set == {
        (task1.ID, BaseTaskDependency.FS),
        (task2.ID, BaseTaskDependency.FS),
    }
    assert task4.input_task_id_dependency_set == set()
    assert task5.input_task_id_dependency_set == {
        (task3.ID, BaseTaskDependency.FS),
        (task4.ID, BaseTaskDependency.FS),
    }

    dummy_workflow.reverse_dependencies()

    assert task1.input_task_id_dependency_set == {(task3.ID, BaseTaskDependency.FS)}
    assert task2.input_task_id_dependency_set == {(task3.ID, BaseTaskDependency.FS)}
    assert task3.input_task_id_dependency_set == {(task5.ID, BaseTaskDependency.FS)}
    assert task4.input_task_id_dependency_set == {(task5.ID, BaseTaskDependency.FS)}
    assert task5.input_task_id_dependency_set == set()

    dummy_workflow.reverse_dependencies()

    assert task1.input_task_id_dependency_set == set()
    assert task2.input_task_id_dependency_set == set()
    assert task3.input_task_id_dependency_set == {
        (task1.ID, BaseTaskDependency.FS),
        (task2.ID, BaseTaskDependency.FS),
    }
    assert task4.input_task_id_dependency_set == set()
    assert task5.input_task_id_dependency_set == {
        (task3.ID, BaseTaskDependency.FS),
        (task4.ID, BaseTaskDependency.FS),
    }


def test_init():
    """Test initialization of BaseWorkflow."""
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task2.add_input_task(task1)
    w = BaseWorkflow(task_set={task1, task2})
    assert w.task_set == {task1, task2}
    assert w.critical_path_length == 0.0


def test_str():
    """Test string representation of BaseWorkflow."""
    print(BaseWorkflow(task_set=set()))


def test_create_task():
    """Test creating a task from a workflow."""
    w = BaseWorkflow()
    task = w.create_task(name="task1")
    assert task.name == "task1"
    assert w.task_set == {task}
    assert task.parent_workflow_id == w.ID


@pytest.fixture(name="dummy_workflow_for_extracting")
def fixture_dummy_workflow_for_extracting():
    """Fixture for a dummy BaseWorkflow for extracting tests.

    Returns:
        BaseWorkflow: A dummy workflow instance with several tasks.
    """
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task3 = BaseTask("task3")
    task3.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task4 = BaseTask("task4")
    task4.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    task5 = BaseTask("task5")
    task5.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.NONE,
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
    ]
    return BaseWorkflow(task_set={task1, task2, task3, task4, task5})


def test_extract_none_task_set(dummy_workflow_for_extracting):
    """Test extracting tasks in NONE state.

    Args:
        dummy_workflow_for_extracting (BaseWorkflow): The dummy workflow fixture.
    """
    assert len(dummy_workflow_for_extracting.extract_none_task_set([5])) == 0
    assert len(dummy_workflow_for_extracting.extract_none_task_set([0])) == 2
    assert len(dummy_workflow_for_extracting.extract_none_task_set([1])) == 1
    assert len(dummy_workflow_for_extracting.extract_none_task_set([0, 1])) == 1


def test_extract_ready_task_set(dummy_workflow_for_extracting):
    """Test extracting tasks in READY state.

    Args:
        dummy_workflow_for_extracting (BaseWorkflow): The dummy workflow fixture.
    """
    assert len(dummy_workflow_for_extracting.extract_ready_task_set([1])) == 1
    assert len(dummy_workflow_for_extracting.extract_ready_task_set([2, 3])) == 1
    assert len(dummy_workflow_for_extracting.extract_ready_task_set([1, 2, 3])) == 0


def test_extract_working_task_set(dummy_workflow_for_extracting):
    """Test extracting tasks in WORKING state.

    Args:
        dummy_workflow_for_extracting (BaseWorkflow): The dummy workflow fixture.
    """
    assert len(dummy_workflow_for_extracting.extract_working_task_set([0])) == 2
    assert len(dummy_workflow_for_extracting.extract_working_task_set([1, 2])) == 1
    assert len(dummy_workflow_for_extracting.extract_working_task_set([1, 2, 3])) == 0


def test_extract_finished_task_set(dummy_workflow_for_extracting):
    """Test extracting tasks in FINISHED state.

    Args:
        dummy_workflow_for_extracting (BaseWorkflow): The dummy workflow fixture.
    """
    assert len(dummy_workflow_for_extracting.extract_finished_task_set([2, 3])) == 2
    assert len(dummy_workflow_for_extracting.extract_finished_task_set([2, 3, 4])) == 2
    assert len(dummy_workflow_for_extracting.extract_finished_task_set([0])) == 0


def test_get_task_set(dummy_workflow):
    """Test getting a task set with specific parameters.

    Args:
        dummy_workflow (BaseWorkflow): The dummy workflow fixture.
    """
    assert (
        len(
            dummy_workflow.get_task_set(
                name="test",
                ID="test",
                default_work_amount=0,
                input_task_id_dependency_set=set(),
                allocated_team_id_set=[],
                allocated_workplace_id_set=[],
                need_facility=False,
                target_component_id="test",
                default_progress=0.85,
                due_time=99,
                auto_task=False,
                fixing_allocating_worker_id_set=set(),
                fixing_allocating_facility_id_set=set(),
                # search param
                est=1,
                eft=2,
                lst=3,
                lft=4,
                remaining_work_amount=999,
                state=BaseTaskState.READY,
                allocated_worker_facility_id_tuple_set=set(),
                allocated_worker_facility_id_tuple_set_record_list=[],
            )
        )
        == 0
    )


def test_initialize():
    """Test initialization/reset of BaseWorkflow and its tasks."""
    task = BaseTask("task")
    task.est = 2.0
    task.eft = 10.0
    task.lst = 3.0
    task.lft = 11.0
    task.remaining_work_amount = 7
    task.actual_work_amount = 6
    task.state = BaseTaskState.FINISHED
    task.additional_task_flag = True
    task.allocated_worker_facility_id_tuple_set = {(BaseWorker("w1").ID, None)}

    task_after1 = BaseTask("task_after1")
    task_after2 = BaseTask("task_after2", default_work_amount=5.0)
    task_after1.add_input_task(task)
    task_after2.add_input_task(task)

    w = BaseWorkflow(task_set={task, task_after1, task_after2})
    w.critical_path_length = 100.0
    w.initialize()
    assert w.critical_path_length == 20.0
    assert task.est == 0.0
    assert task.eft == 10.0
    assert task.lst == 0.0
    assert task.lft == 10.0
    assert task.state == BaseTaskState.NONE
    assert task_after1.est == 10.0
    assert task_after1.eft == 20.0
    assert task_after1.lst == 10.0
    assert task_after1.lft == 20.0
    assert task_after1.state == BaseTaskState.NONE
    assert task_after2.est == 10.0
    assert task_after2.eft == 15.0
    assert task_after2.lst == 15.0
    assert task_after2.lft == 20.0
    assert task_after2.state == BaseTaskState.NONE


def test_update_pert_data(ss_workflow, ff_workflow, sf_workflow):
    """Test updating PERT data for different dependency types.

    Args:
        ss_workflow (BaseWorkflow): Workflow with SS dependency.
        ff_workflow (BaseWorkflow): Workflow with FF dependency.
        sf_workflow (BaseWorkflow): Workflow with SF dependency.
    """
    ss_workflow.update_pert_data(0)
    task1 = next(
        (task for task in ss_workflow.task_set if task.name == "task1"),
        None,
    )
    task2 = next(
        (task for task in ss_workflow.task_set if task.name == "task2"),
        None,
    )
    task3 = next(
        (task for task in ss_workflow.task_set if task.name == "task3"),
        None,
    )
    assert (task1.est, task1.eft) == (0, 10)
    assert (task2.est, task2.eft) == (0, 10)
    assert (task3.est, task3.eft) == (10, 20)
    assert (task1.lst, task1.lft) == (0, 10)
    assert (task2.lst, task2.lft) == (10, 20)
    assert (task3.lst, task3.lft) == (10, 20)

    ff_workflow.update_pert_data(0)
    task1 = next(
        (task for task in ff_workflow.task_set if task.name == "task1"),
        None,
    )
    task2 = next(
        (task for task in ff_workflow.task_set if task.name == "task2"),
        None,
    )
    task3 = next(
        (task for task in ff_workflow.task_set if task.name == "task3"),
        None,
    )
    assert (task1.est, task1.eft) == (0, 10)
    assert (task2.est, task2.eft) == (0, 10)
    assert (task3.est, task3.eft) == (10, 20)
    assert (task1.lst, task1.lft) == (0, 10)
    assert (task2.lst, task2.lft) == (10, 20)
    assert (task3.lst, task3.lft) == (10, 20)

    sf_workflow.update_pert_data(0)
    task1 = next(
        (task for task in sf_workflow.task_set if task.name == "task1"),
        None,
    )
    task2 = next(
        (task for task in sf_workflow.task_set if task.name == "task2"),
        None,
    )
    task3 = next(
        (task for task in sf_workflow.task_set if task.name == "task3"),
        None,
    )
    assert (task1.est, task1.eft) == (0, 10)
    assert (task2.est, task2.eft) == (0, 10)
    assert (task3.est, task3.eft) == (10, 20)
    assert (task1.lst, task1.lft) == (0, 10)
    assert (task2.lst, task2.lft) == (10, 20)
    assert (task3.lst, task3.lft) == (10, 20)




def test_remove_insert_absence_time_list():
    """Test removing and inserting absence time list for BaseWorkflow and its tasks."""
    w1 = BaseTask("w1", "----")
    w1.remaining_work_amount_record_list = [3, 2, 1, 1, 1, 0]
    aa = BaseWorker("aa")
    bb = BaseWorker("bb")
    cc = BaseWorker("cc")
    dd = BaseWorker("dd")
    ee = BaseWorker("ee")
    ff = BaseWorker("ff")
    w1.allocated_worker_facility_id_tuple_set_record_list = [
        (aa.ID, "facility1"),
        (bb.ID, "facility2"),
        (cc.ID, "facility3"),
        (dd.ID, "facility4"),
        (ee.ID, "facility5"),
        (ff.ID, "facility6"),
    ]
    w1.state_record_list = [0, 1, 2, 3, 4, 5]

    w2 = BaseTask("w2", "----")
    w2.remaining_work_amount_record_list = [3, 2, 1, 1, 1, 0]
    w2.allocated_worker_facility_id_tuple_set_record_list = [
        (aa.ID, "facility1"),
        (bb.ID, "facility2"),
        (cc.ID, "facility3"),
        (dd.ID, "facility4"),
        (ee.ID, "facility5"),
        (ff.ID, "facility6"),
    ]
    w2.state_record_list = [0, 1, 2, 3, 4, 5]
    w2.add_input_task(w1)

    workflow = BaseWorkflow(task_set={w1, w2})

    absence_time_list = [3, 4]
    workflow.remove_absence_time_list(absence_time_list)
    assert w1.allocated_worker_facility_id_tuple_set_record_list == [
        (aa.ID, "facility1"),
        (bb.ID, "facility2"),
        (cc.ID, "facility3"),
        (ff.ID, "facility6"),
    ]
    assert w1.state_record_list == [0, 1, 2, 5]
    assert w1.remaining_work_amount_record_list == [3, 2, 1, 0]
    assert w2.allocated_worker_facility_id_tuple_set_record_list == [
        (aa.ID, "facility1"),
        (bb.ID, "facility2"),
        (cc.ID, "facility3"),
        (ff.ID, "facility6"),
    ]
    assert w2.state_record_list == [0, 1, 2, 5]
    assert w2.remaining_work_amount_record_list == [3, 2, 1, 0]

    workflow.insert_absence_time_list(absence_time_list)
    assert w1.allocated_worker_facility_id_tuple_set_record_list == [
        (aa.ID, "facility1"),
        (bb.ID, "facility2"),
        (cc.ID, "facility3"),
        (cc.ID, "facility3"),
        (cc.ID, "facility3"),
        (ff.ID, "facility6"),
    ]
    assert w1.state_record_list == [0, 1, 2, 1, 1, 5]
    assert w1.remaining_work_amount_record_list == [3, 2, 1, 1, 1, 0]
    assert w2.allocated_worker_facility_id_tuple_set_record_list == [
        (aa.ID, "facility1"),
        (bb.ID, "facility2"),
        (cc.ID, "facility3"),
        (cc.ID, "facility3"),
        (cc.ID, "facility3"),
        (ff.ID, "facility6"),
    ]
    assert w2.state_record_list == [0, 1, 2, 1, 1, 5]
    assert w2.remaining_work_amount_record_list == [3, 2, 1, 1, 1, 0]


def test_print_mermaid_diagram(dummy_workflow):
    """Test printing Mermaid diagrams.

    Args:
        dummy_workflow (BaseWorkflow): The dummy workflow fixture.
    """
    dummy_workflow.print_mermaid_diagram(
        orientations="LR",
        print_work_amount_info=True,
        print_dependency_type=False,
    )
    dummy_workflow.print_target_task_mermaid_diagram(
        target_task_set=[
            list(dummy_workflow.task_set)[0],
            list(dummy_workflow.task_set)[2],
            list(dummy_workflow.task_set)[3],
        ],
        orientations="LR",
        print_work_amount_info=False,
        print_dependency_type=True,
        subgraph=True,
    )


def test_print_gantt_mermaid(dummy_workflow):
    """Test printing Gantt Mermaid diagrams.

    Args:
        dummy_workflow (BaseWorkflow): The dummy workflow fixture.
    """
    dummy_workflow.print_gantt_mermaid(
        project_init_datetime=datetime.datetime(2024, 1, 1),
        project_unit_timedelta=datetime.timedelta(days=1),
        target_id_order_list=[task.ID for task in dummy_workflow.task_set]
    )
