#!/usr/bin/python
# -*- coding: utf-8 -*-


from pDESy.model.base_task import BaseTask
import datetime
from pDESy.model.base_workflow import BaseWorkflow
from pDESy.model.base_task import BaseTaskState, BaseTaskDependency
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_facility import BaseFacility
from pDESy.model.base_component import BaseComponent
import os

import pytest


@pytest.fixture
def dummy_workflow(scope="function"):
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task4 = BaseTask("task4")
    task5 = BaseTask("task5")
    task3.extend_input_task_list([task1, task2])
    task5.extend_input_task_list([task3, task4])
    w = BaseWorkflow([task1, task2, task3, task4, task5])
    return w


@pytest.fixture
def SS_workflow(scope="function"):
    """
    Simple workflow including StartToStart dependency
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.append_input_task(task1, task_dependency_mode=BaseTaskDependency.SS)
    task3.append_input_task(task1, task_dependency_mode=BaseTaskDependency.FS)
    task3.append_input_task(task2, task_dependency_mode=BaseTaskDependency.SS)
    return BaseWorkflow([task1, task2, task3])


@pytest.fixture
def FF_workflow(scope="function"):
    """
    Simple workflow including FinishToFinish dependency
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.append_input_task(task1, task_dependency_mode=BaseTaskDependency.FF)
    task3.append_input_task(task1, task_dependency_mode=BaseTaskDependency.FS)
    task3.append_input_task(task2, task_dependency_mode=BaseTaskDependency.SS)
    return BaseWorkflow([task1, task2, task3])


@pytest.fixture
def SF_workflow(scope="function"):
    """
    Simple workflow including StartToFinish dependency
    """
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task2.append_input_task(task1, task_dependency_mode=BaseTaskDependency.SF)
    task3.append_input_task(task1, task_dependency_mode=BaseTaskDependency.FS)
    task3.append_input_task(task2, task_dependency_mode=BaseTaskDependency.SS)
    return BaseWorkflow([task1, task2, task3])


def test_reverse_dependencies(dummy_workflow):
    assert dummy_workflow.task_list[0].input_task_list == []
    assert dummy_workflow.task_list[0].output_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[1].input_task_list == []
    assert dummy_workflow.task_list[1].output_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[2].input_task_list == [
        [dummy_workflow.task_list[0], BaseTaskDependency.FS],
        [dummy_workflow.task_list[1], BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[2].output_task_list == [
        [dummy_workflow.task_list[4], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[3].input_task_list == []
    assert dummy_workflow.task_list[3].output_task_list == [
        [dummy_workflow.task_list[4], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[4].input_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS],
        [dummy_workflow.task_list[3], BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[4].output_task_list == []

    dummy_workflow.reverse_dependencies()

    assert dummy_workflow.task_list[0].output_task_list == []
    assert dummy_workflow.task_list[0].input_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[1].output_task_list == []
    assert dummy_workflow.task_list[1].input_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[2].output_task_list == [
        [dummy_workflow.task_list[0], BaseTaskDependency.FS],
        [dummy_workflow.task_list[1], BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[2].input_task_list == [
        [dummy_workflow.task_list[4], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[3].output_task_list == []
    assert dummy_workflow.task_list[3].input_task_list == [
        [dummy_workflow.task_list[4], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[4].output_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS],
        [dummy_workflow.task_list[3], BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[4].input_task_list == []

    dummy_workflow.reverse_dependencies()

    assert dummy_workflow.task_list[0].input_task_list == []
    assert dummy_workflow.task_list[0].output_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[1].input_task_list == []
    assert dummy_workflow.task_list[1].output_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[2].input_task_list == [
        [dummy_workflow.task_list[0], BaseTaskDependency.FS],
        [dummy_workflow.task_list[1], BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[2].output_task_list == [
        [dummy_workflow.task_list[4], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[3].input_task_list == []
    assert dummy_workflow.task_list[3].output_task_list == [
        [dummy_workflow.task_list[4], BaseTaskDependency.FS]
    ]
    assert dummy_workflow.task_list[4].input_task_list == [
        [dummy_workflow.task_list[2], BaseTaskDependency.FS],
        [dummy_workflow.task_list[3], BaseTaskDependency.FS],
    ]
    assert dummy_workflow.task_list[4].output_task_list == []


def test_init():
    task1 = BaseTask("task1")
    task1.start_time_list = [1]
    task1.ready_time_list = [0]
    task1.finish_time_list = [3]
    task2 = BaseTask("task2")
    task2.start_time_list = [4]
    task2.ready_time_list = [4]
    task2.finish_time_list = [6]
    task2.append_input_task(task1)
    w = BaseWorkflow([task1, task2])
    assert w.task_list == [task1, task2]
    assert w.critical_path_length == 0.0


def test_str():
    print(BaseWorkflow([]))


@pytest.fixture
def dummy_workflow_for_extracting(scope="function"):
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
    return BaseWorkflow([task1, task2, task3, task4, task5])


def test_extract_none_task_list(dummy_workflow_for_extracting):
    assert len(dummy_workflow_for_extracting.extract_none_task_list([5])) == 0
    assert len(dummy_workflow_for_extracting.extract_none_task_list([0])) == 2
    assert len(dummy_workflow_for_extracting.extract_none_task_list([1])) == 1
    assert len(dummy_workflow_for_extracting.extract_none_task_list([0, 1])) == 1


def test_extract_ready_task_list(dummy_workflow_for_extracting):
    assert len(dummy_workflow_for_extracting.extract_ready_task_list([1])) == 1
    assert len(dummy_workflow_for_extracting.extract_ready_task_list([2, 3])) == 1
    assert len(dummy_workflow_for_extracting.extract_ready_task_list([1, 2, 3])) == 0


def test_extract_working_task_list(dummy_workflow_for_extracting):
    assert len(dummy_workflow_for_extracting.extract_working_task_list([0])) == 2
    assert len(dummy_workflow_for_extracting.extract_working_task_list([1, 2])) == 1
    assert len(dummy_workflow_for_extracting.extract_working_task_list([1, 2, 3])) == 0


def test_extract_finished_task_list(dummy_workflow_for_extracting):
    assert len(dummy_workflow_for_extracting.extract_finished_task_list([2, 3])) == 2
    assert len(dummy_workflow_for_extracting.extract_finished_task_list([2, 3, 4])) == 2
    assert len(dummy_workflow_for_extracting.extract_finished_task_list([0])) == 0


def test_get_task_list(dummy_workflow):
    # TODO if we have enough time for setting test case...
    assert (
        len(
            dummy_workflow.get_task_list(
                name="test",
                ID="test",
                default_work_amount=0,
                input_task_list=[],
                output_task_list=[],
                allocated_team_list=[],
                allocated_factory_list=[],
                need_facility=False,
                target_component="test",
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
                ready_time_list=[],
                start_time_list=[],
                finish_time_list=[],
                allocated_worker_list=[],
                allocated_worker_id_record=[],
                allocated_facility_list=[],
                allocated_facility_id_record=[],
            )
        )
        == 0
    )


def test_initialize():
    task = BaseTask("task")
    task.est = 2.0
    task.eft = 10.0
    task.lst = 3.0
    task.lft = 11.0
    task.remaining_work_amount = 7
    task.actual_work_amount = 6
    task.state = BaseTaskState.FINISHED
    task.ready_time_list = [1]
    task.start_time_list = [2]
    task.finish_time_list = [15]
    task.additional_task_flag = True
    task.allocated_worker_list = [BaseWorker("w1")]

    task_after1 = BaseTask("task_after1")
    task_after2 = BaseTask("task_after2", default_work_amount=5.0)
    task_after1.append_input_task(task)
    task_after2.append_input_task(task)

    w = BaseWorkflow([task, task_after1, task_after2])
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
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task4 = BaseTask("task4")
    task5 = BaseTask("task5")
    task3.extend_input_task_list([task1, task2])
    task5.extend_input_task_list([task3, task4])
    w = BaseWorkflow([task1, task2, task3, task4, task5])

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
    # this method is tested in test_check_state()
    pass


def test___check_finished(SF_workflow, FF_workflow):
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
    assert FF_workflow.task_list[1].state == BaseTaskState.FINISHED
    assert FF_workflow.task_list[2].state == BaseTaskState.NONE


def test___set_est_eft_data():
    # this method is tested in test_initialize()
    pass


def test___set_lst_lft_criticalpath_data():
    # this method is tested in test_initialize()
    pass


def test_perform():
    task = BaseTask("task")
    task.state = BaseTaskState.WORKING
    w1 = BaseWorker("w1")
    w2 = BaseWorker("w2")
    w1.workamount_skill_mean_map = {"task": 1.0}
    task.allocated_worker_list = [w1, w2]
    w1.assigned_task_list = [task]
    w2.assigned_task_list = [task]
    c = BaseComponent("a")
    c.append_targeted_task(task)
    w = BaseWorkflow([task])
    w.perform(10)
    assert task.remaining_work_amount == task.default_work_amount - 1.0
    assert task.target_component == c


def test_create_simple_gantt():
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
    w = BaseWorkflow([task1, task2, task0])
    w.create_simple_gantt(finish_margin=1.0, view_auto_task=True, view_ready=False)
    for ext in ["png"]:
        save_fig_path = "test." + ext
        w.create_simple_gantt(
            view_ready=True, view_auto_task=True, save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)
    w.create_simple_gantt(target_start_time=999)  # Warning
    w.create_simple_gantt(target_finish_time=1)  # Warning


def test_create_data_for_gantt_plotly():
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
    task2.append_input_task(task1)
    w = BaseWorkflow([task1, task2])
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    w.create_data_for_gantt_plotly(init_datetime, timedelta, view_ready=True)


def test_create_gantt_plotly():
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
    task2.append_input_task(task1)
    w = BaseWorkflow([task1, task2])
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        w.create_gantt_plotly(init_datetime, timedelta, save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_get_networkx_graph():
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
    task2.append_input_task(task1)
    w = BaseWorkflow([task1, task2])
    w.get_networkx_graph()
    # TODO
    # assert...


def test_draw_networkx():
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
    task2.append_input_task(task1)
    w = BaseWorkflow([task1, task2, task0])
    for ext in ["png"]:
        save_fig_path = "test." + ext
        w.draw_networkx(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_get_node_and_edge_trace_for_plotly_network():
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
    task2.append_input_task(task1)
    w = BaseWorkflow([task1, task2])
    (
        task_node_trace,
        auto_task_node_trace,
        edge_trace,
    ) = w.get_node_and_edge_trace_for_plotly_network()
    # TODO
    # assert...
    (
        task_node_trace,
        auto_task_node_trace,
        edge_trace,
    ) = w.get_node_and_edge_trace_for_plotly_network()
    # TODO
    # assert...


def test_draw_plotly_network():
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
    task2.append_input_task(task1)
    w = BaseWorkflow([task1, task2, task0])
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        w.draw_plotly_network(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)
