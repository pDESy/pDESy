#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for visualization.workplace."""

import datetime
import os

import pytest

from pDESy.model.base_facility import BaseFacilityState
from pDESy.model.base_workplace import BaseWorkplace
from pDESy.visualization import base_workplace_vis as workplace_viz


def test_workplace_gantt_data():
    workplace = BaseWorkplace("workplace")
    facility = workplace.create_facility("facility1")
    facility.state_record_list = [BaseFacilityState.FREE, BaseFacilityState.WORKING]

    data = workplace_viz.create_data_for_gantt_plotly(
        workplace,
        datetime.datetime(2024, 1, 1, 0, 0, 0),
        datetime.timedelta(days=1),
    )

    assert data
    assert any(item["State"] == "WORKING" for item in data)


def _make_workplace_with_facilities():
    workplace = BaseWorkplace("workplace")
    f1 = workplace.create_facility("f1")
    f2 = workplace.create_facility("f2")
    f1.state_record_list = [BaseFacilityState.FREE, BaseFacilityState.WORKING]
    f2.state_record_list = [BaseFacilityState.FREE, BaseFacilityState.WORKING]
    return workplace, f1, f2


def test_plot_simple_gantt(tmpdir):
    pytest.importorskip("matplotlib")
    workplace, f1, f2 = _make_workplace_with_facilities()
    save_fig_path = os.path.join(str(tmpdir), "test.png")
    workplace.plot_simple_gantt(
        target_id_order_list=[f1.ID, f2.ID],
        view_ready=True,
        save_fig_path=save_fig_path,
    )


def test_create_gantt_plotly(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    workplace, f1, f2 = _make_workplace_with_facilities()
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        workplace.create_gantt_plotly(
            init_datetime,
            timedelta,
            target_id_order_list=[f1.ID, f2.ID],
            save_fig_path=save_fig_path,
        )


def test_create_data_for_cost_history_plotly():
    pytest.importorskip("plotly")
    workplace, _f1, _f2 = _make_workplace_with_facilities()
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    workplace.create_data_for_cost_history_plotly(init_datetime, timedelta)


def test_create_cost_history_plotly(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    workplace, _f1, _f2 = _make_workplace_with_facilities()
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        workplace.create_cost_history_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )
