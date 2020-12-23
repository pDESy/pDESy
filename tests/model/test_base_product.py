#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_product import BaseProduct
from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_factory import BaseFactory
import datetime
import os


def test_init():
    c1 = BaseComponent("c1")
    product = BaseProduct([c1])
    assert product.component_list == [c1]


def test_initialize():
    c1 = BaseComponent("c1")
    product = BaseProduct([c1])
    product.initialize()


def test_str():
    print(BaseProduct([]))


def test_create_simple_gantt():
    c1 = BaseComponent("c1")
    task11 = BaseTask("task11")
    task12 = BaseTask("task12")
    c1.extend_targeted_task_list([task11, task12])
    c2 = BaseComponent("c2")
    task2 = BaseTask("task2")
    c2.append_targeted_task(task2)
    product = BaseProduct([c1, c2])

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

    for ext in ["png"]:
        save_fig_path = "test." + ext
        product.create_simple_gantt(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_create_data_for_gantt_plotly():
    c1 = BaseComponent("c1")
    task11 = BaseTask("task11")
    task12 = BaseTask("task12")
    c1.extend_targeted_task_list([task11, task12])
    c2 = BaseComponent("c2")
    task2 = BaseTask("task2")
    c2.append_targeted_task(task2)
    product = BaseProduct([c1, c2])

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


def test_check_removing_placed_factory():
    c1 = BaseComponent("c1")
    task1 = BaseTask("task1")
    c1.append_targeted_task(task1)
    c2 = BaseComponent("c2")
    task2 = BaseTask("task2")
    c2.append_targeted_task(task2)
    product = BaseProduct([c1, c2])

    f1 = BaseFactory("f1")
    f2 = BaseFactory("f2")
    c1.placed_factory = f1
    c2.placed_factory = f2
    f1.set_placed_component(c1)
    f2.set_placed_component(c2)

    # case1
    task1.state = BaseTaskState.WORKING
    task2.state = BaseTaskState.FINISHED
    product.check_removing_placed_factory()
    assert c1.placed_factory.name == "f1"
    assert c2.placed_factory is None

    # case2
    task1.state = BaseTaskState.FINISHED
    task2.state = BaseTaskState.FINISHED
    c1.append_child_component(c2)
    c1.placed_factory = f1
    c2.placed_factory = f1
    f1.placed_component_list = [c1, c2]
    product.check_removing_placed_factory()
    assert c1.placed_factory is None
    assert c2.placed_factory is None


def test_create_gantt_plotly():
    c1 = BaseComponent("c1")
    task11 = BaseTask("task11")
    task12 = BaseTask("task12")
    c1.extend_targeted_task_list([task11, task12])
    c2 = BaseComponent("c2")
    task2 = BaseTask("task2")
    c2.append_targeted_task(task2)
    product = BaseProduct([c1, c2])

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
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        product.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_get_networkx_graph():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = BaseProduct([c3, c2, c1])
    product.get_networkx_graph()
    # TODO
    # assert set(G.nodes) == set([c3, c2, c1])
    # assert set(G.edges) ==   # not yet


def test_draw_networkx():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = BaseProduct([c3, c2, c1])
    for ext in ["png"]:
        save_fig_path = "test." + ext
        product.draw_networkx(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_get_node_and_edge_trace_for_plotly_network():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = BaseProduct([c3, c2, c1])
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


def test_draw_plotly_network():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c2.parent_component_list = [c1]
    c2.child_component_list = [c3]
    product = BaseProduct([c3, c2, c1])
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        product.draw_plotly_network(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)
