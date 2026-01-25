#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for BaseProduct.

This module contains unit tests for the BaseProduct class and related functionality.
"""

import datetime
import os

import pytest

from pDESy.model.base_component import BaseComponent, BaseComponentState
from pDESy.model.base_product import BaseProduct
from pDESy.model.base_task import BaseTaskState


def test_init():
    """Test initialization of BaseProduct."""
    c1 = BaseComponent("c1")
    product = BaseProduct(component_set={c1})
    assert product.component_set == {c1}


def test_initialize():
    """Test initialization/reset of BaseProduct."""
    c1 = BaseComponent("c1")
    product = BaseProduct(component_set={c1})
    product.initialize()


def test_create_component():
    """Test creating a component from a product."""
    product = BaseProduct()
    component = product.create_component("c1")
    assert component in product.component_set
    assert component.parent_product_id == product.ID


def test_str():
    """Test string representation of BaseProduct."""
    print(BaseProduct(component_set=set()))


@pytest.fixture(name="dummy_product_for_extracting")
def fixture_dummy_product_for_extracting():
    """Fixture for a dummy BaseProduct for extracting tests.

    Returns:
        BaseProduct: A dummy product instance with several components.
    """
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
    """Test extracting components in NONE state.

    Args:
        dummy_product_for_extracting (BaseProduct): The dummy product fixture.
    """
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [5], BaseComponentState.NONE
            )
        )
        == 0
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [0], BaseComponentState.NONE
            )
        )
        == 2
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [1], BaseComponentState.NONE
            )
        )
        == 1
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [0, 1], BaseComponentState.NONE
            )
        )
        == 1
    )


def test_extract_ready_component_set(dummy_product_for_extracting):
    """Test extracting components in READY state.

    Args:
        dummy_product_for_extracting (BaseProduct): The dummy product fixture.
    """
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [1], BaseComponentState.READY
            )
        )
        == 1
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [2, 3], BaseComponentState.READY
            )
        )
        == 1
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [1, 2, 3], BaseComponentState.READY
            )
        )
        == 0
    )


def test_extract_working_component_set(dummy_product_for_extracting):
    """Test extracting components in WORKING state.

    Args:
        dummy_product_for_extracting (BaseProduct): The dummy product fixture.
    """
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [0], BaseComponentState.WORKING
            )
        )
        == 2
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [1, 2], BaseComponentState.WORKING
            )
        )
        == 1
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [1, 2, 3], BaseComponentState.WORKING
            )
        )
        == 0
    )


def test_extract_finished_component_set(dummy_product_for_extracting):
    """Test extracting components in FINISHED state.

    Args:
        dummy_product_for_extracting (BaseProduct): The dummy product fixture.
    """
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [2, 3], BaseComponentState.FINISHED
            )
        )
        == 2
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [2, 3, 4], BaseComponentState.FINISHED
            )
        )
        == 2
    )
    assert (
        len(
            dummy_product_for_extracting.get_component_set_by_state(
                [0], BaseComponentState.FINISHED
            )
        )
        == 0
    )




def test_remove_insert_absence_time_list():
    """Test removing and inserting absence time list for BaseProduct."""
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




def test_print_mermaid_diagram(dummy_product_for_extracting):
    """Test printing Mermaid diagrams.

    Args:
        dummy_product_for_extracting (BaseProduct): The dummy product fixture.
    """
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
