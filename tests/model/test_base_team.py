#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_task import BaseTask
from pDESy.model.base_resource import BaseResourceState
import datetime
import os


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
    w.state = BaseResourceState.WORKING
    w.cost_list = [9.0, 7.2]
    w.start_time_list = [0]
    w.finish_time_list = [1]
    w.assigned_task_list = [BaseTask("task")]
    team.initialize()
    assert team.cost_list == []
    assert w.state == BaseResourceState.FREE
    assert w.cost_list == []
    assert w.start_time_list == []
    assert w.finish_time_list == []
    assert w.assigned_task_list == []


def test_add_labor_cost():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w2 = BaseWorker("w2", cost_per_time=5.0)
    team.worker_list = [w2, w1]
    w1.state = BaseResourceState.WORKING
    w2.state = BaseResourceState.FREE
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


def test_create_data_for_gantt_plotly():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w1.start_time_list = [0, 5]
    w1.finish_time_list = [2, 8]
    w2 = BaseWorker("w2", cost_per_time=5.0)
    w2.start_time_list = [9]
    w2.finish_time_list = [11]
    team.worker_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    df = team.create_data_for_gantt_plotly(init_datetime, timedelta)
    # w1 part1
    assert df[0]["Task"] == team.name + ": " + w1.name
    assert df[0]["Start"] == (
        init_datetime + w1.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Finish"] == (
        init_datetime + (w1.finish_time_list[0] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Type"] == "Worker"

    # w1 part2
    assert df[1]["Task"] == team.name + ": " + w1.name
    assert df[1]["Start"] == (
        init_datetime + w1.start_time_list[1] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Finish"] == (
        init_datetime + (w1.finish_time_list[1] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Type"] == "Worker"

    # w2
    assert df[2]["Start"] == (
        init_datetime + w2.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[2]["Finish"] == (
        init_datetime + (w2.finish_time_list[0] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[2]["Type"] == "Worker"


def test_create_gantt_plotly():
    team = BaseTeam("team")
    w1 = BaseWorker("w1", cost_per_time=10.0)
    w1.start_time_list = [0, 5]
    w1.finish_time_list = [2, 8]
    w2 = BaseWorker("w2", cost_per_time=5.0)
    w2.start_time_list = [9]
    w2.finish_time_list = [11]
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
