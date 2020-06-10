#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.worker import Worker
from pDESy.model.task import Task
from pDESy.model.base_task import BaseTaskState
from pDESy.model.component import Component
import datetime


def test_init():
    task = Task("task")
    assert task.name == "task"
    assert len(task.ID) > 0
    assert task.default_work_amount == 10.0
    assert task.input_task_list == []
    assert task.output_task_list == []
    assert task.due_date == -1
    assert task.allocated_team_list == []
    assert task.target_component_list == []
    assert task.default_progress == 0.0
    assert task.additional_work_amount == 0.0
    assert task.est == 0.0
    assert task.eft == 0.0
    assert task.lst == -1.0
    assert task.lft == -1.0
    assert task.remaining_work_amount == task.default_work_amount * (
        1.0 - task.default_progress
    )
    # assert task.actual_work_amount == task.default_work_amount * (
    #     1.0 - task.default_progress
    # )
    assert task.state == BaseTaskState.NONE
    assert task.ready_time_list == []
    assert task.start_time_list == []
    assert task.finish_time_list == []
    assert task.additional_task_flag is False
    assert task.allocated_worker_list == []

    # task_b1 = Task("task_b1", ID="sss")
    # task_b2 = Task("task_b2")
    # task_a1 = Task("task_a1")
    # task_a2 = Task("task_a2")
    # assert task_b1.ID == "sss"


def test_str():
    print(Task("task"))


def test_append_input_task():
    task1 = Task("task1")
    task2 = Task("task2")
    task2.append_input_task(task1)
    assert task2.input_task_list == [task1]
    assert task1.output_task_list == [task2]


def test_extend_input_task_list():
    task11 = Task("task11")
    task12 = Task("task12")
    task2 = Task("task2")
    task2.extend_input_task_list([task11, task12])
    assert task2.input_task_list == [task11, task12]
    assert task11.output_task_list == [task2]
    assert task12.output_task_list == [task2]


def test_initialize():
    task = Task("task")
    task.est = 2.0
    task.eft = 10.0
    task.lst = 3.0
    task.lft = 11.0
    task.remaining_work_amount = 7
    task.actual_work_amount = 6
    task.state = BaseTaskState.READY
    task.ready_time_list = [1]
    task.start_time_list = [2]
    task.finish_time_list = [15]
    task.additional_task_flag = True
    task.allocated_worker_list = [Worker("w1")]
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
    assert task.ready_time_list == []
    assert task.start_time_list == []
    assert task.finish_time_list == []
    assert task.additional_task_flag is False
    assert task.allocated_worker_list == []

    task = Task("task", default_progress=0.2)
    task.initialize()
    assert task.state == BaseTaskState.READY

    task = Task("task", default_progress=1.0)
    task.initialize()
    assert task.state == BaseTaskState.FINISHED


def test_perform():
    task = Task("task")
    task.state = BaseTaskState.WORKING
    w1 = Worker("w1")
    w2 = Worker("w2")
    w1.workamount_skill_mean_map = {"task": 1.0}
    task.allocated_worker_list = [w1, w2]
    w1.assigned_task_list = [task]
    w2.assigned_task_list = [task]
    c = Component("a")
    c.append_targeted_task(task)
    task.perform(10)
    assert task.remaining_work_amount == task.default_work_amount - 1.0
    assert task.target_component_list == [c]
    assert c.error == 0.0

    # Next test case
    w1.workamount_skill_sd_map = {"task": 0.2}
    w1.quality_skill_mean_map = {"task": 0.9}
    w1.quality_skill_sd_map = {"task": 0.02}
    task.perform(11, seed=1234, increase_component_error=2.0)
    assert task.remaining_work_amount == 7.905712967253502
    assert c.error == 2.0


def test_create_data_for_gantt_plotly():
    task1 = Task("task1")
    task1.start_time_list = [1, 4]
    task1.ready_time_list = [0, 2]
    task1.finish_time_list = [3, 5]
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    df = task1.create_data_for_gantt_plotly(init_datetime, timedelta, view_ready=True)
    assert df[0]["Start"] == (
        init_datetime + task1.ready_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Finish"] == (
        init_datetime + (task1.start_time_list[0]) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Type"] == "Task"
    assert df[1]["Start"] == (
        init_datetime + task1.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Finish"] == (
        init_datetime + (task1.finish_time_list[0] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Type"] == "Task"
