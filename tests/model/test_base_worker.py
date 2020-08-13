#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_task import BaseTask
from pDESy.model.base_task import BaseTaskState
from pDESy.model.base_resource import BaseResourceState

import pytest


@pytest.fixture
def dummy_worker():
    w = BaseWorker("wsss", team_id="---")
    return w


def test_init(dummy_worker):
    # team = BaseTeam("team")
    assert dummy_worker.name == "wsss"
    assert dummy_worker.team_id == "---"
    assert dummy_worker.cost_per_time == 0.0
    assert dummy_worker.workamount_skill_mean_map == {}
    assert dummy_worker.workamount_skill_sd_map == {}
    assert dummy_worker.facility_skill_map == {}
    assert dummy_worker.state == BaseResourceState.FREE
    assert dummy_worker.cost_list == []
    assert dummy_worker.start_time_list == []
    assert dummy_worker.finish_time_list == []
    assert dummy_worker.assigned_task_list == []
    w = BaseWorker(
        "w1",
        state=BaseResourceState.WORKING,
        cost_list=[10, 10],
        start_time_list=[1],
        finish_time_list=[2],
        assigned_task_list=[BaseTask("task")],
        assigned_task_id_record=[[], ["ss"]],
    )
    assert w.name == "w1"
    assert w.team_id is None
    assert w.cost_per_time == 0.0
    assert w.workamount_skill_mean_map == {}
    assert w.workamount_skill_sd_map == {}
    assert w.facility_skill_map == {}
    assert w.state == BaseResourceState.WORKING
    assert w.cost_list == [10, 10]
    assert w.start_time_list == [1]
    assert w.finish_time_list == [2]
    assert w.assigned_task_list[0].name == "task"
    assert w.assigned_task_id_record == [[], ["ss"]]


def test_str():
    print(BaseWorker("w1"))


def test_initialize():
    team = BaseTeam("team")
    w = BaseWorker("w1", team_id=team.ID)
    w.state = BaseResourceState.WORKING
    w.cost_list = [9.0, 7.2]
    w.start_time_list = [0]
    w.finish_time_list = [1]
    w.assigned_task_list = [BaseTask("task")]
    w.initialize()
    assert w.state == BaseResourceState.FREE
    assert w.cost_list == []
    assert w.start_time_list == []
    assert w.finish_time_list == []
    assert w.assigned_task_list == []


# def test_set_workamount_skill_mean_map():
#     w = BaseResource("w1", "----")
#     w.set_workamount_skill_mean_map(
#         {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True
#     )
#     assert w.workamount_skill_mean_map == {"task1": 1.0, "task2": 0.0}
#     assert w.workamount_skill_sd_map == {"task1": 0.0, "task2": 0.0}
#     assert w.quality_skill_mean_map == {"task1": 0.0, "task2": 0.0}

#     w.set_workamount_skill_mean_map({"task3": 0.5, "task1": 0.5})
#     w.quality_skill_mean_map["task3"] = 1.0
#     assert w.workamount_skill_mean_map == {"task1": 0.5, "task3": 0.5}
#     assert w.workamount_skill_sd_map == {"task1": 0.0, "task2": 0.0}
#     assert w.quality_skill_mean_map == {"task1": 0.0, "task2": 0.0, "task3": 1.0}

#     w.set_workamount_skill_mean_map(
#         {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True,
#     )
#     assert w.workamount_skill_mean_map == {"task1": 1.0, "task2": 0.0}
#     assert w.workamount_skill_sd_map == {"task1": 0.0, "task2": 0.0}
#     assert w.quality_skill_mean_map == {"task1": 0.0, "task2": 0.0}


# def test_set_quality_skill_mean_map():
#     w = BaseResource("w1", "----")
#     w.set_quality_skill_mean_map(
#         {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True
#     )
#     assert w.quality_skill_mean_map == {"task1": 1.0, "task2": 0.0}
#     assert w.quality_skill_sd_map == {"task1": 0.0, "task2": 0.0}
#     assert w.quality_skill_mean_map == {"task1": 0.0, "task2": 0.0}

#     w.set_quality_skill_mean_map({"task3": 0.5, "task1": 0.5})
#     w.quality_skill_mean_map["task3"] = 1.0
#     assert w.quality_skill_mean_map == {"task1": 0.5, "task3": 0.5}
#     assert w.quality_skill_sd_map == {"task1": 0.0, "task2": 0.0}
#     assert w.quality_skill_mean_map == {"task1": 0.0, "task2": 0.0, "task3": 1.0}

#     w.set_quality_skill_mean_map(
#         {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True,
#     )
#     assert w.quality_skill_mean_map == {"task1": 1.0, "task2": 0.0}
#     assert w.quality_skill_sd_map == {"task1": 0.0, "task2": 0.0}
#     assert w.quality_skill_mean_map == {"task1": 0.0, "task2": 0.0}


def test_has_workamount_skill():
    w = BaseWorker("w1", "----")
    # w.set_workamount_skill_mean_map(
    #     {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True
    # )
    w.workamount_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    assert w.has_workamount_skill("task1")
    assert not w.has_workamount_skill("task2")
    assert not w.has_workamount_skill("task3")


def test_has_facility_skill():
    w = BaseWorker("w1", "----")
    # w.set_workamount_skill_mean_map(
    #     {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True
    # )
    w.facility_skill_map = {"f1": 1.0, "f2": 0.0}
    assert w.has_facility_skill("f1")
    assert not w.has_facility_skill("f2")
    assert not w.has_facility_skill("f3")


# def test_has_quality_skill():
#     w = BaseWorker("w1", "----")
#     # w.set_quality_skill_mean_map(
#     #     {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True
#     # )
#     w.quality_skill_mean_map = {"task1": 1.0, "task2": 0.0}
#     assert w.has_quality_skill("task1")
#     assert not w.has_quality_skill("task2")
#     assert not w.has_quality_skill("task3")


def test_get_work_amount_skill_progress():
    w = BaseWorker("w1", "----")
    # w.set_workamount_skill_mean_map(
    #     {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True
    # )
    w.workamount_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    assert w.get_work_amount_skill_progress("task3") == 0.0
    assert w.get_work_amount_skill_progress("task2") == 0.0
    with pytest.raises(ZeroDivisionError):
        assert w.get_work_amount_skill_progress("task1") == 1.0

    task1 = BaseTask("task1")
    task1.state = BaseTaskState.NONE
    w.assigned_task_list = [task1]
    with pytest.raises(ZeroDivisionError):
        assert w.get_work_amount_skill_progress("task1") == 1.0
    task1.state = BaseTaskState.READY
    with pytest.raises(ZeroDivisionError):
        assert w.get_work_amount_skill_progress("task1") == 1.0
    task1.state = BaseTaskState.WORKING_ADDITIONALLY
    assert w.get_work_amount_skill_progress("task1") == 1.0
    task1.state = BaseTaskState.FINISHED
    with pytest.raises(ZeroDivisionError):
        assert w.get_work_amount_skill_progress("task1") == 1.0
    task1.state = BaseTaskState.WORKING
    assert w.get_work_amount_skill_progress("task1") == 1.0

    w.workamount_skill_sd_map["task1"] = 0.1
    assert w.get_work_amount_skill_progress("task1", seed=1234) == 1.0471435163732492

    task2 = BaseTask("task2")
    task2.state = BaseTaskState.NONE
    w.assigned_task_list.append(task2)
    w.workamount_skill_sd_map["task1"] = 0.0
    assert w.get_work_amount_skill_progress("task1") == 1.0
    task2.state = BaseTaskState.WORKING
    assert w.get_work_amount_skill_progress("task1") == 0.5


# def test_get_quality_skill_point():
#     w = BaseWorker("w1", "----")
#     # w.set_quality_skill_mean_map(
#     #     {"task1": 1.0, "task2": 0.0}, update_other_skill_info=True
#     # )
#     w.quality_skill_mean_map = {"task1": 1.0, "task2": 0.0}
#     assert w.get_quality_skill_point("task3") == 0.0
#     assert w.get_quality_skill_point("task2") == 0.0
#     assert w.get_quality_skill_point("task1") == 1.0

#     task1 = BaseTask("task1")
#     task1.state = BaseTaskState.NONE
#     w.assigned_task_list = [task1]
#     assert w.get_quality_skill_point("task1") == 1.0
#     task1.state = BaseTaskState.READY
#     assert w.get_quality_skill_point("task1") == 1.0
#     task1.state = BaseTaskState.WORKING_ADDITIONALLY
#     assert w.get_quality_skill_point("task1") == 1.0
#     task1.state = BaseTaskState.FINISHED
#     assert w.get_quality_skill_point("task1") == 1.0
#     task1.state = BaseTaskState.WORKING
#     assert w.get_quality_skill_point("task1") == 1.0

#     w.quality_skill_sd_map["task1"] = 0.1
#     assert w.get_quality_skill_point("task1", seed=1234) == 1.0471435163732492

#     task2 = BaseTask("task2")
#     task2.state = BaseTaskState.NONE
#     w.assigned_task_list.append(task2)
#     w.quality_skill_sd_map["task1"] = 0.0
#     assert w.get_quality_skill_point("task1") == 1.0
#     task2.state = BaseTaskState.WORKING
#     assert w.get_quality_skill_point("task1") == 1.0
