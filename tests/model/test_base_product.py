#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_base_product."""

import datetime
import os

import pytest

from pDESy.model.base_component import BaseComponent, BaseComponentState
from pDESy.model.base_product import BaseProduct
from pDESy.model.base_task import BaseTaskState


def test_init():
    """test_init."""
    c1 = BaseComponent("c1")
    product = BaseProduct(component_set={c1})
    assert product.component_set == {c1}


def test_initialize():
    """test_initialize."""
    c1 = BaseComponent("c1")
    product = BaseProduct(component_set={c1})
    product.initialize()


def test_str():
    """test_str."""
    print(BaseProduct(component_set=set()))


@pytest.fixture(name="dummy_product_for_extracting")
def fixture_dummy_product_for_extracting():
    """dummy_product_for_extracting."""
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
    return BaseProduct(
        component_set={component1, component2, component3, component4, component5}
    )


def test_extract_none_component_set(dummy_product_for_extracting):
    """test_extract_none_component_set."""
    assert len(dummy_product_for_extracting.extract_none_component_set([5])) == 0
    assert len(dummy_product_for_extracting.extract_none_component_set([0])) == 2
    assert len(dummy_product_for_extracting.extract_none_component_set([1])) == 1
    assert len(dummy_product_for_extracting.extract_none_component_set([0, 1])) == 1


def test_extract_ready_component_set(dummy_product_for_extracting):
    """test_extract_ready_component_set."""
    assert len(dummy_product_for_extracting.extract_ready_component_set([1])) == 1
    assert len(dummy_product_for_extracting.extract_ready_component_set([2, 3])) == 1
    assert len(dummy_product_for_extracting.extract_ready_component_set([1, 2, 3])) == 0


def test_extract_working_component_set(dummy_product_for_extracting):
    """test_extract_working_component_set."""
    assert len(dummy_product_for_extracting.extract_working_component_set([0])) == 2
    assert len(dummy_product_for_extracting.extract_working_component_set([1, 2])) == 1
    assert (
        len(dummy_product_for_extracting.extract_working_component_set([1, 2, 3])) == 0
    )


def test_extract_finished_component_set(dummy_product_for_extracting):
    """test_extract_finished_component_set."""
    assert len(dummy_product_for_extracting.extract_finished_component_set([2, 3])) == 2
    assert (
        len(dummy_product_for_extracting.extract_finished_component_set([2, 3, 4])) == 2
    )
    assert len(dummy_product_for_extracting.extract_finished_component_set([0])) == 0


def test_plot_simple_gantt(tmpdir):
    """test_plot_simple_gantt."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    product = BaseProduct(component_set={c1, c2})

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
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        product.plot_simple_gantt(save_fig_path=save_fig_path)


def test_create_data_for_gantt_plotly():
    """test_create_data_for_gantt_plotly."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    product = BaseProduct(component_set={c1, c2})

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


def test_remove_insert_absence_time_list():
    """test_remove_insert_absence_time_list."""
    c1 = BaseComponent("c1", "----")
    c1.placed_workplace_id_record_list = ["aa", "bb", "cc", "dd", "ee", "ff"]
    c1.state_record_list = [0, 1, 2, 3, 4, 5]

    c2 = BaseComponent("c2", "----")
    c2.placed_workplace_id_record_list = ["ff", "ee", "dd", "cc", "bb", "aa"]
    c2.state_record_list = [5, 4, 3, 2, 1, 0]
    c2.add_child_component(c1)

    product = BaseProduct(component_set={c1, c2})

    absence_time_list = [0, 1]
    product.remove_absence_time_list(absence_time_list)
    assert c1.placed_workplace_id_record_list == ["cc", "dd", "ee", "ff"]
    assert c1.state_record_list == [2, 3, 4, 5]
    assert c2.placed_workplace_id_record_list == ["dd", "cc", "bb", "aa"]
    assert c2.state_record_list == [3, 2, 1, 0]

    product.insert_absence_time_list(absence_time_list)
    assert c1.placed_workplace_id_record_list == [
        None,
        None,
        "cc",
        "dd",
        "ee",
        "ff",
    ]
    assert c1.state_record_list == [
        BaseComponentState.NONE,
        BaseComponentState.READY,
        2,
        3,
        4,
        5,
    ]
    assert c2.placed_workplace_id_record_list == [
        None,
        None,
        "dd",
        "cc",
        "bb",
        "aa",
    ]
    assert c2.state_record_list == [
        BaseComponentState.NONE,
        BaseComponentState.NONE,
        3,
        2,
        1,
        0,
    ]


def test_create_gantt_plotly(tmpdir):
    """test_create_gantt_plotly."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    product = BaseProduct(component_set={c1, c2})

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
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        product.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )


def test_get_networkx_graph():
    """test_get_networkx_graph."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})
    product.get_networkx_graph()


def test_draw_networkx(tmpdir):
    """test_draw_networkx."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})
    for ext in ["png"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        product.draw_networkx(save_fig_path=save_fig_path)


def test_get_node_and_edge_trace_for_plotly_network():
    """test_get_node_and_edge_trace_for_plotly_network."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})
    product.get_node_and_edge_trace_for_plotly_network()


def test_draw_plotly_network(tmpdir):
    """test_draw_plotly_network."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    c1.child_component_id_set = {c2.ID}
    c2.child_component_id_set = {c3.ID}
    product = BaseProduct(component_set={c3, c2, c1})
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        product.draw_plotly_network(save_fig_path=save_fig_path)


def test_print_mermaid_diagram(dummy_product_for_extracting):
    """test_print_mermaid_diagram."""
    dummy_product_for_extracting.print_mermaid_diagram(
        orientations="LR",
        subgraph=True,
    )
    dummy_product_for_extracting.print_target_component_mermaid_diagram(
        {
            list(dummy_product_for_extracting.component_set)[0],
            list(dummy_product_for_extracting.component_set)[1],
        },
        orientations="LR",
        subgraph=False,
    )
