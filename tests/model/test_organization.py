#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pDESy.model.team import Team
from pDESy.model.organization import Organization
from pDESy.model.worker import Worker
import datetime
from pDESy.model.base_resource import BaseResourceState


def test_init():
    c1 = Team("c1")
    organization = Organization([c1])
    assert organization.team_list == [c1]


def test_initialize():
    c1 = Team("c1")
    c1.cost_list = [4.0]
    organization = Organization([c1])
    organization.cost_list = [4.0]
    assert c1.cost_list == [4.0]
    assert organization.cost_list == [4.0]
    organization.initialize()
    assert c1.cost_list == []
    assert organization.cost_list == []


def test_str():
    print(Organization([]))


def test_add_labor_cost():
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w2 = Worker("w2", cost_per_time=5.0)
    team.worker_list = [w2, w1]
    w1.state = BaseResourceState.WORKING
    w2.state = BaseResourceState.FREE
    organization = Organization([team])
    organization.add_labor_cost()
    assert organization.cost_list == [10.0]


def test_create_data_for_gantt_plotly():
    c1 = Team("c1")
    w11 = Worker("w11", cost_per_time=10.0)
    w12 = Worker("w12", cost_per_time=5.0)
    w11.start_time_list = [0, 5]
    w11.finish_time_list = [2, 8]
    w12.start_time_list = [9]
    w12.finish_time_list = [11]
    c1.worker_list = [w11, w12]

    c2 = Team("c2")
    w2 = Worker("w2", cost_per_time=5.0)
    w2.start_time_list = [9]
    w2.finish_time_list = [11]
    c2.worker_list = [w2]
    organization = Organization([c1, c2])

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    df = organization.create_data_for_gantt_plotly(init_datetime, timedelta)

    # w11 part1
    assert df[0]["Task"] == c1.name + ": " + w11.name
    assert df[0]["Start"] == (
        init_datetime + w11.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Finish"] == (
        init_datetime + (w11.finish_time_list[0] + 0.9) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Type"] == "Worker"

    # w11 part2
    assert df[1]["Task"] == c1.name + ": " + w11.name
    assert df[1]["Start"] == (
        init_datetime + w11.start_time_list[1] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Finish"] == (
        init_datetime + (w11.finish_time_list[1] + 0.9) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Type"] == "Worker"

    # w12
    assert df[2]["Task"] == c1.name + ": " + w12.name
    assert df[2]["Start"] == (
        init_datetime + w12.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[2]["Finish"] == (
        init_datetime + (w12.finish_time_list[0] + 0.9) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[2]["Type"] == "Worker"

    # w2
    assert df[3]["Task"] == c2.name + ": " + w2.name
    assert df[3]["Start"] == (
        init_datetime + w2.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[3]["Finish"] == (
        init_datetime + (w2.finish_time_list[0] + 0.9) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[3]["Type"] == "Worker"


def test_create_gantt_plotly():
    c1 = Team("c1")
    w11 = Worker("w11", cost_per_time=10.0)
    w12 = Worker("w12", cost_per_time=5.0)
    w11.start_time_list = [0, 5]
    w11.finish_time_list = [2, 8]
    w12.start_time_list = [9]
    w12.finish_time_list = [11]
    c1.worker_list = [w11, w12]

    c2 = Team("c2")
    w2 = Worker("w2", cost_per_time=5.0)
    w2.start_time_list = [9]
    w2.finish_time_list = [11]
    c2.worker_list = [w2]
    organization = Organization([c1, c2])

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    organization.create_gantt_plotly(init_datetime, timedelta)


def test_create_data_for_cost_history_plotly():
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = Worker("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    team.worker_list = [w1, w2]
    team.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))
    organization = Organization([team])
    organization.cost_list == team.cost_list
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    data = organization.create_data_for_cost_history_plotly(init_datetime, timedelta)
    x = [
        (init_datetime + time * timedelta).strftime("%Y-%m-%d %H:%M:%S")
        for time in range(len(organization.cost_list))
    ]
    # w1
    assert data[0].name == team.name
    assert data[0].x == tuple(x)
    assert data[0].y == tuple(team.cost_list)


def test_create_cost_history_plotly():
    team = Team("team")
    w1 = Worker("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = Worker("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    team.worker_list = [w1, w2]
    team.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))
    organization = Organization([team])

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    organization.create_cost_history_plotly(init_datetime, timedelta)
    organization.create_cost_history_plotly(init_datetime, timedelta, title="bbbbbbb")


def test_get_networkx_graph():
    c1 = Team("c1")
    w2 = Worker("w2")
    c2 = Team("c2", worker_list=[w2])
    c3 = Team("c3")
    c2.depended_Team_list = [c1]
    c2.depending_Team_list = [c3]
    organization = Organization([c3, c2, c1])
    organization.get_networkx_graph()
    # TODO
    # assert set(G.nodes) == set([c3, c2, c1])
    # assert set(G.edges) ==   # not yet

    organization.get_networkx_graph(view_workers=True)


def test_draw_networkx():
    c1 = Team("c1")
    c2 = Team("c2")
    c3 = Team("c3")
    c2.depended_Team_list = [c1]
    c2.depending_Team_list = [c3]
    organization = Organization([c3, c2, c1])
    organization.draw_networkx()


def test_get_node_and_edge_trace_for_ploty_network():
    c1 = Team("c1")
    c2 = Team("c2")
    c3 = Team("c3")
    c2.depended_team_list = [c1]
    c2.depending_team_list = [c3]
    organization = Organization([c3, c2, c1])
    node_trace, edge_trace = organization.get_node_and_edge_trace_for_ploty_network()
    # TODO
    # assert node_trace["x"] == (
    #     0.6430634353668857,
    #     -0.1450984764057351,
    #     -0.49796495896115067,
    # )
    # assert node_trace["y"] == (
    #     0.12291614192037693,
    #     -0.17634885928791186,
    #     0.05343271736753491,
    # )
    # assert node_trace["text"] == ("c3", "c2", "c1")
    # assert edge_trace["x"] == (-0.3579082411734774, -0.6420917588265226)
    # assert edge_trace["y"] == (0.12291614192037693, -0.17634885928791186)


def test_draw_plotly_network():
    c1 = Team("c1")
    c2 = Team("c2")
    c3 = Team("c3")
    c2.depended_Team_list = [c1]
    c2.depending_Team_list = [c3]
    organization = Organization([c3, c2, c1])
    organization.draw_plotly_network()
