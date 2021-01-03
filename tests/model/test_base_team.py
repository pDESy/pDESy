#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.base_worker import BaseWorker, BaseWorkerState
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_task import BaseTask
import datetime
import os
import pytest


def test_init():
    team = BaseTeam("team")
    assert team.name == "team"
    assert len(team.ID) > 0
    assert team.worker_list == []
    assert team.targeted_task_list == []
    assert team.parent_team is None
    assert team.cost_list == []
    team.cost_list.append(1)
    assert team.cost_list == [1.0]

    w1 = BaseWorker("w1")
    t1 = BaseTask("task1")
    team1 = BaseTeam(
        "team1",
        parent_team=team,
        targeted_task_list=[t1],
        worker_list=[w1],
        cost_list=[10],
    )
    assert team1.worker_list == [w1]
    assert team1.targeted_task_list == [t1]
    assert team1.parent_team == team
    assert team1.cost_list == [10]


def test_set_parent_team():
    team = BaseTeam("team")
    team.set_parent_team(BaseTeam("xxx"))
    assert team.parent_team.name == "xxx"


def test_extend_targeted_task_list():
    team = BaseTeam("team")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    team.extend_targeted_task_list([task1, task2])
    assert team.targeted_task_list == [task1, task2]
    assert task1.allocated_team_list == [team]
    assert task2.allocated_team_list == [team]


def test_append_targeted_task():
    team = BaseTeam("team")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    team.append_targeted_task(task1)
    team.append_targeted_task(task2)
    assert team.targeted_task_list == [task1, task2]
    assert task1.allocated_team_list == [team]
    assert task2.allocated_team_list == [team]


def test_add_worker():
    team = BaseTeam("team")
    worker = BaseWorker("worker")
    team.add_worker(worker)
    assert len(team.worker_list) == 1
    assert worker.team_id == team.ID


def test_initialize():
    team = BaseTeam("team")
    team.cost_list = [9.0, 7.2]
    w = BaseWorker("w1")
    team.worker_list = [w]
    w.state = BaseWorkerState.WORKING
    w.cost_list = [9.0, 7.2]
    w.start_time_list = [0]
    w.finish_time_list = [1]
    w.assigned_task_list = [BaseTask("task")]
    team.initialize()
    assert team.cost_list == []
    assert w.state == BaseWorkerState.FREE
    assert w.cost_list == []
    assert w.start_time_list == []
    assert w.finish_time_list == []
    assert w.assigned_task_list == []


def test_add_labor_cost():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w2 = BaseWorker("w2", cost_per_time=5.0)
    team.worker_list = [w2, w1]
    w1.state = BaseWorkerState.WORKING
    w2.state = BaseWorkerState.FREE
    team.add_labor_cost()
    assert w1.cost_list == [10.0]
    assert w2.cost_list == [0.0]
    assert team.cost_list == [10.0]
    team.add_labor_cost(only_working=False)
    assert team.cost_list == [10.0, 15.0]
    assert w1.cost_list == [10.0, 10.0]
    assert w2.cost_list == [0.0, 5.0]


def test_str():
    print(BaseTeam("aaaaaaaa"))


@pytest.fixture
def dummy_team_for_extracting(scope="function"):
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
    return BaseTeam("test", worker_list=[worker1, worker2, worker3, worker4, worker5])


def test_extract_free_worker_list(dummy_team_for_extracting):
    assert len(dummy_team_for_extracting.extract_free_worker_list([5])) == 0
    assert len(dummy_team_for_extracting.extract_free_worker_list([3, 4])) == 2
    assert len(dummy_team_for_extracting.extract_free_worker_list([0, 1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_free_worker_list([0, 1, 4])) == 2


def test_extract_working_worker_list(dummy_team_for_extracting):
    assert len(dummy_team_for_extracting.extract_working_worker_list([0, 1])) == 1
    assert len(dummy_team_for_extracting.extract_working_worker_list([1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_working_worker_list([1, 2, 3])) == 1


def test_get_worker_list():
    # TODO if we have enough time for setting test case...
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w2 = BaseWorker("w2", cost_per_time=5.0)
    team.worker_list = [w2, w1]
    assert (
        len(
            team.get_worker_list(
                name="test",
                ID="test",
                team_id="test",
                cost_per_time=99876,
                solo_working=True,
                workamount_skill_mean_map={},
                workamount_skill_sd_map=[],
                facility_skill_map={},
                state=BaseWorkerState.WORKING,
                cost_list=[],
                start_time_list=[],
                finish_time_list=[],
                assigned_task_list=[],
                assigned_task_id_record=[],
            )
        )
        == 0
    )


def test_create_data_for_gantt_plotly():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w1.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    w2 = BaseWorker("w2", cost_per_time=5.0)
    w2.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    team.worker_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    team.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_create_gantt_plotly():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w1.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    w2 = BaseWorker("w2", cost_per_time=5.0)
    w2.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    team.worker_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    team.create_gantt_plotly(init_datetime, timedelta)

    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        team.create_gantt_plotly(init_datetime, timedelta, save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_create_data_for_cost_history_plotly():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseWorker("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    team.worker_list = [w1, w2]
    team.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    data = team.create_data_for_cost_history_plotly(init_datetime, timedelta)

    x = [
        (init_datetime + time * timedelta).strftime("%Y-%m-%d %H:%M:%S")
        for time in range(len(team.cost_list))
    ]
    # w1
    assert data[0].name == w1.name
    assert data[0].x == tuple(x)
    assert data[0].y == tuple(w1.cost_list)

    # w2
    assert data[1].name == w2.name
    assert data[1].x == tuple(x)
    assert data[1].y == tuple(w2.cost_list)


def test_create_cost_history_plotly():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseWorker("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    team.worker_list = [w1, w2]
    team.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    team.create_cost_history_plotly(init_datetime, timedelta)

    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        team.create_cost_history_plotly(
            init_datetime, timedelta, title="bbbbbbb", save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)
