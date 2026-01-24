#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for BaseWorkplace.

This module contains unit tests for the BaseWorkplace class and related functionality.
"""

import datetime
import os

import pytest

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility, BaseFacilityState
from pDESy.model.base_task import BaseTask
from pDESy.model.base_workplace import BaseWorkplace


def test_init():
    """Test initialization of BaseWorkplace."""
    workplace = BaseWorkplace("workplace")
    assert workplace.name == "workplace"
    assert len(workplace.ID) > 0
    assert workplace.facility_set == set()
    assert workplace.targeted_task_id_set == set()
    assert workplace.parent_workplace_id is None
    assert workplace.input_workplace_id_set == set()
    assert workplace.cost_record_list == []
    workplace.cost_record_list.append(1)
    assert workplace.cost_record_list == [1.0]

    w1 = BaseFacility("w1")
    t1 = BaseTask("task1")
    workplace1 = BaseWorkplace(
        "workplace1",
        parent_workplace_id=workplace.ID,
        targeted_task_id_set={t1.ID},
        facility_set={w1},
        max_space_size=2.0,
        cost_record_list=[10],
        placed_component_id_set={BaseComponent("c").ID},
        placed_component_id_set_record_list=["xxxx"],
    )
    assert workplace1.facility_set == {w1}
    assert workplace1.targeted_task_id_set == {t1.ID}
    assert workplace1.parent_workplace_id == workplace.ID
    assert workplace1.max_space_size == 2.0
    assert workplace1.cost_record_list == [10]
    assert workplace1.placed_component_id_set_record_list == ["xxxx"]


@pytest.fixture(name="dummy_team_for_extracting")
def fixture_dummy_team_for_extracting():
    """Fixture for a dummy BaseWorkplace for extracting tests.

    Returns:
        BaseWorkplace: A dummy workplace instance with several facilities.
    """
    facility1 = BaseFacility("facility1")
    facility1.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    facility2 = BaseFacility("facility2")
    facility2.state_record_list = [
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
    ]
    facility3 = BaseFacility("facility3")
    facility3.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    facility4 = BaseFacility("facility4")
    facility4.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
    ]
    facility5 = BaseFacility("facility5")
    facility5.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
    ]
    return BaseWorkplace(
        "test", facility_set={facility1, facility2, facility3, facility4, facility5}
    )


def test_extract_free_facility_set(dummy_team_for_extracting):
    """Test extracting free facilities.

    Args:
        dummy_team_for_extracting (BaseWorkplace): The dummy workplace fixture.
    """
    assert len(dummy_team_for_extracting.extract_free_facility_set([5])) == 0
    assert len(dummy_team_for_extracting.extract_free_facility_set([3, 4])) == 2
    assert len(dummy_team_for_extracting.extract_free_facility_set([0, 1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_free_facility_set([0, 1, 4])) == 2


def test_extract_working_facility_set(dummy_team_for_extracting):
    """Test extracting working facilities.

    Args:
        dummy_team_for_extracting (BaseWorkplace): The dummy workplace fixture.
    """
    assert len(dummy_team_for_extracting.extract_working_facility_set([0, 1])) == 1
    assert len(dummy_team_for_extracting.extract_working_facility_set([1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_working_facility_set([1, 2, 3])) == 1


def test_set_parent_workplace():
    """Test setting the parent workplace."""
    workplace = BaseWorkplace("workplace")
    parent_workplace = BaseWorkplace("parent_workplace")
    workplace.set_parent_workplace(parent_workplace)
    assert workplace.parent_workplace_id == parent_workplace.ID


def test_add_facility():
    """Test adding a facility to the workplace."""
    workplace = BaseWorkplace("workplace")
    facility = BaseFacility("facility")
    workplace.add_facility(facility)
    assert len(workplace.facility_set) == 1
    assert facility.workplace_id == workplace.ID


def test_update_targeted_task_set():
    """Test updating the targeted task set."""
    workplace = BaseWorkplace("workplace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workplace.update_targeted_task_set({task1, task2})
    assert workplace.targeted_task_id_set == {task1.ID, task2.ID}
    assert task1.allocated_workplace_id_set == {workplace.ID}
    assert task2.allocated_workplace_id_set == {workplace.ID}


def test_add_targeted_task():
    """Test adding a targeted task."""
    workplace = BaseWorkplace("workplace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workplace.add_targeted_task(task1)
    workplace.add_targeted_task(task2)
    assert workplace.targeted_task_id_set == {task1.ID, task2.ID}
    assert task1.allocated_workplace_id_set == {workplace.ID}
    assert task2.allocated_workplace_id_set == {workplace.ID}


def test_create_facility():
    """Test creating a facility from a workplace."""
    workplace = BaseWorkplace("workplace")
    facility1 = workplace.create_facility(
        name="facility1",
    )
    assert facility1.name == "facility1"
    assert facility1.workplace_id == workplace.ID
    assert workplace.facility_set == {facility1}
    facility2 = workplace.create_facility(
        name="facility2",
    )
    assert facility2.workplace_id == workplace.ID
    assert workplace.facility_set == {facility2, facility1}


def test_initialize():
    """Test initialization/reset of BaseWorkplace and its facilities."""
    workplace = BaseWorkplace("workplace")
    workplace.cost_record_list = [9.0, 7.2]
    w = BaseFacility("w1")
    workplace.facility_set.add(w)
    w.state = BaseFacilityState.WORKING
    w.cost_record_list = [9.0, 7.2]
    w.assigned_task_worker_id_tuple_set = {(BaseTask("task").ID, "dummy_worker")}
    workplace.initialize()
    assert workplace.cost_record_list == []
    assert w.state == BaseFacilityState.FREE
    assert w.cost_record_list == []
    assert w.assigned_task_worker_id_tuple_set == set()


def test_add_labor_cost():
    """Test adding labor cost to the workplace and its facilities."""
    workplace = BaseWorkplace("workplace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    workplace.facility_set = {w2, w1}
    w1.state = BaseFacilityState.WORKING
    w2.state = BaseFacilityState.FREE
    workplace.add_labor_cost()
    assert w1.cost_record_list == [10.0]
    assert w2.cost_record_list == [0.0]
    assert workplace.cost_record_list == [10.0]
    workplace.add_labor_cost(only_working=False)
    assert workplace.cost_record_list == [10.0, 15.0]
    assert w1.cost_record_list == [10.0, 10.0]
    assert w2.cost_record_list == [0.0, 5.0]


def test_str():
    """Test string representation of BaseWorkplace."""
    print(BaseWorkplace("dummy_base_workflow"))


def test_get_facility_set():
    """Test getting a facility set with specific parameters."""
    workplace = BaseWorkplace("workplace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    workplace.facility_set = {w2, w1}
    assert (
        len(
            workplace.get_facility_set(
                name="test",
                ID="test",
                workplace_id="test",
                cost_per_time=99876,
                solo_working=True,
                workamount_skill_mean_map={},
                workamount_skill_sd_map=[],
                state=BaseFacilityState.WORKING,
                cost_record_list=[],
                assigned_task_worker_id_tuple_set=set(),
                assigned_task_worker_id_tuple_set_record_list=[],
            )
        )
        == 0
    )




def test_add_input_workplace():
    """Test adding input workplaces."""
    workplace = BaseWorkplace("workplace")
    workplace1 = BaseWorkplace("workplace1")
    workplace2 = BaseWorkplace("workplace2")
    workplace.add_input_workplace(workplace1)
    workplace.add_input_workplace(workplace2)
    assert workplace.input_workplace_id_set == {workplace1.ID, workplace2.ID}


def test_update_input_workplace_set():
    """Test updating input workplace set."""
    workplace11 = BaseWorkplace("workplace11")
    workplace12 = BaseWorkplace("workplace12")
    workplace2 = BaseWorkplace("workplace2")
    workplace2.update_input_workplace_set([workplace11, workplace12])
    assert workplace2.input_workplace_id_set == {workplace11.ID, workplace12.ID}


def test_remove_insert_absence_time_list():
    """Test removing and inserting absence time list for BaseWorkplace and its facilities."""
    f1 = BaseFacility("w1", "----")
    f1.cost_record_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    f1.assigned_task_worker_id_tuple_set_record_list = [
        "aa",
        "bb",
        "cc",
        "dd",
        "ee",
        "ff",
    ]
    f1.state_record_list = [2, 1, 2, 1, 1, 2]

    f2 = BaseFacility("w1", "----")
    f2.cost_record_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    f2.assigned_task_worker_id_tuple_set_record_list = [
        "aa",
        "bb",
        "cc",
        "dd",
        "ee",
        "ff",
    ]
    f2.state_record_list = [2, 1, 2, 1, 1, 2]

    workplace = BaseWorkplace("aa", facility_set={f1, f2})
    workplace.cost_record_list = [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]

    absence_time_list = [1, 3, 4]
    workplace.remove_absence_time_list(absence_time_list)
    assert workplace.cost_record_list == [2.0, 2.0, 2.0]
    assert f1.cost_record_list == [1.0, 1.0, 1.0]
    assert f1.assigned_task_worker_id_tuple_set_record_list == ["aa", "cc", "ff"]
    assert f1.state_record_list == [2, 2, 2]
    assert f2.cost_record_list == [1.0, 1.0, 1.0]
    assert f2.assigned_task_worker_id_tuple_set_record_list == ["aa", "cc", "ff"]
    assert f2.state_record_list == [2, 2, 2]

    workplace.insert_absence_time_list(absence_time_list)
    assert workplace.cost_record_list == [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]
    assert f1.cost_record_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert f1.assigned_task_worker_id_tuple_set_record_list == [
        "aa",
        "aa",
        "cc",
        "cc",
        "cc",
        "ff",
    ]
    assert f1.state_record_list == [2, 0, 2, 0, 0, 2]
    assert f2.cost_record_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert f2.assigned_task_worker_id_tuple_set_record_list == [
        "aa",
        "aa",
        "cc",
        "cc",
        "cc",
        "ff",
    ]
    assert f2.state_record_list == [2, 0, 2, 0, 0, 2]


def test_print_mermaid_diagram(dummy_team_for_extracting):
    """Test printing Mermaid diagrams.

    Args:
        dummy_team_for_extracting (BaseWorkplace): The dummy workplace fixture.
    """
    dummy_team_for_extracting.print_mermaid_diagram(orientations="LR", subgraph=True)
    dummy_team_for_extracting.print_target_facility_mermaid_diagram(
        [
            list(dummy_team_for_extracting.facility_set)[0],
            list(dummy_team_for_extracting.facility_set)[1],
        ],
        orientations="TB",
        subgraph=True,
    )
