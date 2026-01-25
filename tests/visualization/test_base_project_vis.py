#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for visualization.project."""

import datetime
import os

import pytest

from pDESy.model.base_project import BaseProject
from pDESy.model.base_task import BaseTaskState
from pDESy.model.base_component import BaseComponentState
from pDESy.model.base_worker import BaseWorkerState
from pDESy.model.base_facility import BaseFacilityState


def _make_project():
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
    )
    product = project.create_product("Product")
    component = product.create_component("Component")

    workflow = project.create_workflow("Workflow")
    task = workflow.create_task("Task")

    component.add_targeted_task(task)

    team = project.create_team("Team")
    team.add_targeted_task(task)
    worker = team.create_worker("Worker")

    workplace = project.create_workplace("Workplace")
    workplace.add_targeted_task(task)
    facility = workplace.create_facility("Facility")

    component.state_record_list = [
        BaseComponentState.READY,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
    ]
    task.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    worker.state_record_list = [
        BaseWorkerState.FREE,
        BaseWorkerState.WORKING,
        BaseWorkerState.FREE,
    ]
    facility.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
    ]

    return project


def test_create_gantt_plotly(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    project = _make_project()

    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        project.create_gantt_plotly(save_fig_path=save_fig_path)


def test_get_networkx_graph():
    pytest.importorskip("networkx")
    project = _make_project()
    project.get_networkx_graph(view_workers=True, view_facilities=True)


def test_draw_networkx(tmpdir):
    pytest.importorskip("matplotlib")
    pytest.importorskip("networkx")
    project = _make_project()
    save_fig_path = os.path.join(str(tmpdir), "test.png")
    project.draw_networkx(
        view_workers=True,
        view_facilities=True,
        save_fig_path=save_fig_path,
    )


def test_get_node_and_edge_trace_for_plotly_network():
    pytest.importorskip("plotly")
    pytest.importorskip("networkx")
    project = _make_project()
    project.get_node_and_edge_trace_for_plotly_network(
        view_workers=True, view_facilities=True
    )


def test_draw_plotly_network(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("networkx")
    pytest.importorskip("kaleido")
    project = _make_project()
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        project.draw_plotly_network(save_fig_path=save_fig_path)
