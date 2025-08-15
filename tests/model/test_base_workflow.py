#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_base_workflow."""

import datetime
import os

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility
from pDESy.model.base_task import BaseTask, BaseTaskDependency, BaseTaskState
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_workflow import BaseWorkflow

import pytest


@pytest.fixture
def dummy_workflow(scope="function"):
    """dummy_workflow."""
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task4 = BaseTask("task4")
    task5 = BaseTask("task5")
    task3.extend_input_task_list([task1, task2])
    task5.append_input_task_dependency(task3)
    task5.append_input_task_dependency(task4)
    w = BaseWorkflow(task_list=[task1, task2, task3, task4, task5])
    return w


@pytest.fixture
def SS_workflow(scope="function"):
    """SS_workflow.

    Simple workflow including StartToStart dependency.
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.append_input_task_dependency(
        task1, task_dependency_mode=BaseTaskDependency.SS
    )
    task3.append_input_task_dependency(
        task1, task_dependency_mode=BaseTaskDependency.FS
    )
    task3.append_input_task_dependency(
        task2, task_dependency_mode=BaseTaskDependency.SS
    )
    return BaseWorkflow(task_list=[task1, task2, task3])


@pytest.fixture
def FF_workflow(scope="function"):
    """FF_workflow.

    Simple workflow including FinishToFinish dependency.
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.append_input_task_dependency(
        task1, task_dependency_mode=BaseTaskDependency.FF
    )
    task3.append_input_task_dependency(
        task1, task_dependency_mode=BaseTaskDependency.FS
    )
    task3.append_input_task_dependency(
        task2, task_dependency_mode=BaseTaskDependency.SS
    )
    return BaseWorkflow(task_list=[task1, task2, task3])


@pytest.fixture
def SF_workflow(scope="function"):
    """SF_workflow.

    Simple workflow including StartToFinish dependency.
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.append_input_task_dependency(
        task1, task_dependency_mode=BaseTaskDependency.SF
    )
    task3.append_input_task_dependency(
        task1, task_dependency_mode=BaseTaskDependency.FS
    )
    task3.append_input_task_dependency(
        task2, task_dependency_mode=BaseTaskDependency.SS
    )
    return BaseWorkflow(task_list=[task1, task2, task3])


def test_reverse_dependencies(dummy_workflow):
    """test_reverse_dependencies."""
    assert dummy_workflow.task_list[0].input_task_id_dependency_list == []
    assert dummy_workflow.task_list[1].input_task_id_dependency_list == []
    assert dummy_workflow.task_list[2].input_task_id_dependency_list == [
        [dummy_workflow.task_list[0].ID, BaseTaskDependency.FS],
        [dummy_workflow.task_list[1].ID, BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[3].input_task_id_dependency_list == []
    assert dummy_workflow.task_list[4].input_task_id_dependency_list == [
        [dummy_workflow.task_list[2].ID, BaseTaskDependency.FS],
        [dummy_workflow.task_list[3].ID, BaseTaskDependency.FS],
    ]

    dummy_workflow.reverse_dependencies()

    assert dummy_workflow.task_list[0].input_task_id_dependency_list == [
        [dummy_workflow.task_list[2].ID, BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[1].input_task_id_dependency_list == [
        [dummy_workflow.task_list[2].ID, BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[2].input_task_id_dependency_list == [
        [dummy_workflow.task_list[4].ID, BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[3].input_task_id_dependency_list == [
        [dummy_workflow.task_list[4].ID, BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[4].input_task_id_dependency_list == []

    dummy_workflow.reverse_dependencies()

    assert dummy_workflow.task_list[0].input_task_id_dependency_list == []
    assert dummy_workflow.task_list[1].input_task_id_dependency_list == []
    assert dummy_workflow.task_list[2].input_task_id_dependency_list == [
        [dummy_workflow.task_list[0].ID, BaseTaskDependency.FS],
        [dummy_workflow.task_list[1].ID, BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[3].input_task_id_dependency_list == []
    assert dummy_workflow.task_list[4].input_task_id_dependency_list == [
        [dummy_workflow.task_list[2].ID, BaseTaskDependency.FS],
        [dummy_workflow.task_list[3].ID, BaseTaskDependency.FS],
    ]


def test_init():
    """test_init."""
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task2.append_input_task_dependency(task1)
    w = BaseWorkflow(task_list=[task1, task2])
    assert w.task_list == [task1, task2]
    assert w.critical_path_length == 0.0


def test_str():
    """test_str."""
    print(BaseWorkflow(task_list=[]))


@pytest.fixture
def dummy_workflow_for_extracting(scope="function"):
    """dummy_workflow_for_extracting."""
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
    return BaseWorkflow(task_list=[task1, task2, task3, task4, task5])


def test_extract_none_task_list(dummy_workflow_for_extracting):
    """test_extract_none_task_list."""
    assert len(dummy_workflow_for_extracting.extract_none_task_list([5])) == 0
    assert len(dummy_workflow_for_extracting.extract_none_task_list([0])) == 2
    assert len(dummy_workflow_for_extracting.extract_none_task_list([1])) == 1
    assert len(dummy_workflow_for_extracting.extract_none_task_list([0, 1])) == 1


def test_extract_ready_task_list(dummy_workflow_for_extracting):
    """test_extract_ready_task_list."""
    assert len(dummy_workflow_for_extracting.extract_ready_task_list([1])) == 1
    assert len(dummy_workflow_for_extracting.extract_ready_task_list([2, 3])) == 1
    assert len(dummy_workflow_for_extracting.extract_ready_task_list([1, 2, 3])) == 0


def test_extract_working_task_list(dummy_workflow_for_extracting):
    """test_extract_working_task_list."""
    assert len(dummy_workflow_for_extracting.extract_working_task_list([0])) == 2
    assert len(dummy_workflow_for_extracting.extract_working_task_list([1, 2])) == 1
    assert len(dummy_workflow_for_extracting.extract_working_task_list([1, 2, 3])) == 0


def test_extract_finished_task_list(dummy_workflow_for_extracting):
    """test_extract_finished_task_list."""
    assert len(dummy_workflow_for_extracting.extract_finished_task_list([2, 3])) == 2
    assert len(dummy_workflow_for_extracting.extract_finished_task_list([2, 3, 4])) == 2
    assert len(dummy_workflow_for_extracting.extract_finished_task_list([0])) == 0


def test_get_task_list(dummy_workflow):
    """test_get_task_list."""
    # TODO if we have enough time for setting test case...
    assert (
        len(
            dummy_workflow.get_task_list(
                name="test",
                ID="test",
                default_work_amount=0,
                input_task_id_dependency_list=[],
                allocated_team_id_list=[],
                allocated_workplace_id_list=[],
                need_facility=False,
                target_component_id="test",
                default_progress=0.85,
                due_time=99,
                auto_task=False,
                fixing_allocating_worker_id_list=[],
                fixing_allocating_facility_id_list=[],
                # search param
                est=1,
                eft=2,
                lst=3,
                lft=4,
                remaining_work_amount=999,
                state=BaseTaskState.READY,
                allocated_worker_list=[],
                allocated_worker_id_record=[],
                allocated_facility_list=[],
                allocated_facility_id_record=[],
            )
        )
        == 0
    )


def test_initialize():
    """test_initialize."""
    task = BaseTask("task")
    task.est = 2.0
    task.eft = 10.0
    task.lst = 3.0
    task.lft = 11.0
    task.remaining_work_amount = 7
    task.actual_work_amount = 6
    task.state = BaseTaskState.FINISHED
    task.additional_task_flag = True
    task.allocated_worker_list = [BaseWorker("w1")]

    task_after1 = BaseTask("task_after1")
    task_after2 = BaseTask("task_after2", default_work_amount=5.0)
    task_after1.append_input_task_dependency(task)
    task_after2.append_input_task_dependency(task)

    w = BaseWorkflow(task_list=[task, task_after1, task_after2])
    w.critical_path_length = 100.0
    w.initialize()
    assert w.critical_path_length == 20.0
    assert w.task_list[0].est == 0.0
    assert w.task_list[0].eft == 10.0
    assert w.task_list[0].lst == 0.0
    assert w.task_list[0].lft == 10.0
    assert w.task_list[0].state == BaseTaskState.READY
    assert w.task_list[1].est == 10.0
    assert w.task_list[1].eft == 20.0
    assert w.task_list[1].lst == 10.0
    assert w.task_list[1].lft == 20.0
    assert w.task_list[1].state == BaseTaskState.NONE
    assert w.task_list[2].est == 10.0
    assert w.task_list[2].eft == 15.0
    assert w.task_list[2].lst == 15.0
    assert w.task_list[2].lft == 20.0
    assert w.task_list[2].state == BaseTaskState.NONE


def test_update_PERT_data(SS_workflow, FF_workflow, SF_workflow):
    """test_update_PERT_data."""
    SS_workflow.update_PERT_data(0)
    assert (SS_workflow.task_list[0].est, SS_workflow.task_list[0].eft) == (0, 10)
    assert (SS_workflow.task_list[1].est, SS_workflow.task_list[1].eft) == (0, 10)
    assert (SS_workflow.task_list[2].est, SS_workflow.task_list[2].eft) == (10, 20)
    assert (SS_workflow.task_list[0].lst, SS_workflow.task_list[0].lft) == (0, 10)
    assert (SS_workflow.task_list[1].lst, SS_workflow.task_list[1].lft) == (10, 20)
    assert (SS_workflow.task_list[2].lst, SS_workflow.task_list[2].lft) == (10, 20)

    FF_workflow.update_PERT_data(0)
    assert (FF_workflow.task_list[0].est, FF_workflow.task_list[0].eft) == (0, 10)
    assert (FF_workflow.task_list[1].est, FF_workflow.task_list[1].eft) == (0, 10)
    assert (FF_workflow.task_list[2].est, FF_workflow.task_list[2].eft) == (10, 20)
    assert (FF_workflow.task_list[0].lst, FF_workflow.task_list[0].lft) == (0, 10)
    assert (FF_workflow.task_list[1].lst, FF_workflow.task_list[1].lft) == (10, 20)
    assert (FF_workflow.task_list[2].lst, FF_workflow.task_list[2].lft) == (10, 20)

    SF_workflow.update_PERT_data(0)
    assert (SF_workflow.task_list[0].est, SF_workflow.task_list[0].eft) == (0, 10)
    assert (SF_workflow.task_list[1].est, SF_workflow.task_list[1].eft) == (0, 10)
    assert (SF_workflow.task_list[2].est, SF_workflow.task_list[2].eft) == (10, 20)
    assert (SF_workflow.task_list[0].lst, SF_workflow.task_list[0].lft) == (0, 10)
    assert (SF_workflow.task_list[1].lst, SF_workflow.task_list[1].lft) == (10, 20)
    assert (SF_workflow.task_list[2].lst, SF_workflow.task_list[2].lft) == (10, 20)


def test_check_state():
    """test_check_state."""
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task4 = BaseTask("task4")
    task5 = BaseTask("task5")
    task3.append_input_task_dependency(task1)
    task3.append_input_task_dependency(task2)
    task5.append_input_task_dependency(task3)
    task5.append_input_task_dependency(task4)
    w = BaseWorkflow(task_list=[task1, task2, task3, task4, task5])

    w1 = BaseWorker("w1", assigned_task_list=[task1])

    # __check_ready test
    task1.state = BaseTaskState.FINISHED
    task2.state = BaseTaskState.FINISHED
    task3.state = BaseTaskState.NONE
    task4.state = BaseTaskState.NONE
    task5.state = BaseTaskState.NONE
    w.check_state(2, BaseTaskState.READY)
    assert task1.state == BaseTaskState.FINISHED
    assert task2.state == BaseTaskState.FINISHED
    assert task3.state == BaseTaskState.READY
    assert task4.state == BaseTaskState.READY
    assert task5.state == BaseTaskState.NONE

    # __check_working test
    task1.state = BaseTaskState.READY
    task2.state = BaseTaskState.READY
    task2.allocated_worker_list = [w1]
    task3.state = BaseTaskState.NONE
    task4.state = BaseTaskState.NONE
    task5.state = BaseTaskState.NONE
    w.check_state(2, BaseTaskState.WORKING)
    assert task1.state == BaseTaskState.READY
    assert task2.state == BaseTaskState.WORKING
    assert task3.state == BaseTaskState.NONE
    assert task4.state == BaseTaskState.NONE
    assert task5.state == BaseTaskState.NONE

    task1.state = BaseTaskState.WORKING
    task1.need_facility = True
    w2 = BaseWorker("w2", assigned_task_list=[task1])
    f2 = BaseFacility("f2", assigned_task_list=[task1])
    task1.allocated_worker_list = [w2]
    task1.allocated_facility_list = [f2]
    w.check_state(2, BaseTaskState.WORKING)

    # __check_finished test
    task1.state = BaseTaskState.WORKING
    task1.allocated_worker_list = [w1]
    task1.remaining_work_amount = 0.0
    task2.state = BaseTaskState.FINISHED
    task3.state = BaseTaskState.NONE
    task4.state = BaseTaskState.NONE
    task5.state = BaseTaskState.NONE
    w.check_state(2, BaseTaskState.FINISHED)
    assert task1.state == BaseTaskState.FINISHED
    assert task2.state == BaseTaskState.FINISHED
    assert task3.state == BaseTaskState.NONE
    assert task4.state == BaseTaskState.NONE
    assert task5.state == BaseTaskState.NONE


def test___check_ready(SS_workflow, SF_workflow, FF_workflow):
    """test___check_ready."""
    # For SS_workflow
    SS_workflow.check_state(-1, BaseTaskState.READY)
    assert SS_workflow.task_list[0].state == BaseTaskState.READY
    assert SS_workflow.task_list[1].state == BaseTaskState.NONE
    assert SS_workflow.task_list[2].state == BaseTaskState.NONE
    SS_workflow.task_list[0].state = BaseTaskState.WORKING
    SS_workflow.check_state(0, BaseTaskState.READY)
    assert SS_workflow.task_list[0].state == BaseTaskState.WORKING
    assert SS_workflow.task_list[1].state == BaseTaskState.READY
    assert SS_workflow.task_list[2].state == BaseTaskState.NONE
    SS_workflow.task_list[1].state = BaseTaskState.WORKING
    SS_workflow.check_state(1, BaseTaskState.READY)
    assert SS_workflow.task_list[0].state == BaseTaskState.WORKING
    assert SS_workflow.task_list[1].state == BaseTaskState.WORKING
    assert SS_workflow.task_list[2].state == BaseTaskState.NONE
    SS_workflow.task_list[0].state = BaseTaskState.FINISHED
    SS_workflow.check_state(2, BaseTaskState.READY)
    assert SS_workflow.task_list[0].state == BaseTaskState.FINISHED
    assert SS_workflow.task_list[1].state == BaseTaskState.WORKING
    assert SS_workflow.task_list[2].state == BaseTaskState.READY

    # For FF_workflow
    FF_workflow.check_state(-1, BaseTaskState.READY)
    assert FF_workflow.task_list[0].state == BaseTaskState.READY
    assert FF_workflow.task_list[1].state == BaseTaskState.READY
    assert FF_workflow.task_list[2].state == BaseTaskState.NONE

    # For SF_workflow
    SF_workflow.check_state(-1, BaseTaskState.READY)
    assert SF_workflow.task_list[0].state == BaseTaskState.READY
    assert SF_workflow.task_list[1].state == BaseTaskState.READY
    assert SF_workflow.task_list[2].state == BaseTaskState.NONE


def test___check_working():
    """test___check_working."""
    # this method is tested in test_check_state()
    pass


def test___check_finished(SF_workflow, FF_workflow):
    """test___check_finished."""
    # For SF_workflow
    SF_workflow.check_state(-1, BaseTaskState.READY)
    assert SF_workflow.task_list[0].state == BaseTaskState.READY
    assert SF_workflow.task_list[1].state == BaseTaskState.READY
    assert SF_workflow.task_list[2].state == BaseTaskState.NONE
    SF_workflow.task_list[1].state = BaseTaskState.WORKING
    SF_workflow.task_list[1].remaining_work_amount = 0
    SF_workflow.check_state(0, BaseTaskState.FINISHED)
    assert SF_workflow.task_list[0].state == BaseTaskState.READY
    assert SF_workflow.task_list[1].state == BaseTaskState.WORKING
    assert SF_workflow.task_list[2].state == BaseTaskState.NONE
    SF_workflow.task_list[0].state = BaseTaskState.WORKING
    SF_workflow.check_state(0, BaseTaskState.FINISHED)
    assert SF_workflow.task_list[0].state == BaseTaskState.WORKING
    assert SF_workflow.task_list[1].state == BaseTaskState.FINISHED
    assert SF_workflow.task_list[2].state == BaseTaskState.NONE

    # For FF_workflow
    FF_workflow.check_state(-1, BaseTaskState.READY)
    FF_workflow.task_list[1].state = BaseTaskState.WORKING
    FF_workflow.task_list[1].remaining_work_amount = 0
    FF_workflow.check_state(0, BaseTaskState.FINISHED)
    assert FF_workflow.task_list[0].state == BaseTaskState.READY
    assert FF_workflow.task_list[1].state == BaseTaskState.WORKING
    assert FF_workflow.task_list[2].state == BaseTaskState.NONE
    FF_workflow.task_list[0].state = BaseTaskState.WORKING
    FF_workflow.check_state(1, BaseTaskState.FINISHED)
    assert FF_workflow.task_list[0].state == BaseTaskState.WORKING
    assert FF_workflow.task_list[1].state == BaseTaskState.WORKING
    assert FF_workflow.task_list[2].state == BaseTaskState.NONE
    FF_workflow.task_list[0].remaining_work_amount = 0
    FF_workflow.check_state(2, BaseTaskState.FINISHED)
    assert FF_workflow.task_list[0].state == BaseTaskState.FINISHED
    assert FF_workflow.task_list[2].state == BaseTaskState.NONE


def test___set_est_eft_data():
    """test___set_est_eft_data."""
    # this method is tested in test_initialize()
    pass


def test___set_lst_lft_criticalpath_data():
    """test___set_lst_lft_criticalpath_data."""
    # this method is tested in test_initialize()
    pass


def test_plot_simple_gantt(tmpdir):
    """test_plot_simple_gantt."""
    task0 = BaseTask("auto", auto_task=True)
    task0.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    w = BaseWorkflow(task_list=[task1, task2, task0])
    w.plot_simple_gantt(finish_margin=1.0, view_auto_task=True, view_ready=False)
    for ext in ["png"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        w.plot_simple_gantt(
            view_ready=True, view_auto_task=True, save_fig_path=save_fig_path
        )


def test_create_data_for_gantt_plotly():
    """test_create_data_for_gantt_plotly."""
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task_dependency(task1)
    w = BaseWorkflow(task_list=[task1, task2])
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    w.create_data_for_gantt_plotly(init_datetime, timedelta, view_ready=True)


def test_create_gantt_plotly(tmpdir):
    """test_create_gantt_plotly."""
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task_dependency(task1)
    w = BaseWorkflow(task_list=[task1, task2])
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        w.create_gantt_plotly(init_datetime, timedelta, save_fig_path=save_fig_path)


def test_get_networkx_graph():
    """test_get_networkx_graph."""
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task_dependency(task1)
    w = BaseWorkflow(task_list=[task1, task2])
    w.get_networkx_graph()


def test_draw_networkx(tmpdir):
    """test_draw_networkx."""
    task0 = BaseTask("auto", auto_task=True)
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task_dependency(task1)
    w = BaseWorkflow(task_list=[task1, task2, task0])
    for ext in ["png"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        w.draw_networkx(save_fig_path=save_fig_path)


def test_get_node_and_edge_trace_for_plotly_network():
    """test_get_node_and_edge_trace_for_plotly_network."""
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task_dependency(task1)
    w = BaseWorkflow(task_list=[task1, task2])
    (
        task_node_trace,
        auto_task_node_trace,
        edge_trace,
    ) = w.get_node_and_edge_trace_for_plotly_network()
    (
        task_node_trace,
        auto_task_node_trace,
        edge_trace,
    ) = w.get_node_and_edge_trace_for_plotly_network()


def test_draw_plotly_network(tmpdir):
    """test_draw_plotly_network."""
    task0 = BaseTask("auto", auto_task=True)
    task1 = BaseTask("task1")
    task1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2 = BaseTask("task2")
    task2.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]
    task2.append_input_task_dependency(task1)
    w = BaseWorkflow(task_list=[task1, task2, task0])
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        w.draw_plotly_network(save_fig_path=save_fig_path)


def test_remove_insert_absence_time_list():
    """test_remove_insert_absence_time_list."""
    w1 = BaseTask("w1", "----")
    w1.remaining_work_amount_record_list = [3, 2, 1, 1, 1, 0]
    w1.allocated_worker_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w1.allocated_facility_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w1.state_record_list = [0, 1, 2, 3, 4, 5]

    w2 = BaseTask("w2", "----")
    w2.remaining_work_amount_record_list = [3, 2, 1, 1, 1, 0]
    w2.allocated_worker_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w2.allocated_facility_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w2.state_record_list = [0, 1, 2, 3, 4, 5]
    w2.append_input_task_dependency(w1)

    workflow = BaseWorkflow(task_list=[w1, w2])

    absence_time_list = [3, 4]
    workflow.remove_absence_time_list(absence_time_list)
    assert w1.allocated_worker_id_record == ["aa", "bb", "cc", "ff"]
    assert w1.allocated_facility_id_record == ["aa", "bb", "cc", "ff"]
    assert w1.state_record_list == [0, 1, 2, 5]
    assert w1.remaining_work_amount_record_list == [3, 2, 1, 0]
    assert w2.allocated_worker_id_record == ["aa", "bb", "cc", "ff"]
    assert w2.allocated_facility_id_record == ["aa", "bb", "cc", "ff"]
    assert w2.state_record_list == [0, 1, 2, 5]
    assert w2.remaining_work_amount_record_list == [3, 2, 1, 0]

    workflow.insert_absence_time_list(absence_time_list)
    assert w1.allocated_worker_id_record == ["aa", "bb", "cc", "cc", "cc", "ff"]
    assert w1.allocated_facility_id_record == ["aa", "bb", "cc", "cc", "cc", "ff"]
    assert w1.state_record_list == [0, 1, 2, 1, 1, 5]
    assert w1.remaining_work_amount_record_list == [3, 2, 1, 1, 1, 0]
    assert w2.allocated_worker_id_record == ["aa", "bb", "cc", "cc", "cc", "ff"]
    assert w2.allocated_facility_id_record == ["aa", "bb", "cc", "cc", "cc", "ff"]
    assert w2.state_record_list == [0, 1, 2, 1, 1, 5]
    assert w2.remaining_work_amount_record_list == [3, 2, 1, 1, 1, 0]


def test_print_mermaid_diagram(dummy_workflow):
    """test_print_mermaid_diagram."""
    dummy_workflow.print_mermaid_diagram(
        orientations="LR",
        print_work_amount_info=True,
        print_dependency_type=False,
    )
    dummy_workflow.print_target_task_mermaid_diagram(
        target_task_list=[
            dummy_workflow.task_list[0],
            dummy_workflow.task_list[2],
            dummy_workflow.task_list[3],
        ],
        orientations="LR",
        print_work_amount_info=False,
        print_dependency_type=True,
        subgraph=True,
    )


def test_print_gantt_mermaid(dummy_workflow):
    """test_print_gantt_mermaid."""
    dummy_workflow.print_gantt_mermaid()
