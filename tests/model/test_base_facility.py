#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_base_facility."""

import pytest

from pDESy.model.base_facility import BaseFacility, BaseFacilityState
from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_workplace import BaseWorkplace


@pytest.fixture(name="dummy_facility")
def fixture_dummy_facility():
    """dummy_facility."""
    w = BaseFacility("dummy", workplace_id="---")
    return w


def test_init(dummy_facility):
    """test_init."""
    # team = Team("team")
    assert dummy_facility.name == "dummy"
    assert dummy_facility.workplace_id == "---"
    assert dummy_facility.cost_per_time == 0.0
    assert not dummy_facility.solo_working
    assert dummy_facility.workamount_skill_mean_map == {}
    assert dummy_facility.workamount_skill_sd_map == {}
    # assert dummy_facility.quality_skill_mean_map == {}
    assert dummy_facility.state == BaseFacilityState.FREE
    assert dummy_facility.cost_list == []
    assert dummy_facility.assigned_task_list == []
    w = BaseFacility(
        "w1",
        solo_working=True,
        state=BaseFacilityState.WORKING,
        cost_list=[10, 10],
        state_record_list=["a"],
        assigned_task_list=[BaseTask("task")],
        assigned_task_id_record=[[], ["ss"]],
    )
    assert w.name == "w1"
    assert w.workplace_id is None
    assert w.cost_per_time == 0.0
    assert w.solo_working
    assert w.workamount_skill_mean_map == {}
    assert w.workamount_skill_sd_map == {}
    # assert w.quality_skill_mean_map == {}
    assert w.state == BaseFacilityState.WORKING
    assert w.cost_list == [10, 10]
    assert w.assigned_task_list[0].name == "task"
    assert w.assigned_task_id_record == [[], ["ss"]]


def test_str():
    """test_str."""
    print(BaseFacility("w1"))


def test_initialize():
    """test_initialize."""
    team = BaseWorkplace("team")
    w = BaseFacility("w1", workplace_id=team.ID)
    w.state = BaseFacilityState.WORKING
    w.cost_list = [9.0, 7.2]
    w.assigned_task_list = [BaseTask("task")]
    w.initialize()
    assert w.state == BaseFacilityState.FREE
    assert w.cost_list == []
    assert w.assigned_task_list == []


def test_remove_insert_absence_time_list():
    """test_remove_insert_absence_time_list."""
    w = BaseFacility("w1", "----")
    w.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    w.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w.state_record_list = [2, 1, 2, 1, 1, 2]

    absence_time_list = [0, 1, 4]
    w.remove_absence_time_list(absence_time_list)
    assert w.cost_list == [1.0, 0.0, 1.0]
    assert w.assigned_task_id_record == ["cc", "dd", "ff"]
    assert w.state_record_list == [2, 1, 2]

    w.insert_absence_time_list(absence_time_list)
    assert w.cost_list == [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert w.assigned_task_id_record == [None, None, "cc", "dd", "dd", "ff"]
    assert w.state_record_list == [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        2,
        1,
        BaseFacilityState.FREE,
        2,
    ]


def test_has_workamount_skill():
    """test_has_workamount_skill."""
    w = BaseFacility("w1", "----")
    w.workamount_skill_mean_map = {"task1": 1.0, "task2": 0.0}
    assert w.has_workamount_skill("task1")
    assert not w.has_workamount_skill("task2")
    assert not w.has_workamount_skill("task3")


def test_get_work_amount_skill_progress():
    """test_get_work_amount_skill_progress."""
    w = BaseFacility("w1", "----")
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
    w.get_work_amount_skill_progress("task1", seed=1234)  # seed test

    task2 = BaseTask("task2")
    task2.state = BaseTaskState.NONE
    w.assigned_task_list.append(task2)
    w.workamount_skill_sd_map["task1"] = 0.0
    assert w.get_work_amount_skill_progress("task1") == 1.0
    task2.state = BaseTaskState.WORKING
    assert w.get_work_amount_skill_progress("task1") == 0.5


def test_check_update_state_from_absence_time_list():
    """test_check_update_state_from_absence_time_list."""
    w = BaseFacility("w1", "----", absence_time_list=[1, 2, 4])
    w.state = BaseFacilityState.FREE
    w.check_update_state_from_absence_time_list(0)
    assert w.state == BaseFacilityState.FREE
    w.check_update_state_from_absence_time_list(1)
    assert w.state == BaseFacilityState.ABSENCE

    w.state = BaseFacilityState.WORKING
    w.assigned_task_list = []
    w.check_update_state_from_absence_time_list(2)
    assert w.state == BaseFacilityState.ABSENCE
    w.check_update_state_from_absence_time_list(3)
    assert w.state == BaseFacilityState.FREE

    task = BaseTask("task")
    w.state = BaseFacilityState.WORKING
    w.assigned_task_list = [task]
    w.check_update_state_from_absence_time_list(2)
    assert w.state == BaseFacilityState.ABSENCE
    w.check_update_state_from_absence_time_list(3)
    assert w.state == BaseFacilityState.WORKING


def test_get_time_list_for_gantt_chart():
    """test_get_time_list_for_gantt_chart."""
    w = BaseFacility("w1", "----")
    w.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
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
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
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
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
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
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
    ]
    (
        ready_time_list,
        working_time_list,
        absence_time_list,
    ) = w.get_time_list_for_gantt_chart()
    assert ready_time_list == [(0, 1), (4, 3)]
    assert working_time_list == [(1, 3), (7, 1)]
    assert not absence_time_list


def test_print_mermaid_diagram(dummy_facility):
    """Test the print_mermaid_diagram method."""
    dummy_facility.print_mermaid_diagram(
        subgraph=True,
    )
