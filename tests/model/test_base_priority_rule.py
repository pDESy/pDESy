#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pDESy.model.base_task import BaseTask
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_priority_rule import BasePriorityRule as pr
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
