#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_base_task."""

import datetime

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility
from pDESy.model.base_task import BaseTask, BaseTaskDependency, BaseTaskState
from pDESy.model.base_worker import BaseWorker


def test_init():
    """test_init."""
    task = BaseTask("task")
    assert task.name == "task"
    assert len(task.ID) > 0
    assert task.default_work_amount == 10.0
    assert task.input_task_list == []
    assert task.output_task_list == []
    assert task.due_time == -1
    assert task.allocated_team_list == []
    assert task.target_component is None
    assert task.default_progress == 0.0
    assert task.fixing_allocating_worker_id_list is None
    assert task.fixing_allocating_facility_id_list is None
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
    # assert task.additional_task_flag is False
    assert task.allocated_worker_list == []

    tb = BaseTask(
        "task_b1",
        remaining_work_amount=0.0,
        state=BaseTaskState.FINISHED,
        state_record_list=["a"],
        fixing_allocating_worker_id_list=["aaa", "bbb"],
        fixing_allocating_facility_id_list=["ccc", "ddd"],
        allocated_worker_list=[BaseWorker("a")],
        allocated_worker_id_record=[["idid"]],
        allocated_facility_list=[BaseFacility("b")],
        allocated_facility_id_record=[["ibib"]],
        additional_task_flag=True,
    )
    assert tb.fixing_allocating_worker_id_list == ["aaa", "bbb"]
    assert tb.fixing_allocating_facility_id_list == ["ccc", "ddd"]
    assert tb.remaining_work_amount == 0.0
    assert tb.state == BaseTaskState.FINISHED
    assert tb.allocated_worker_list[0].name == "a"
    assert tb.allocated_worker_id_record == [["idid"]]
    assert tb.allocated_facility_list[0].name == "b"
    assert tb.allocated_facility_id_record == [["ibib"]]
    assert tb.additional_task_flag is True


def test_str():
    """test_str."""
    print(BaseTask("task"))


def test_append_input_task():
    """test_append_input_task."""
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task2.append_input_task(task1)
    assert task2.input_task_list == [[task1, BaseTaskDependency.FS]]
    assert task1.output_task_list == [[task2, BaseTaskDependency.FS]]


def test_extend_input_task_list():
    """test_extend_input_task_list."""
    task11 = BaseTask("task11")
    task12 = BaseTask("task12")
    task2 = BaseTask("task2")
    task2.extend_input_task_list([task11, task12])
    assert task2.input_task_list == [
        [task11, BaseTaskDependency.FS],
        [task12, BaseTaskDependency.FS],
    ]
    assert task11.output_task_list == [[task2, BaseTaskDependency.FS]]
    assert task12.output_task_list == [[task2, BaseTaskDependency.FS]]


def test_initialize():
    """test_initialize."""
    task = BaseTask("task")
    task.est = 2.0
    task.eft = 10.0
    task.lst = 3.0
    task.lft = 11.0
    task.remaining_work_amount = 7
    task.actual_work_amount = 6
    task.state = BaseTaskState.READY
    task.additional_task_flag = True
    task.allocated_worker_list = [BaseWorker("w1")]
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
    assert task.allocated_worker_list == []

    task = BaseTask("task", default_progress=0.2)
    task.initialize()
    assert task.state == BaseTaskState.READY

    task = BaseTask("task", default_progress=1.0)
    task.initialize()
    assert task.state == BaseTaskState.FINISHED


def test_perform():
    """test_perform."""
    auto = BaseTask("a", auto_task=True, state=BaseTaskState.WORKING)
    auto.perform(0, seed=1234)
    assert auto.remaining_work_amount == auto.default_work_amount - 1

    task = BaseTask("task")
    task.state = BaseTaskState.READY
    w1 = BaseWorker("w1")
    w2 = BaseWorker("w2")
    w1.workamount_skill_mean_map = {"task": 1.0}
    task.allocated_worker_list = [w1, w2]
    w1.assigned_task_list = [task]
    w2.assigned_task_list = [task]
    c = BaseComponent("a")
    c.append_targeted_task(task)
    task.perform(10)
    assert task.remaining_work_amount == task.default_work_amount
    assert task.target_component == c
    # assert c.error == 0.0

    task.state = BaseTaskState.WORKING
    task.perform(10)
    assert task.remaining_work_amount == task.default_work_amount - 1.0
    assert task.target_component == c
    # assert c.error == 0.0

    # Next test case
    w1.workamount_skill_sd_map = {"task": 0.2}
    w1.quality_skill_mean_map = {"task": 0.9}
    w1.quality_skill_sd_map = {"task": 0.02}
    task.perform(11, seed=1234, increase_component_error=2.0)
    assert task.remaining_work_amount == 7.905712967253502
    assert c.error == 2.0


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
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    task1.create_data_for_gantt_plotly(init_datetime, timedelta, view_ready=True)


def test_get_state_from_record():
    """test_get_state_from_record."""
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


def test_can_add_resources():
    """test_can_add_resources."""
    task = BaseTask("task")
    w1 = BaseWorker("w1", solo_working=True)
    w2 = BaseWorker("w2")
    w1.workamount_skill_mean_map = {"task": 1.0}
    w2.workamount_skill_mean_map = {"task": 1.0}
    f1 = BaseFacility("f1")
    f2 = BaseFacility("f2", solo_working=True)
    f1.workamount_skill_mean_map = {"task": 1.0}
    f2.workamount_skill_mean_map = {"task": 1.0}
    w1.facility_skill_map = {f1.name: 1.0}

    assert task.can_add_resources(worker=w1) is False
    task.state = BaseTaskState.FINISHED
    assert task.can_add_resources(worker=w1) is False
    task.state = BaseTaskState.READY
    assert task.can_add_resources(worker=w1) is True

    assert task.can_add_resources(worker=w2, facility=f2) is False
    assert task.can_add_resources(worker=w1, facility=f1) is True

    w1.solo_working = False
    task.allocated_worker_list = [w1]
    task.allocated_facility_list = [f1]
    assert task.can_add_resources(worker=w2, facility=f2) is False

    w1.solo_working = True
    assert task.can_add_resources(worker=w2, facility=f2) is False

    w1.solo_working = False
    f1.solo_working = True
    assert task.can_add_resources(worker=w2, facility=f2) is False

    w1.solo_working = False
    f1.solo_working = False
    w2.solo_working = False
    f2.solo_working = False
    assert task.can_add_resources(worker=w1, facility=f1) is True
    assert task.can_add_resources(worker=w2, facility=f2) is False

    f1.workamount_skill_mean_map = {}
    assert task.can_add_resources(worker=w1, facility=f1) is False

    w1.workamount_skill_mean_map = {}
    assert task.can_add_resources(worker=w1) is False

    assert task.can_add_resources() is False

    task2 = BaseTask(
        "task",
        fixing_allocating_worker_id_list=[w1.ID],
        fixing_allocating_facility_id_list=[f1.ID],
    )
    task2.state = BaseTaskState.WORKING
    w1.workamount_skill_mean_map = {"task": 1.0}
    w2.workamount_skill_mean_map = {"task": 1.0}
    f1.workamount_skill_mean_map = {"task": 1.0}
    f2.workamount_skill_mean_map = {"task": 1.0}
    assert task2.can_add_resources(worker=w1) is True
    assert task2.can_add_resources(worker=w2) is False
    assert task2.can_add_resources(worker=w1, facility=f1) is True
    assert task2.can_add_resources(worker=w1, facility=f2) is False


def test_remove_insert_absence_time_list():
    """test_remove__nsert_absence_time_list."""
    w = BaseTask("w1", "----")
    w.allocated_worker_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w.allocated_facility_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w.state_record_list = [0, 1, 2, 3, 4, 5]

    absence_time_list = [3, 4]
    w.remove_absence_time_list(absence_time_list)
    assert w.allocated_worker_id_record == ["aa", "bb", "cc", "ff"]
    assert w.allocated_facility_id_record == ["aa", "bb", "cc", "ff"]
    assert w.state_record_list == [0, 1, 2, 5]

    w.insert_absence_time_list(absence_time_list)
    assert w.allocated_worker_id_record == ["aa", "bb", "cc", "cc", "cc", "ff"]
    assert w.allocated_facility_id_record == ["aa", "bb", "cc", "cc", "cc", "ff"]
    assert w.state_record_list == [0, 1, 2, 1, 1, 5]


def test_get_time_list_for_gannt_chart():
    w = BaseTask("w1", "----")
    w.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.READY,
        BaseTaskState.WORKING,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gannt_chart()
    assert ready_time_list == [(1, 1)]
    assert working_time_list == [(2, 1)]

    w.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.READY,
        BaseTaskState.READY,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gannt_chart()
    assert ready_time_list == [(1, 2)]
    assert working_time_list == []

    w.state_record_list = [
        BaseTaskState.NONE,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    ready_time_list, working_time_list = w.get_time_list_for_gannt_chart()
    assert ready_time_list == []
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
    ready_time_list, working_time_list = w.get_time_list_for_gannt_chart()
    assert ready_time_list == [(2, 2), (7, 1)]
    assert working_time_list == [(1, 1), (5, 2)]
