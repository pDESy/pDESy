#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pDESy.model.base_team import BaseTeam
from pDESy.model.base_factory import BaseFactory
from pDESy.model.base_organization import BaseOrganization
from pDESy.model.base_worker import BaseWorker, BaseWorkerState
from pDESy.model.base_facility import BaseFacility, BaseFacilityState

import datetime
import pytest
import os


@pytest.fixture
def dummy_organization(scope="function"):
    c1 = BaseTeam("c1")
    w11 = BaseWorker("w11", cost_per_time=10.0)
    w12 = BaseWorker("w12", cost_per_time=5.0)
    w11.start_time_list = [0, 5]
    w11.finish_time_list = [2, 8]
    w12.start_time_list = [9]
    w12.finish_time_list = [11]
    c1.worker_list = [w11, w12]

    c2 = BaseTeam("c2")
    w2 = BaseWorker("w2", cost_per_time=5.0)
    w2.start_time_list = [9]
    w2.finish_time_list = [11]
    c2.worker_list = [w2]
    c2.parent_team = c1

    f = BaseFacility("f", cost_per_time=20.0)
    f.start_time_list = [9]
    f.finish_time_list = [11]
    factory = BaseFactory("factory", facility_list=[f])

    dummy_factory = BaseFactory("dummy")
    factory.parent_factory = dummy_factory

    organization = BaseOrganization(
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


def test_get_team_list(dummy_organization):
    # TODO if we have enough time for setting test case...
    assert (
        len(
            dummy_organization.get_team_list(
                name="test",
                ID="test",
                worker_list=[],
                targeted_task_list=[],
                parent_team=[],
                cost_list=[],
            )
        )
        == 0
    )


def test_get_factory_list(dummy_organization):
    # TODO if we have enough time for setting test case...
    assert (
        len(
            dummy_organization.get_factory_list(
                name="test",
                ID="test",
                facility_list=[],
                targeted_task_list=[],
                parent_factory=[],
                max_space_size=99876,
                cost_list=[],
                placed_component_list=[],
                placed_component_id_record=[],
            )
        )
        == 0
    )


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
    for ext in ["png"]:
        save_fig_path = "test." + ext
        dummy_organization.create_simple_gantt(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_create_data_for_gantt_plotly(dummy_organization):
    c1 = dummy_organization.team_list[0]
    w11 = c1.worker_list[0]
    w12 = c1.worker_list[1]

    c2 = dummy_organization.team_list[1]
    w2 = c2.worker_list[0]
    w2.start_time_list = [9]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    df = dummy_organization.create_data_for_gantt_plotly(init_datetime, timedelta)

    # w11 part1
    assert df[0]["Task"] == c1.name + ": " + w11.name
    assert df[0]["Start"] == (
        init_datetime + w11.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Finish"] == (
        init_datetime + (w11.finish_time_list[0] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[0]["Type"] == "Worker"

    # w11 part2
    assert df[1]["Task"] == c1.name + ": " + w11.name
    assert df[1]["Start"] == (
        init_datetime + w11.start_time_list[1] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Finish"] == (
        init_datetime + (w11.finish_time_list[1] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[1]["Type"] == "Worker"

    # w12
    assert df[2]["Task"] == c1.name + ": " + w12.name
    assert df[2]["Start"] == (
        init_datetime + w12.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[2]["Finish"] == (
        init_datetime + (w12.finish_time_list[0] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[2]["Type"] == "Worker"

    # w2
    assert df[3]["Task"] == c2.name + ": " + w2.name
    assert df[3]["Start"] == (
        init_datetime + w2.start_time_list[0] * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[3]["Finish"] == (
        init_datetime + (w2.finish_time_list[0] + 1.0) * timedelta
    ).strftime("%Y-%m-%d %H:%M:%S")
    assert df[3]["Type"] == "Worker"


def test_create_gantt_plotly(dummy_organization):
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        dummy_organization.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


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
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        dummy_organization.create_cost_history_plotly(
            init_datetime, timedelta, title="bbbbbbb", save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_get_networkx_graph(dummy_organization):
    dummy_organization.get_networkx_graph()
    dummy_organization.get_networkx_graph(view_workers=True, view_facilities=True)


def test_draw_networkx(dummy_organization):
    for ext in ["png"]:
        save_fig_path = "test." + ext
        dummy_organization.draw_networkx(
            view_workers=True, view_facilities=True, save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


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
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        dummy_organization.draw_plotly_network(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)
