#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for BaseTeam.

This module contains unit tests for the BaseTeam class and related functionality.
"""

import datetime
import os

import pytest

from pDESy.model.base_task import BaseTask
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorker, BaseWorkerState


def test_init():
    """Test initialization of BaseTeam."""
    team = BaseTeam("team")
    assert team.name == "team"
    assert len(team.ID) > 0
    assert team.worker_set == set()
    assert team.targeted_task_id_set == set()
    assert team.parent_team_id is None
    assert team.cost_record_list == []
    team.cost_record_list.append(1)
    assert team.cost_record_list == [1.0]

    w1 = BaseWorker("w1")
    t1 = BaseTask("task1")
    team1 = BaseTeam(
        "team1",
        parent_team_id=team.ID,
        targeted_task_id_set={t1.ID},
        worker_set={w1},
        cost_record_list=[10],
    )
    assert team1.worker_set == {w1}
    assert team1.targeted_task_id_set == {t1.ID}
    assert team1.parent_team_id == team.ID
    assert team1.cost_record_list == [10]


def test_set_parent_team():
    """Test setting the parent team."""
    team = BaseTeam("team")
    parent_team = BaseTeam("parent_team")
    team.set_parent_team(parent_team)
    assert team.parent_team_id == parent_team.ID


def test_update_targeted_task_set():
    """Test updating the targeted task set."""
    team = BaseTeam("team")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    team.update_targeted_task_set({task1, task2})
    assert team.targeted_task_id_set == {task1.ID, task2.ID}
    assert task1.allocated_team_id_set == {team.ID}
    assert task2.allocated_team_id_set == {team.ID}


def test_add_targeted_task():
    """Test adding a targeted task."""
    team = BaseTeam("team")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    team.add_targeted_task(task1)
    team.add_targeted_task(task2)
    assert team.targeted_task_id_set == {task1.ID, task2.ID}
    assert task1.allocated_team_id_set == {team.ID}
    assert task2.allocated_team_id_set == {team.ID}


def test_add_worker():
    """Test adding a worker to the team."""
    team = BaseTeam("team")
    worker = BaseWorker("worker")
    team.add_worker(worker)
    assert len(team.worker_set) == 1
    assert worker.team_id == team.ID


def test_create_worker():
    """Test creating a worker from a team."""
    team = BaseTeam("team")
    worker1 = team.create_worker(
        name="worker1",
    )
    assert worker1.name == "worker1"
    assert worker1.team_id == team.ID
    assert team.worker_set == {worker1}
    worker2 = team.create_worker(
        name="worker2",
    )
    assert team.worker_set == {worker2, worker1}


def test_initialize():
    """Test initialization/reset of BaseTeam and its workers."""
    team = BaseTeam("team")
    team.cost_record_list = [9.0, 7.2]
    w = BaseWorker("w1")
    team.worker_set = {w}
    w.state = BaseWorkerState.WORKING
    w.cost_record_list = [9.0, 7.2]
    w.assigned_task_facility_id_tuple_set = {(BaseTask("task").ID, "dummy_facility")}
    team.initialize()
    assert team.cost_record_list == []
    assert w.state == BaseWorkerState.FREE
    assert w.cost_record_list == []
    assert w.assigned_task_facility_id_tuple_set == set()


def test_add_labor_cost():
    """Test adding labor cost to the team and its workers."""
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w2 = BaseWorker("w2", cost_per_time=5.0)
    team.worker_set = {w2, w1}
    w1.state = BaseWorkerState.WORKING
    w2.state = BaseWorkerState.FREE
    team.add_labor_cost()
    assert w1.cost_record_list == [10.0]
    assert w2.cost_record_list == [0.0]
    assert team.cost_record_list == [10.0]
    team.add_labor_cost(only_working=False)
    assert team.cost_record_list == [10.0, 15.0]
    assert w1.cost_record_list == [10.0, 10.0]
    assert w2.cost_record_list == [0.0, 5.0]


def test_str():
    """Test string representation of BaseTeam."""
    print(BaseTeam("aaaaaaaa"))


@pytest.fixture(name="dummy_team_for_extracting")
def fixture_dummy_team_for_extracting():
    """Fixture for a dummy BaseTeam for extracting tests.

    Returns:
        BaseTeam: A dummy team instance with several workers.
    """
    worker1 = BaseWorker("worker1")
    worker1.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    worker2 = BaseWorker("worker2")
    worker2.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
    ]
    worker3 = BaseWorker("worker3")
    worker3.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    worker4 = BaseWorker("worker4")
    worker4.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
    ]
    worker5 = BaseWorker("worker5")
    worker5.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
    ]
    return BaseTeam("test", worker_set={worker1, worker2, worker3, worker4, worker5})


def test_extract_free_worker_set(dummy_team_for_extracting):
    """Test extracting free workers.

    Args:
        dummy_team_for_extracting (BaseTeam): The dummy team fixture.
    """
    assert len(dummy_team_for_extracting.extract_free_worker_set([5])) == 0
    assert len(dummy_team_for_extracting.extract_free_worker_set([3, 4])) == 2
    assert len(dummy_team_for_extracting.extract_free_worker_set([0, 1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_free_worker_set([0, 1, 4])) == 2


def test_extract_working_worker_set(dummy_team_for_extracting):
    """Test extracting working workers.

    Args:
        dummy_team_for_extracting (BaseTeam): The dummy team fixture.
    """
    assert len(dummy_team_for_extracting.extract_working_worker_set([0, 1])) == 1
    assert len(dummy_team_for_extracting.extract_working_worker_set([1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_working_worker_set([1, 2, 3])) == 1


def test_get_worker_set():
    """Test getting a worker set with specific parameters."""
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w2 = BaseWorker("w2", cost_per_time=5.0)
    team.worker_set = {w2, w1}
    assert (
        len(
            team.get_worker_set(
                name="test",
                ID="test",
                team_id="test",
                cost_per_time=99876,
                solo_working=True,
                workamount_skill_mean_map={},
                workamount_skill_sd_map=[],
                facility_skill_map={},
                state=BaseWorkerState.WORKING,
                cost_record_list=[],
                assigned_task_facility_id_tuple_set=set(),
                assigned_task_facility_id_tuple_set_record_list=[],
            )
        )
        == 0
    )




def test_remove_insert_absence_time_list():
    """Test removing and inserting absence time list for BaseTeam and its workers."""
    w1 = BaseWorker("w1", "----")
    w1.cost_record_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    w1.assigned_task_facility_id_tuple_set_record_list = [
        "aa",
        "bb",
        "cc",
        "dd",
        "ee",
        "ff",
    ]
    w1.state_record_list = [2, 1, 2, 1, 1, 2]

    w2 = BaseWorker("w1", "----")
    w2.cost_record_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    w2.assigned_task_facility_id_tuple_set_record_list = [
        "aa",
        "bb",
        "cc",
        "dd",
        "ee",
        "ff",
    ]
    w2.state_record_list = [2, 1, 2, 1, 1, 2]

    team = BaseTeam("aa", worker_set={w1, w2})
    team.cost_record_list = [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]

    absence_time_list = [1, 3, 4]
    team.remove_absence_time_list(absence_time_list)
    assert team.cost_record_list == [2.0, 2.0, 2.0]
    assert w1.cost_record_list == [1.0, 1.0, 1.0]
    assert w1.assigned_task_facility_id_tuple_set_record_list == ["aa", "cc", "ff"]
    assert w1.state_record_list == [2, 2, 2]
    assert w2.cost_record_list == [1.0, 1.0, 1.0]
    assert w2.assigned_task_facility_id_tuple_set_record_list == ["aa", "cc", "ff"]
    assert w2.state_record_list == [2, 2, 2]

    team.insert_absence_time_list(absence_time_list)
    assert team.cost_record_list == [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]
    assert w1.cost_record_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert w1.assigned_task_facility_id_tuple_set_record_list == [
        "aa",
        "aa",
        "cc",
        "cc",
        "cc",
        "ff",
    ]
    assert w1.state_record_list == [2, 0, 2, 0, 0, 2]
    assert w2.cost_record_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert w2.assigned_task_facility_id_tuple_set_record_list == [
        "aa",
        "aa",
        "cc",
        "cc",
        "cc",
        "ff",
    ]
    assert w2.state_record_list == [2, 0, 2, 0, 0, 2]


def test_print_mermaid_diagram(dummy_team_for_extracting):
    """Test printing Mermaid diagrams.

    Args:
        dummy_team_for_extracting (BaseTeam): The dummy team fixture.
    """
    dummy_team_for_extracting.print_mermaid_diagram(orientations="LR", subgraph=True)
    dummy_team_for_extracting.print_target_worker_mermaid_diagram(
        [
            list(dummy_team_for_extracting.worker_set)[0],
            list(dummy_team_for_extracting.worker_set)[1],
        ],
        orientations="TB",
        subgraph=True,
    )
