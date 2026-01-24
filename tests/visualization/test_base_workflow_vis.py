#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for visualization.workflow."""

import datetime
import os

import pytest

from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_workflow import BaseWorkflow
from pDESy.visualization import base_workflow_vis as workflow_viz


def test_workflow_gantt_data():
    workflow = BaseWorkflow("wf")
    task = BaseTask("task1")
    task.state_record_list = [BaseTaskState.READY, BaseTaskState.WORKING]
    workflow.task_set = {task}

    data = workflow_viz.create_data_for_gantt_plotly(
        workflow,
        datetime.datetime(2024, 1, 1, 0, 0, 0),
        datetime.timedelta(days=1),
    )

    assert data
    assert any(item["State"] == "WORKING" for item in data)


def _make_workflow():
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    task3 = BaseTask("task3")
    task4 = BaseTask("task4")
    task5 = BaseTask("task5")
    task3.update_input_task_set({task1, task2})
    task5.add_input_task(task3)
    task5.add_input_task(task4)
    w = BaseWorkflow(task_set={task1, task2, task3, task4, task5})
    return w


def test_plot_simple_gantt(tmpdir):
    pytest.importorskip("matplotlib")
    w = _make_workflow()
    task0 = BaseTask("auto", auto_task=True)
    w.task_set.add(task0)

    for task in w.task_set:
        task.state_record_list = [
            BaseTaskState.READY,
            BaseTaskState.WORKING,
            BaseTaskState.FINISHED,
        ]

    save_fig_path = os.path.join(str(tmpdir), "test.png")
    w.plot_simple_gantt(finish_margin=1.0, view_auto_task=True, view_ready=False)
    w.plot_simple_gantt(
        finish_margin=1.0,
        view_auto_task=True,
        view_ready=False,
        save_fig_path=save_fig_path,
    )


def test_create_gantt_plotly(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    w = _make_workflow()
    for task in w.task_set:
        task.state_record_list = [
            BaseTaskState.READY,
            BaseTaskState.WORKING,
            BaseTaskState.FINISHED,
        ]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        w.create_gantt_plotly(
            init_datetime,
            timedelta,
            target_id_order_list=[task.ID for task in w.task_set],
            save_fig_path=save_fig_path,
        )


def test_get_networkx_graph():
    pytest.importorskip("networkx")
    w = _make_workflow()
    w.get_networkx_graph()


def test_draw_networkx(tmpdir):
    pytest.importorskip("matplotlib")
    pytest.importorskip("networkx")
    w = _make_workflow()
    save_fig_path = os.path.join(str(tmpdir), "test.png")
    w.draw_networkx(save_fig_path=save_fig_path)


def test_get_node_and_edge_trace_for_plotly_network():
    pytest.importorskip("plotly")
    pytest.importorskip("networkx")
    w = _make_workflow()
    w.get_node_and_edge_trace_for_plotly_network()


def test_draw_plotly_network(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("networkx")
    pytest.importorskip("kaleido")
    w = _make_workflow()
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        w.draw_plotly_network(save_fig_path=save_fig_path)
