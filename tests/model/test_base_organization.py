#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_base_organization."""

import datetime
import os

from pDESy.model.base_facility import BaseFacility, BaseFacilityState
from pDESy.model.base_organization import BaseOrganization
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorker, BaseWorkerState
from pDESy.model.base_workplace import BaseWorkplace

import pytest


@pytest.fixture
def dummy_organization(scope="function"):
    """dummy_organization."""
    c1 = BaseTeam("c1")
    w11 = BaseWorker("w11", cost_per_time=10.0)
    w12 = BaseWorker("w12", cost_per_time=5.0)
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

    c2 = BaseTeam("c2")
    w2 = BaseWorker("w2", cost_per_time=5.0)
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
    workplace = BaseWorkplace("workplace", facility_list=[f])

    dummy_workplace = BaseWorkplace("dummy")
    workplace.parent_workplace = dummy_workplace

    organization = BaseOrganization(
        team_list=[c1, c2], workplace_list=[workplace, dummy_workplace]
    )
    return organization


def test_init(dummy_organization):
    """test_init."""
    assert [team.name for team in dummy_organization.team_list] == ["c1", "c2"]
    assert [workplace.name for workplace in dummy_organization.workplace_list] == [
        "workplace",
        "dummy",
    ]


def test_initialize(dummy_organization):
    """test_initialize."""
    team = dummy_organization.team_list[0]
    workplace = dummy_organization.workplace_list[0]
    team.cost_list = [4.0]
    workplace.cost_list = [4.0]
    dummy_organization.cost_list = [8.0]
    assert team.cost_list == [4.0]
    assert workplace.cost_list == [4.0]
    assert dummy_organization.cost_list == [8.0]
    dummy_organization.initialize()
    assert team.cost_list == []
    assert workplace.cost_list == []
    assert dummy_organization.cost_list == []


def test_str(dummy_organization):
    """test_str."""
    print(dummy_organization)


def test_get_team_list(dummy_organization):
    """test_get_team_list."""
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


def test_get_workplace_list(dummy_organization):
    """test_get_workplace_list."""
    # TODO if we have enough time for setting test case...
    assert (
        len(
            dummy_organization.get_workplace_list(
                name="test",
                ID="test",
                facility_list=[],
                targeted_task_list=[],
                parent_workplace=[],
                max_space_size=99876,
                cost_list=[],
                placed_component_list=[],
                placed_component_id_record=[],
            )
        )
        == 0
    )


def test_add_labor_cost(dummy_organization):
    """test_add_labor_cost."""
    w11 = dummy_organization.team_list[0].worker_list[0]
    w12 = dummy_organization.team_list[0].worker_list[1]
    w21 = dummy_organization.team_list[1].worker_list[0]
    facility = dummy_organization.workplace_list[0].facility_list[0]
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


def test_plot_simple_gantt(dummy_organization, tmpdir):
    """test_plot_simple_gantt."""
    for ext in ["png"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_organization.plot_simple_gantt(save_fig_path=save_fig_path)


def test_create_data_for_gantt_plotly(dummy_organization):
    """test_create_data_for_gantt_plotly."""
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    dummy_organization.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_create_gantt_plotly(dummy_organization, tmpdir):
    """test_create_gantt_plotly."""
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_organization.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )


def test_create_data_for_cost_history_plotly(dummy_organization):
    """test_create_data_for_cost_history_plotly."""
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


def test_create_cost_history_plotly(dummy_organization, tmpdir):
    """test_create_cost_history_plotly."""
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    dummy_organization.create_cost_history_plotly(init_datetime, timedelta)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_organization.create_cost_history_plotly(
            init_datetime, timedelta, title="bbbbbbb", save_fig_path=save_fig_path
        )


def test_get_networkx_graph(dummy_organization):
    """test_get_networkx_graph."""
    dummy_organization.get_networkx_graph()
    dummy_organization.get_networkx_graph(view_workers=True, view_facilities=True)


def test_draw_networkx(dummy_organization, tmpdir):
    """test_draw_networkx."""
    for ext in ["png"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_organization.draw_networkx(
            view_workers=True, view_facilities=True, save_fig_path=save_fig_path
        )


def test_get_node_and_edge_trace_for_plotly_network(dummy_organization):
    """test_get_node_and_edge_trace_for_plotly_network."""
    (
        team_node_trace,
        worker_node_trace,
        workplace_node_trace,
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
        workplace_node_trace,
        facility_node_trace,
        edge_trace,
    ) = dummy_organization.get_node_and_edge_trace_for_plotly_network(
        view_workers=True, view_facilities=True
    )
    # TODO
    # assert...


def test_draw_plotly_network(dummy_organization, tmpdir):
    """test_draw_plotly_network."""
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_organization.draw_plotly_network(save_fig_path=save_fig_path)


def test_remove_insert_absence_time_list():
    """test_remove_insert_absence_time_list."""
    f1 = BaseFacility("w1", "----")
    f1.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    f1.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    f1.state_record_list = [2, 1, 2, 1, 1, 2]

    f2 = BaseFacility("w1", "----")
    f2.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    f2.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    f2.state_record_list = [2, 1, 2, 1, 1, 2]

    workplace = BaseWorkplace("aa", facility_list=[f1, f2])
    workplace.cost_list = [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]

    w1 = BaseWorker("w1", "----")
    w1.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    w1.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w1.state_record_list = [2, 1, 2, 1, 1, 2]

    w2 = BaseWorker("w1", "----")
    w2.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    w2.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    w2.state_record_list = [2, 1, 2, 1, 1, 2]

    team = BaseTeam("aa", worker_list=[w1, w2])
    team.cost_list = [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]

    organization = BaseOrganization(team_list=[team], workplace_list=[workplace])
    organization.cost_list = [4.0, 0.0, 4.0, 0.0, 0.0, 4.0]

    absence_time_list = [1, 3, 4]
    organization.remove_absence_time_list(absence_time_list)
    assert organization.cost_list == [4.0, 4.0, 4.0]
    assert workplace.cost_list == [2.0, 2.0, 2.0]
    assert f1.cost_list == [1.0, 1.0, 1.0]
    assert f1.assigned_task_id_record == ["aa", "cc", "ff"]
    assert f1.state_record_list == [2, 2, 2]
    assert f2.cost_list == [1.0, 1.0, 1.0]
    assert f2.assigned_task_id_record == ["aa", "cc", "ff"]
    assert f2.state_record_list == [2, 2, 2]
    assert team.cost_list == [2.0, 2.0, 2.0]
    assert w1.cost_list == [1.0, 1.0, 1.0]
    assert w1.assigned_task_id_record == ["aa", "cc", "ff"]
    assert w1.state_record_list == [2, 2, 2]
    assert w2.cost_list == [1.0, 1.0, 1.0]
    assert w2.assigned_task_id_record == ["aa", "cc", "ff"]
    assert w2.state_record_list == [2, 2, 2]

    organization.insert_absence_time_list(absence_time_list)
    assert organization.cost_list == [4.0, 0.0, 4.0, 0.0, 0.0, 4.0]
    assert team.cost_list == [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]
    assert w1.cost_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert w1.assigned_task_id_record == ["aa", "aa", "cc", "cc", "cc", "ff"]
    assert w1.state_record_list == [2, 0, 2, 0, 0, 2]
    assert w2.cost_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert w2.assigned_task_id_record == ["aa", "aa", "cc", "cc", "cc", "ff"]
    assert w2.state_record_list == [2, 0, 2, 0, 0, 2]
    assert workplace.cost_list == [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]
    assert f1.cost_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert f1.assigned_task_id_record == ["aa", "aa", "cc", "cc", "cc", "ff"]
    assert f1.state_record_list == [2, 0, 2, 0, 0, 2]
    assert f2.cost_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert f2.assigned_task_id_record == ["aa", "aa", "cc", "cc", "cc", "ff"]
    assert f2.state_record_list == [2, 0, 2, 0, 0, 2]


def test_print_mermaid_diagram(dummy_organization):
    """test_print_mermaid_diagram."""
    dummy_organization.print_mermaid_diagram(orientations="LR", subgraph=True)
