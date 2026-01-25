#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for visualization.team."""

import datetime
import os

import pytest

from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorkerState
from pDESy.visualization import base_team_vis as team_viz


def test_team_gantt_data():
    team = BaseTeam("team")
    worker = team.create_worker("worker1")
    worker.state_record_list = [BaseWorkerState.FREE, BaseWorkerState.WORKING]

    data = team_viz.create_data_for_gantt_plotly(
        team,
        datetime.datetime(2024, 1, 1, 0, 0, 0),
        datetime.timedelta(days=1),
    )

    assert data
    assert any(item["State"] == "WORKING" for item in data)


def _make_team_with_workers():
    team = BaseTeam("team")
    w1 = team.create_worker("w1")
    w2 = team.create_worker("w2")
    w1.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
    ]
    w2.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
    ]
    return team, w1, w2


def test_plot_simple_gantt(tmpdir):
    pytest.importorskip("matplotlib")
    team, w1, w2 = _make_team_with_workers()
    save_fig_path = os.path.join(str(tmpdir), "test.png")
    team.plot_simple_gantt(target_id_order_list=[w1.ID, w2.ID], view_ready=True)
    team.plot_simple_gantt(
        target_id_order_list=[w1.ID, w2.ID],
        view_ready=True,
        save_fig_path=save_fig_path,
    )


def test_create_gantt_plotly(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    team, w1, w2 = _make_team_with_workers()
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        team.create_gantt_plotly(
            init_datetime,
            timedelta,
            target_id_order_list=[w1.ID, w2.ID],
            save_fig_path=save_fig_path,
        )


def test_create_data_for_cost_history_plotly():
    pytest.importorskip("plotly")
    team, _w1, _w2 = _make_team_with_workers()
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    team.create_data_for_cost_history_plotly(init_datetime, timedelta)


def test_create_cost_history_plotly(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    team, _w1, _w2 = _make_team_with_workers()
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        team.create_cost_history_plotly(
            init_datetime,
            timedelta,
            save_fig_path=save_fig_path,
        )
