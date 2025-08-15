#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_base_priority_rule."""

import pDESy.model.base_priority_rule as pr
from pDESy.model.base_facility import BaseFacility
from pDESy.model.base_priority_rule import (
    ResourcePriorityRuleMode,
    TaskPriorityRuleMode,
    WorkplacePriorityRuleMode,
)
from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_workplace import BaseWorkplace


def test_sort_task_list_tslack():
    """test_sort_task_list_tslack."""
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


def test_sort_task_list_est():
    """test_sort_task_list_est."""
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


def test_sort_task_list_spt():
    """test_sort_task_list_spt."""
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


def test_sort_task_list_lpt():
    """test_sort_task_list_lpt."""
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


def test_sort_task_list_srpt():
    """test_sort_task_list_srpt."""
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


def test_sort_task_list_lrpt():
    """test_sort_task_list_lrpt."""
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


def test_sort_task_list_fifo():
    """test_sort_task_list_fifo."""
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


def test_sort_worker_list_mw():
    """test_sort_worker_list_mw."""
    r0 = BaseWorker("r0", main_workplace_id="w0")
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
    r2 = BaseWorker("r2", main_workplace_id="w2")
    r2.workamount_skill_mean_map = {
        "a": 0.0,
        "b": 0.0,
        "c": 0.0,
        "d": 0.0,
    }
    r3 = BaseWorker("r3", main_workplace_id="w2")
    r3.workamount_skill_mean_map = {
        "a": 1.0,
        "b": 0.0,
        "c": 0.0,
        "d": 0.0,
    }
    r_list = [r0, r1, r2, r3]
    assert r_list[0].name == "r0"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r2"
    assert r_list[3].name == "r3"
    r_list = pr.sort_worker_list(r_list, ResourcePriorityRuleMode.MW, workplace_id="w2")
    assert r_list[0].name == "r2"  # r2
    assert r_list[1].name == "r3"  # r2
    assert r_list[2].name == "r1"  # r1
    assert r_list[3].name == "r0"  # r0


def test_sort_worker_list_ssp():
    """test_sort_worker_list_ssp."""
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
    r_list = pr.sort_worker_list(r_list, ResourcePriorityRuleMode.SSP)
    assert r_list[0].name == "r2"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r0"


def test_sort_worker_list_vc():
    """test_sort_worker_list_vc."""
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
    r_list = pr.sort_worker_list(r_list, ResourcePriorityRuleMode.VC)
    assert r_list[0].name == "r0"
    assert r_list[1].name == "r2"
    assert r_list[2].name == "r1"


def test_sort_worker_list_hsv():
    """test_sort_worker_list_hsv."""
    r0 = BaseWorker("r0")
    r0.workamount_skill_mean_map = {
        "a": 0.0,
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
    r_list = pr.sort_worker_list(r_list, ResourcePriorityRuleMode.HSV, name="a")
    assert r_list[0].name == "r2"
    assert r_list[1].name == "r1"
    assert r_list[2].name == "r0"
    r_list = pr.sort_worker_list(r_list, ResourcePriorityRuleMode.HSV, name="b")
    assert r_list[0].name == "r1"
    assert r_list[1].name == "r2"
    assert r_list[2].name == "r0"


def test_sort_workplace_list_fss():
    """test_sort_workplace_list_fss."""
    wp4 = BaseWorkplace("wp4", max_space_size=4.0)
    wp5 = BaseWorkplace("wp5", max_space_size=5.0)
    workplace_list = [wp4, wp5]
    assert workplace_list[0].name == "wp4"
    assert workplace_list[1].name == "wp5"
    workplace_list = pr.sort_workplace_list(
        workplace_list, WorkplacePriorityRuleMode.FSS
    )
    assert workplace_list[0].name == "wp5"
    assert workplace_list[1].name == "wp4"


def test_sort_workplace_list_ssp():
    """test_sort_workplace_list_ssp."""
    wp4 = BaseWorkplace("wp4", max_space_size=4.0)
    wp5 = BaseWorkplace("wp5", max_space_size=4.0)
    workplace_list = [wp4, wp5]
    assert workplace_list[0].name == "wp4"
    assert workplace_list[1].name == "wp5"
    f51 = BaseFacility("f51")
    f51.workamount_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    wp5.add_facility(f51)
    workplace_list = pr.sort_workplace_list(
        workplace_list, WorkplacePriorityRuleMode.SSP, name="task1"
    )
    assert workplace_list[0].name == "wp5"
    assert workplace_list[1].name == "wp4"
    workplace_list = pr.sort_workplace_list(
        workplace_list, WorkplacePriorityRuleMode.SSP, name="task2"
    )
    assert workplace_list[0].name == "wp5"
    assert workplace_list[1].name == "wp4"
    f41 = BaseFacility("f41")
    f41.workamount_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    wp4.add_facility(f41)
    f42 = BaseFacility("f42")
    f42.workamount_skill_mean_map = {"task1": 1.0}
    wp4.add_facility(f42)
    workplace_list = pr.sort_workplace_list(
        workplace_list, WorkplacePriorityRuleMode.SSP, name="task1"
    )
    assert workplace_list[0].name == "wp4"
    assert workplace_list[1].name == "wp5"
    f51.workamount_skill_mean_map["task2"] = 2.0
    workplace_list = pr.sort_workplace_list(
        workplace_list, WorkplacePriorityRuleMode.SSP, name="task2"
    )
    assert workplace_list[0].name == "wp5"
    assert workplace_list[1].name == "wp4"
