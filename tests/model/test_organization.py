#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pDESy.model.team import Team
from pDESy.model.base_factory import BaseFactory
from pDESy.model.organization import Organization
from pDESy.model.worker import Worker
from pDESy.model.base_worker import BaseWorkerState
from pDESy.model.base_facility import BaseFacility, BaseFacilityState
import datetime

import pytest
import os


@pytest.fixture
def dummy_organization(scope="function"):
    c1 = Team("c1")
    w11 = Worker("w11", cost_per_time=10.0)
    w12 = Worker("w12", cost_per_time=5.0)
    w11.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    w12.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    c1.worker_list = [w11, w12]

    c2 = Team("c2")
    w2 = Worker("w2", cost_per_time=5.0)
    w2.state_record_list = [
        BaseWorkerState.WORKING,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
    ]
    c2.worker_list = [w2]
    c2.parent_team = c1

    f = BaseFacility("f", cost_per_time=20.0)
    f.state_record_list = [
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    factory = BaseFactory("factory", facility_list=[f])

    dummy_factory = BaseFactory("dummy")
    factory.parent_factory = dummy_factory

    organization = Organization(
        team_list=[c1, c2], factory_list=[factory, dummy_factory]
    )
    return organization


def test_init(dummy_organization):
    assert [team.name for team in dummy_organization.team_list] == ["c1", "c2"]
    assert [factory.name for factory in dummy_organization.factory_list] == [
        "factory",
        "dummy",
    ]


def test_initialize(dummy_organization):
    team = dummy_organization.team_list[0]
    factory = dummy_organization.factory_list[0]
    team.cost_list = [4.0]
    factory.cost_list = [4.0]
    dummy_organization.cost_list = [8.0]
    assert team.cost_list == [4.0]
    assert factory.cost_list == [4.0]
    assert dummy_organization.cost_list == [8.0]
    dummy_organization.initialize()
    assert team.cost_list == []
    assert factory.cost_list == []
    assert dummy_organization.cost_list == []


def test_str(dummy_organization):
    print(dummy_organization)


def test_add_labor_cost(dummy_organization):
    w11 = dummy_organization.team_list[0].worker_list[0]
    w12 = dummy_organization.team_list[0].worker_list[1]
    w21 = dummy_organization.team_list[1].worker_list[0]
    facility = dummy_organization.factory_list[0].facility_list[0]
    w11.state = BaseWorkerState.WORKING
    w12.state = BaseWorkerState.FREE
    w21.state = BaseWorkerState.WORKING
    facility.state = BaseFacilityState.WORKING
    dummy_organization.add_labor_cost(
        only_working=False,
        add_zero_to_all_workers=False,
        add_zero_to_all_facilities=False,
    )
    assert dummy_organization.cost_list == [40.0]
    dummy_organization.add_labor_cost(
        only_working=False,
        add_zero_to_all_workers=True,
        add_zero_to_all_facilities=True,
    )
    assert dummy_organization.cost_list == [40.0, 0.0]
    dummy_organization.add_labor_cost(
        only_working=True,
        add_zero_to_all_workers=False,
        add_zero_to_all_facilities=False,
    )
    assert dummy_organization.cost_list == [40.0, 0.0, 35.0]


def test_create_simple_gantt(dummy_organization):
    dummy_organization.create_simple_gantt(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_create_data_for_gantt_plotly(dummy_organization):
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    dummy_organization.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_create_gantt_plotly(dummy_organization):
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    dummy_organization.create_gantt_plotly(
        init_datetime, timedelta, save_fig_path="test.png"
    )
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_create_data_for_cost_history_plotly(dummy_organization):
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    data = dummy_organization.create_data_for_cost_history_plotly(
        init_datetime, timedelta
    )
    x = [
        (init_datetime + time * timedelta).strftime("%Y-%m-%d %H:%M:%S")
        for time in range(len(dummy_organization.cost_list))
    ]
    # w1
    assert data[0].name == dummy_organization.team_list[0].name
    assert data[0].x == tuple(x)
    assert data[0].y == tuple(dummy_organization.team_list[0].cost_list)


def test_create_cost_history_plotly(dummy_organization):
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    dummy_organization.create_cost_history_plotly(init_datetime, timedelta)
    dummy_organization.create_cost_history_plotly(
        init_datetime, timedelta, title="bbbbbbb", save_fig_path="test.png"
    )
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_networkx_graph(dummy_organization):
    dummy_organization.get_networkx_graph()
    dummy_organization.get_networkx_graph(view_workers=True, view_facilities=True)


def test_draw_networkx(dummy_organization):
    dummy_organization.draw_networkx(
        view_workers=True, view_facilities=True, save_fig_path="test.png"
    )
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_node_and_edge_trace_for_plotly_network(dummy_organization):
    (
        team_node_trace,
        worker_node_trace,
        factory_node_trace,
        facility_node_trace,
        edge_trace,
    ) = dummy_organization.get_node_and_edge_trace_for_plotly_network()
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
    (
        team_node_trace,
        worker_node_trace,
        factory_node_trace,
        facility_node_trace,
        edge_trace,
    ) = dummy_organization.get_node_and_edge_trace_for_plotly_network(
        view_workers=True, view_facilities=True
    )
    # TODO
    # assert...


def test_draw_plotly_network(dummy_organization):
    dummy_organization.draw_plotly_network(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")
