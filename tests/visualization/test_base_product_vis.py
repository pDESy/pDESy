#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for visualization.product."""

import datetime
import os

import pytest

from pDESy.model.base_component import BaseComponent, BaseComponentState
from pDESy.model.base_product import BaseProduct
from pDESy.visualization import base_product_vis as product_viz


def test_product_gantt_data():
    component = BaseComponent("c1")
    component.state_record_list = [
        BaseComponentState.READY,
        BaseComponentState.WORKING,
    ]
    product = BaseProduct(component_set={component})

    data = product_viz.create_data_for_gantt_plotly(
        product,
        datetime.datetime(2024, 1, 1, 0, 0, 0),
        datetime.timedelta(days=1),
    )

    assert data
    assert any(item["State"] == "WORKING" for item in data)


def _make_product_with_components():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    product = BaseProduct(component_set={c1, c2})
    c1.state_record_list = [
        BaseComponentState.READY,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.WORKING,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
    ]
    c2.state_record_list = [
        BaseComponentState.WORKING,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    return product, c1, c2


def test_plot_simple_gantt(tmpdir):
    pytest.importorskip("matplotlib")
    product, c1, c2 = _make_product_with_components()

    save_fig_path = os.path.join(str(tmpdir), "test.png")
    product.plot_simple_gantt(
        target_id_order_list=[c1.ID, c2.ID],
        save_fig_path=save_fig_path,
    )


def test_create_gantt_plotly(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("kaleido")
    product, c1, c2 = _make_product_with_components()

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        product.create_gantt_plotly(
            init_datetime,
            timedelta,
            target_id_order_list=[c1.ID, c2.ID],
            save_fig_path=save_fig_path,
        )


def test_get_networkx_graph():
    pytest.importorskip("networkx")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})

    product.get_networkx_graph()


def test_draw_networkx(tmpdir):
    pytest.importorskip("matplotlib")
    pytest.importorskip("networkx")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})

    save_fig_path = os.path.join(str(tmpdir), "test.png")
    product.draw_networkx(save_fig_path=save_fig_path)


def test_get_node_and_edge_trace_for_plotly_network():
    pytest.importorskip("plotly")
    pytest.importorskip("networkx")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})

    product.get_node_and_edge_trace_for_plotly_network()


def test_draw_plotly_network(tmpdir):
    pytest.importorskip("plotly")
    pytest.importorskip("networkx")
    pytest.importorskip("kaleido")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})

    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        product.draw_plotly_network(save_fig_path=save_fig_path)
