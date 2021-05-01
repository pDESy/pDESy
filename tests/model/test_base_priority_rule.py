#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pDESy.model.base_task import BaseTask
from pDESy.model.base_task import BaseTaskState
from pDESy.model.base_workflow import BaseWorkflow
from pDESy.model.base_worker import BaseWorker
import pDESy.model.base_priority_rule as pr
from pDESy.model.base_priority_rule import (
    TaskPriorityRuleMode,
    ResourcePriorityRuleMode,
)


def test_sort_task_list_TSLACK():
    t0 = BaseTask("t0", est=10, lst=30)
    t1 = BaseTask("t1", est=10, lst=20)
    t2 = BaseTask("t2", est=10, lst=10)
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.TSLACK)
    assert task_list[0].name == "t2"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t0"


def test_sort_task_list_EST():
    t0 = BaseTask("t0", est=20, lst=30)
    t1 = BaseTask("t1", est=10, lst=20)
    t2 = BaseTask("t2", est=30, lst=40)
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.EST)
    assert task_list[0].name == "t1"
    assert task_list[1].name == "t0"
    assert task_list[2].name == "t2"


def test_sort_task_list_SPT():
    t0 = BaseTask("t0", default_work_amount=10)
    t1 = BaseTask("t1", default_work_amount=20)
    t2 = BaseTask("t2", default_work_amount=30)
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.SPT)
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"


def test_sort_task_list_LPT():
    t0 = BaseTask("t0", default_work_amount=10)
    t1 = BaseTask("t1", default_work_amount=20)
    t2 = BaseTask("t2", default_work_amount=30)
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.LPT)
    assert task_list[0].name == "t2"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t0"


def test_sort_task_list_SRPT():
    t0 = BaseTask("t0", default_work_amount=10)
    t1 = BaseTask("t1", default_work_amount=20)
    t2 = BaseTask("t2", default_work_amount=30)
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.SRPT)
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    t2.remaining_work_amount = 0
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.SRPT)
    assert task_list[0].name == "t2"
    assert task_list[1].name == "t0"
    assert task_list[2].name == "t1"


def test_sort_task_list_LRPT():
    t0 = BaseTask("t0", default_work_amount=10)
    t1 = BaseTask("t1", default_work_amount=20)
    t2 = BaseTask("t2", default_work_amount=30)
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.LRPT)
    assert task_list[0].name == "t2"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t0"
    t2.remaining_work_amount = 0
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.LRPT)
    assert task_list[0].name == "t1"
    assert task_list[1].name == "t0"
    assert task_list[2].name == "t2"


def test_sort_task_list_FIFO():
    t0 = BaseTask("t0")
    t0.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.READY,
        BaseTaskState.READY,
    ]
    t1 = BaseTask("t1")
    t1.state_record_list = [BaseTaskState.NONE, BaseTaskState.NONE, BaseTaskState.NONE]
    t2 = BaseTask("t2")
    t2.state_record_list = [BaseTaskState.NONE, BaseTaskState.NONE, BaseTaskState.READY]

    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.FIFO)
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t2"
    assert task_list[2].name == "t1"


def test_sort_task_list_LWRPT():
    t0 = BaseTask("t0", default_work_amount=10)
    t1 = BaseTask("t1", default_work_amount=20)
    t2 = BaseTask("t2", default_work_amount=30)
    w0 = BaseWorkflow("w0")
    w1 = BaseWorkflow("w1")
    w2 = BaseWorkflow("w2")
    w0.task_list = [t0]
    w1.task_list = [t1]
    w2.task_list = [t2]
    w0.initialize()  # for registering task.remaining_work_amount and workflow.critical_path_length
    w1.initialize()  # for registering task.remaining_work_amount and workflow.critical_path_length
    w2.initialize()  # for registering task.remaining_work_amount and workflow.critical_path_length
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.LWRPT)
    assert task_list[0].name == "t2"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t0"


def test_sort_task_list_SWRPT():
    t0 = BaseTask("t0", default_work_amount=10)
    t1 = BaseTask("t1", default_work_amount=20)
    t2 = BaseTask("t2", default_work_amount=30)
    w0 = BaseWorkflow("w0")
    w1 = BaseWorkflow("w1")
    w2 = BaseWorkflow("w2")
    w0.task_list = [t0]
    w1.task_list = [t1]
    w2.task_list = [t2]
    w0.initialize()  # for registering task.remaining_work_amount and workflow.critical_path_length
    w1.initialize()  # for registering task.remaining_work_amount and workflow.critical_path_length
    w2.initialize()  # for registering task.remaining_work_amount and workflow.critical_path_length
    task_list = [t0, t1, t2]
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"
    task_list = pr.sort_task_list(task_list, TaskPriorityRuleMode.SWRPT)
    assert task_list[0].name == "t0"
    assert task_list[1].name == "t1"
    assert task_list[2].name == "t2"


def test_sort_worker_list_SSP():
    r0 = BaseWorker("r0")
    r0.workamount_skill_mean_map = {
        "a": 1.0,
        "b": 1.0,
        "c": 0.0,
        "d": 1.0,
    }
    r1 = BaseWorker("r1")
    r1.workamount_skill_mean_map = {
        "a": 0.0,
        "b": 1.0,
    }
    r2 = BaseWorker("r2")
    r2.workamount_skill_mean_map = {
        "a": 0.0,
        "b": 0.0,
        "c": 0.0,
        "d": 0.0,
    }
    r_list = [r0, r1, r2]
    assert r_list[0].name == "r0"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r2"
    r_list = pr.sort_resource_list(r_list, ResourcePriorityRuleMode.SSP)
    assert r_list[0].name == "r2"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r0"


def test_sort_worker_list_VC():
    r0 = BaseWorker("r0")
    r0.cost_per_time = 30

    r1 = BaseWorker("r1")
    r1.cost_per_time = 50

    r2 = BaseWorker("r2")
    r2.cost_per_time = 40

    r_list = [r0, r1, r2]
    assert r_list[0].name == "r0"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r2"
    r_list = pr.sort_resource_list(r_list, ResourcePriorityRuleMode.VC)
    assert r_list[0].name == "r0"
    assert r_list[1].name == "r2"
    assert r_list[2].name == "r1"


def test_sort_worker_list_HSV():
    r0 = BaseWorker("r0")
    r0.workamount_skill_mean_map = {
        "a": 0.0,
        "b": 0.0,
        "c": 1.0,
        "d": 0.0,
    }
    r1 = BaseWorker("r1")
    r1.workamount_skill_mean_map = {
        "a": 1.0,
        "b": 1.0,
    }
    r2 = BaseWorker("r2")
    r2.workamount_skill_mean_map = {
        "a": 2.0,
        "b": 0.5,
        "c": 2.0,
        "d": 1.0,
    }
    r_list = [r0, r1, r2]
    assert r_list[0].name == "r0"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r2"
    r_list = pr.sort_resource_list(r_list, ResourcePriorityRuleMode.HSV, "a")
    assert r_list[0].name == "r2"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r0"
    r_list = pr.sort_resource_list(r_list, ResourcePriorityRuleMode.HSV, "b")
    assert r_list[0].name == "r1"
    assert r_list[1].name == "r2"
    assert r_list[2].name == "r0"
