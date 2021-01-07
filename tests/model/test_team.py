#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.worker import Worker
from pDESy.model.team import Team
from pDESy.model.task import Task
from pDESy.model.base_worker import BaseWorkerState
import datetime


def test_init():
    team = Team("team")
    assert team.name == "team"
    assert len(team.ID) > 0
    assert team.worker_list == []
    assert team.targeted_task_list == []
    assert team.parent_team is None
    assert team.cost_list == []
    team.cost_list.append(1)
    assert team.cost_list == [1.0]

    w1 = Worker("w1")
    t1 = Task("task1")
    team1 = Team(
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
    team = Team("team")
    team.set_parent_team(Team("xxx"))
    assert team.parent_team.name == "xxx"


def test_extend_targeted_task_list():
    team = Team("team")
    task1 = Task("task1")
    task2 = Task("task2")
    team.extend_targeted_task_list([task1, task2])
    assert team.targeted_task_list == [task1, task2]
    assert task1.allocated_team_list == [team]
    assert task2.allocated_team_list == [team]


def test_append_targeted_task():
    team = Team("team")
    task1 = Task("task1")
    task2 = Task("task2")
    team.append_targeted_task(task1)
    team.append_targeted_task(task2)
    assert team.targeted_task_list == [task1, task2]
    assert task1.allocated_team_list == [team]
    assert task2.allocated_team_list == [team]


def test_initialize():
    team = Team("team")
    team.cost_list = [9.0, 7.2]
    w = Worker("w1")
    team.worker_list = [w]
    w.state = BaseWorkerState.WORKING
    w.cost_list = [9.0, 7.2]
    w.assigned_task_list = [Task("task")]
    team.initialize()
    assert team.cost_list == []
    assert w.state == BaseWorkerState.FREE
    assert w.cost_list == []
    assert w.assigned_task_list == []


def test_add_labor_cost():
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w2 = Worker("w2", cost_per_time=5.0)
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
    print(Team("aaaaaaaa"))


def test_create_data_for_gantt_plotly():
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w1.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    w2 = Worker("w2", cost_per_time=5.0)
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
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w1.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    w2 = Worker("w2", cost_per_time=5.0)
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

    # not yet implemented
    team.create_gantt_plotly(init_datetime, timedelta, save_fig_path="test.png")


def test_create_data_for_cost_history_plotly():
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = Worker("w2", cost_per_time=5.0)
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
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = Worker("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    team.worker_list = [w1, w2]
    team.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    team.create_cost_history_plotly(init_datetime, timedelta)
    team.create_cost_history_plotly(init_datetime, timedelta, title="bbbbbbb")
