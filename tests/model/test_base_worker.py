#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_base_worker."""

import pytest

from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorker, BaseWorkerState


@pytest.fixture(name="dummy_worker")
def fixture_dummy_worker():
    """dummy_worker."""
    w = BaseWorker("dummy_worker", team_id="---")
    return w


def test_init(dummy_worker):
    """test_init."""
    assert dummy_worker.name == "dummy_worker"
    assert dummy_worker.team_id == "---"
    assert dummy_worker.cost_per_time == 0.0
    assert not dummy_worker.solo_working
    assert dummy_worker.workamount_skill_mean_map == {}
    assert dummy_worker.workamount_skill_sd_map == {}
    assert dummy_worker.facility_skill_map == {}
    assert dummy_worker.quality_skill_mean_map == {}
    assert dummy_worker.state == BaseWorkerState.FREE
    assert dummy_worker.cost_list == []
    w = BaseWorker(
        "w1",
        solo_working=True,
        state=BaseWorkerState.WORKING,
        cost_list=[10, 10],
        state_record_list=["a"],
        assigned_task_id_list=[BaseTask("task").ID],
        assigned_task_id_record=[[], ["ss"]],
    )
    assert w.name == "w1"
    assert w.team_id is None
    assert w.cost_per_time == 0.0
    assert w.solo_working
    assert w.workamount_skill_mean_map == {}
    assert w.workamount_skill_sd_map == {}
    assert w.facility_skill_map == {}
    assert w.quality_skill_mean_map == {}
    assert w.state == BaseWorkerState.WORKING
    assert w.cost_list == [10, 10]
    assert w.assigned_task_id_record == [[], ["ss"]]


def test_str():
    """test_str."""
    print(BaseWorker("w1"))


def test_initialize():
    """test_initialize."""
    team = BaseTeam("team")
    w = BaseWorker("w1", team_id=team.ID)
    w.state = BaseWorkerState.WORKING
    w.cost_list = [9.0, 7.2]
    w.assigned_task_id_list = [BaseTask("task").ID]
    w.initialize()
    assert w.state == BaseWorkerState.FREE
    assert w.cost_list == []
    assert w.assigned_task_id_list == []


def test_has_workamount_skill():
    """test_has_workamount_skill."""
    w = BaseWorker("w1", "----")
    w.workamount_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    assert w.has_workamount_skill("task1")
    assert not w.has_workamount_skill("task2")
    assert not w.has_workamount_skill("task3")


def test_has_facility_skill():
    """test_has_facility_skill."""
    w = BaseWorker("w1", "----")
    w.facility_skill_map = {"f1": 1.0, "f2": 0.0}
    assert w.has_facility_skill("f1")
    assert not w.has_facility_skill("f2")
    assert not w.has_facility_skill("f3")


def test_has_quality_skill():
    """test_has_quality_skill."""
    w = BaseWorker("w1", "----")
    w.quality_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    assert w.has_quality_skill("task1")
    assert not w.has_quality_skill("task2")
    assert not w.has_quality_skill("task3")


def test_remove_insert_absence_time_list():
    """test_remove_insert_absence_time_list."""
    w = BaseWorker("w1", "----")
    w.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    w.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w.state_record_list = [2, 1, 2, 1, 1, 2]

    absence_time_list = [1, 3, 4]
    w.remove_absence_time_list(absence_time_list)
    assert w.cost_list == [1.0, 1.0, 1.0]
    assert w.assigned_task_id_record == ["aa", "cc", "ff"]
    assert w.state_record_list == [2, 2, 2]

    w.insert_absence_time_list(absence_time_list)
    assert w.cost_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert w.assigned_task_id_record == ["aa", "aa", "cc", "cc", "cc", "ff"]
    assert w.state_record_list == [2, 0, 2, 0, 0, 2]


def test_check_update_state_from_absence_time_list():
    """test_check_update_state_from_absence_time_list."""
    w = BaseWorker("w1", "----", absence_time_list=[1, 2, 4])
    w.state = BaseWorkerState.FREE
    w.check_update_state_from_absence_time_list(0)
    assert w.state == BaseWorkerState.FREE
    w.check_update_state_from_absence_time_list(1)
    assert w.state == BaseWorkerState.ABSENCE

    w.state = BaseWorkerState.WORKING
    w.assigned_task_id_list = []
    w.check_update_state_from_absence_time_list(2)
    assert w.state == BaseWorkerState.ABSENCE
    w.check_update_state_from_absence_time_list(3)
    assert w.state == BaseWorkerState.FREE

    task = BaseTask("task")
    w.state = BaseWorkerState.WORKING
    w.assigned_task_id_list = [task.ID]
    w.check_update_state_from_absence_time_list(2)
    assert w.state == BaseWorkerState.ABSENCE
    w.check_update_state_from_absence_time_list(3)
    assert w.state == BaseWorkerState.WORKING


def test_get_time_list_for_gantt_chart():
    """test_get_time_list_for_gantt_chart."""
    w = BaseWorker("w1", "----")
    w.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
    ]
    (
        ready_time_list,
        working_time_list,
        absence_time_list,
    ) = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(0, 2)]
    assert working_time_list == [(2, 1)]
    assert not absence_time_list

    w.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
    ]
    (
        ready_time_list,
        working_time_list,
        absence_time_list,
    ) = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(2, 1)]
    assert working_time_list == [(0, 2)]
    assert not absence_time_list

    w.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
    ]
    (
        ready_time_list,
        working_time_list,
        absence_time_list,
    ) = w.get_time_list_for_gantt_chart()
    assert not ready_time_list
    assert working_time_list == [(0, 3)]
    assert not absence_time_list

    # for backward
    w.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
    ]
    (
        ready_time_list,
        working_time_list,
        absence_time_list,
    ) = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(0, 1), (4, 3)]
    assert working_time_list == [(1, 3), (7, 1)]


def test_get_quality_skill_point():
    """test_get_quality_skill_point."""
    w = BaseWorker("w1", "----")
    w.quality_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    assert w.get_quality_skill_point("task3") == 0.0
    assert w.get_quality_skill_point("task2") == 0.0
    assert w.get_quality_skill_point("task1") == 1.0

    task1 = BaseTask("task1")
    task1.state = BaseTaskState.NONE
    w.assigned_task_id_list = [task1.ID]
    assert w.get_quality_skill_point("task1") == 1.0
    task1.state = BaseTaskState.READY
    assert w.get_quality_skill_point("task1") == 1.0
    task1.state = BaseTaskState.WORKING_ADDITIONALLY
    assert w.get_quality_skill_point("task1") == 1.0
    task1.state = BaseTaskState.FINISHED
    assert w.get_quality_skill_point("task1") == 1.0
    task1.state = BaseTaskState.WORKING
    assert w.get_quality_skill_point("task1") == 1.0

    w.quality_skill_sd_map["task1"] = 0.1
    assert w.get_quality_skill_point("task1", seed=1234) == 1.0471435163732492

    task2 = BaseTask("task2")
    task2.state = BaseTaskState.NONE
    w.assigned_task_id_list.append(task2.ID)
    w.quality_skill_sd_map["task1"] = 0.0
    assert w.get_quality_skill_point("task1") == 1.0
    task2.state = BaseTaskState.WORKING
    assert w.get_quality_skill_point("task1") == 1.0


def test_print_mermaid_diagram(dummy_worker):
    """Test the print_mermaid_diagram method."""
    dummy_worker.print_mermaid_diagram(
        subgraph=True,
    )
