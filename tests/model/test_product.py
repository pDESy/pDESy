#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_product."""

import datetime
import os

from pDESy.model.base_component import BaseComponentState
from pDESy.model.component import Component
from pDESy.model.product import Product


def test_init():
    """test_init."""
    c1 = Component("c1")
    product = Product([c1])
    assert product.component_list == [c1]


def test_initialize():
    """test_initialize."""
    c1 = Component("c1")
    c1.error = 4.0
    product = Product([c1])
    product.initialize()
    assert c1.error == 0.0


def test_str():
    """test_str."""
    print(Product([]))


def test_plot_simple_gantt(tmpdir):
    """test_plot_simple_gantt."""
    c1 = Component("c1")
    c1.state_record_list = [
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    c1.create_data_for_gantt_plotly(init_datetime, timedelta)
    product = Product([c1])
    product.plot_simple_gantt(save_fig_path=os.path.join(str(tmpdir), "test.png"))


def test_create_data_for_gantt_plotly():
    """test_create_data_for_gantt_plotly."""
    c1 = Component("c1")
    c1.state_record_list = [
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    product = Product([c1])
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    product.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_create_gantt_plotly(tmpdir):
    """test_create_gantt_plotly."""
    c1 = Component("c1")
    c1.state_record_list = [
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    product = Product([c1])

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    product.create_gantt_plotly(
        init_datetime, timedelta, save_fig_path=os.path.join(str(tmpdir), "test.png")
    )


def test_get_networkx_graph():
    """test_get_networkx_graph."""
    c1 = Component("c1")
    c2 = Component("c2")
    c3 = Component("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = Product([c3, c2, c1])
    product.get_networkx_graph()
    # TODO
    # assert set(G.nodes) == set([c3, c2, c1])
    # assert set(G.edges) ==   # not yet


def test_draw_networkx(tmpdir):
    """test_draw_networkx."""
    c1 = Component("c1")
    c2 = Component("c2")
    c3 = Component("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = Product([c3, c2, c1])
    product.draw_networkx(save_fig_path=os.path.join(str(tmpdir), "test.png"))


def test_get_node_and_edge_trace_for_plotly_network():
    """test_get_node_and_edge_trace_for_plotly_network."""
    c1 = Component("c1")
    c2 = Component("c2")
    c3 = Component("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = Product([c3, c2, c1])
    node_trace, edge_trace = product.get_node_and_edge_trace_for_plotly_network()
    # TODO
    # assert node_trace["x"] == (-0.3579082411734774, -0.6420917588265226, 1.0)
    # assert node_trace["y"] == (
    #     0.12291614192037693,
    #     -0.17634885928791186,
    #     0.05343271736753491,
    # )
    # assert node_trace["text"] == ("c3", "c2", "c1")
    # assert edge_trace["x"] == (-0.3579082411734774, -0.6420917588265226)
    # assert edge_trace["y"] == (0.12291614192037693, -0.17634885928791186)


def test_draw_plotly_network(tmpdir):
    """test_draw_plotly_network."""
    c1 = Component("c1")
    c2 = Component("c2")
    c3 = Component("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = Product([c3, c2, c1])
    product.draw_plotly_network(save_fig_path=os.path.join(str(tmpdir), "test.png"))
