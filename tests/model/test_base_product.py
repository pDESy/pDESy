#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pDESy.model.base_component import BaseComponent, BaseComponentState
from pDESy.model.base_product import BaseProduct
from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_workplace import BaseWorkplace
import datetime
import os
import pytest


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


@pytest.fixture
def dummy_product_for_extracting(scope="function"):
    component1 = BaseComponent("component1")
    component1.state_record_list = [
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    component2 = BaseComponent("component2")
    component2.state_record_list = [
        BaseComponentState.WORKING,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    component3 = BaseComponent("component3")
    component3.state_record_list = [
        BaseComponentState.READY,
        BaseComponentState.WORKING,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
        BaseComponentState.FINISHED,
    ]
    component4 = BaseComponent("component4")
    component4.state_record_list = [
        BaseComponentState.NONE,
        BaseComponentState.READY,
        BaseComponentState.WORKING,
        BaseComponentState.WORKING,
        BaseComponentState.FINISHED,
    ]
    component5 = BaseComponent("component5")
    component5.state_record_list = [
        BaseComponentState.NONE,
        BaseComponentState.NONE,
        BaseComponentState.READY,
        BaseComponentState.READY,
        BaseComponentState.WORKING,
    ]
    return BaseProduct([component1, component2, component3, component4, component5])


def test_extract_none_component_list(dummy_product_for_extracting):
    assert len(dummy_product_for_extracting.extract_none_component_list([5])) == 0
    assert len(dummy_product_for_extracting.extract_none_component_list([0])) == 2
    assert len(dummy_product_for_extracting.extract_none_component_list([1])) == 1
    assert len(dummy_product_for_extracting.extract_none_component_list([0, 1])) == 1


def test_extract_ready_component_list(dummy_product_for_extracting):
    assert len(dummy_product_for_extracting.extract_ready_component_list([1])) == 1
    assert len(dummy_product_for_extracting.extract_ready_component_list([2, 3])) == 1
    assert (
        len(dummy_product_for_extracting.extract_ready_component_list([1, 2, 3])) == 0
    )


def test_extract_working_component_list(dummy_product_for_extracting):
    assert len(dummy_product_for_extracting.extract_working_component_list([0])) == 2
    assert len(dummy_product_for_extracting.extract_working_component_list([1, 2])) == 1
    assert (
        len(dummy_product_for_extracting.extract_working_component_list([1, 2, 3])) == 0
    )


def test_extract_finished_component_list(dummy_product_for_extracting):
    assert (
        len(dummy_product_for_extracting.extract_finished_component_list([2, 3])) == 2
    )
    assert (
        len(dummy_product_for_extracting.extract_finished_component_list([2, 3, 4]))
        == 2
    )
    assert len(dummy_product_for_extracting.extract_finished_component_list([0])) == 0


def test_get_component_list():
    # TODO if we have enough time for setting test case...
    c1 = BaseComponent("c1")
    product = BaseProduct([c1])
    assert (
        len(
            product.get_component_list(
                name="test",
                ID="test",
                parent_component_list=[],
                child_component_list=[],
                targeted_task_list=[],
                space_size=99876,
                placed_workplace="test",
                placed_workplace_id_record=[],
            )
        )
    ) == 0


def test_create_simple_gantt():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    product = BaseProduct([c1, c2])

    # Set test case
    c1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    c2.state_record_list = [
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]

    for ext in ["png"]:
        save_fig_path = "test." + ext
        product.create_simple_gantt(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_create_data_for_gantt_plotly():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    product = BaseProduct([c1, c2])

    # Set test case
    c1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    c2.state_record_list = [
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    product.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_check_removing_placed_workplace():
    c1 = BaseComponent("c1")
    task1 = BaseTask("task1")
    c1.append_targeted_task(task1)
    c2 = BaseComponent("c2")
    task2 = BaseTask("task2")
    c2.append_targeted_task(task2)
    product = BaseProduct([c1, c2])

    f1 = BaseWorkplace("f1")
    f2 = BaseWorkplace("f2")
    c1.placed_workplace = f1
    c2.placed_workplace = f2
    f1.set_placed_component(c1)
    f2.set_placed_component(c2)

    # case1
    task1.state = BaseTaskState.WORKING
    task2.state = BaseTaskState.FINISHED
    product.check_removing_placed_workplace()
    assert c1.placed_workplace.name == "f1"
    assert c2.placed_workplace is None

    # case2
    task1.state = BaseTaskState.FINISHED
    task2.state = BaseTaskState.FINISHED
    c1.append_child_component(c2)
    c1.placed_workplace = f1
    c2.placed_workplace = f1
    f1.placed_component_list = [c1, c2]
    product.check_removing_placed_workplace()
    assert c1.placed_workplace is None
    assert c2.placed_workplace is None


def test_create_gantt_plotly():
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    product = BaseProduct([c1, c2])

    # Set test case
    c1.state_record_list = [
        BaseTaskState.READY,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
    ]
    c2.state_record_list = [
        BaseTaskState.WORKING,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.WORKING,
        BaseTaskState.FINISHED,
        BaseTaskState.FINISHED,
    ]

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
