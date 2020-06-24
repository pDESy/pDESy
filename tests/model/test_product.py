#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pDESy.model.component import Component
from pDESy.model.product import Product
from pDESy.model.task import Task
import datetime
import os


def test_init():
    c1 = Component("c1")
    product = Product([c1])
    assert product.component_list == [c1]


def test_initialize():
    c1 = Component("c1")
    c1.error = 4.0
    product = Product([c1])
    product.initialize()
    assert c1.error == 0.0


def test_str():
    print(Product([]))


def test_create_simple_gantt():
    c1 = Component("c1")
    task11 = Task("task11")
    task12 = Task("task12")
    c1.extend_targeted_task_list([task11, task12])
    c2 = Component("c2")
    task2 = Task("task2")
    c2.append_targeted_task(task2)
    product = Product([c1, c2])

    # Set test case
    task11.start_time_list = [1, 5]
    task11.ready_time_list = [0, 4]
    task11.finish_time_list = [2, 6]
    task12.start_time_list = [2]
    task12.ready_time_list = [1]
    task12.finish_time_list = [5]
    task2.start_time_list = [2]
    task2.ready_time_list = [1]
    task2.finish_time_list = [5]

    product.create_simple_gantt(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_create_data_for_gantt_plotly():
    c1 = Component("c1")
    task11 = Task("task11")
    task12 = Task("task12")
    c1.extend_targeted_task_list([task11, task12])
    c2 = Component("c2")
    task2 = Task("task2")
    c2.append_targeted_task(task2)
    product = Product([c1, c2])

    # Set test case
    task11.start_time_list = [0, 2]
    task11.ready_time_list = [0, 2]
    task11.finish_time_list = [3, 5]
    task12.start_time_list = [1]
    task12.ready_time_list = [2]
    task12.finish_time_list = [5]
    task2.start_time_list = [1]
    task2.ready_time_list = [2]
    task2.finish_time_list = [5]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    df = product.create_data_for_gantt_plotly(init_datetime, timedelta)
    assert df[0]["Start"] == (init_datetime + 0 * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[0]["Finish"] == (init_datetime + (5 + 1.0) * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[0]["Type"] == "Component"
    assert df[1]["Start"] == (init_datetime + 1 * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[1]["Finish"] == (init_datetime + (5 + 1.0) * timedelta).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    assert df[1]["Type"] == "Component"


def test_create_gantt_plotly():
    c1 = Component("c1")
    task11 = Task("task11")
    task12 = Task("task12")
    c1.extend_targeted_task_list([task11, task12])
    c2 = Component("c2")
    task2 = Task("task2")
    c2.append_targeted_task(task2)
    product = Product([c1, c2])

    # Set test case
    task11.start_time_list = [0, 2]
    task11.ready_time_list = [0, 2]
    task11.finish_time_list = [3, 5]
    task12.start_time_list = [1]
    task12.ready_time_list = [2]
    task12.finish_time_list = [5]
    task2.start_time_list = [1]
    task2.ready_time_list = [2]
    task2.finish_time_list = [5]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    product.create_gantt_plotly(init_datetime, timedelta, save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_networkx_graph():
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


def test_draw_networkx():
    c1 = Component("c1")
    c2 = Component("c2")
    c3 = Component("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = Product([c3, c2, c1])
    product.draw_networkx(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_node_and_edge_trace_for_ploty_network():
    c1 = Component("c1")
    c2 = Component("c2")
    c3 = Component("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = Product([c3, c2, c1])
    node_trace, edge_trace = product.get_node_and_edge_trace_for_ploty_network()
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


def test_draw_plotly_network():
    c1 = Component("c1")
    c2 = Component("c2")
    c3 = Component("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = Product([c3, c2, c1])
    product.draw_plotly_network(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")
