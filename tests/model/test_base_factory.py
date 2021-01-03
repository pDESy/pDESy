#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.base_facility import BaseFacility, BaseFacilityState
from pDESy.model.base_factory import BaseFactory
from pDESy.model.base_component import BaseComponent
from pDESy.model.base_task import BaseTask
import datetime
import os
import pytest


def test_init():
    factory = BaseFactory("factory")
    assert factory.name == "factory"
    assert len(factory.ID) > 0
    assert factory.facility_list == []
    assert factory.targeted_task_list == []
    assert factory.parent_factory is None
    assert factory.max_space_size == 1.0
    assert factory.cost_list == []
    factory.cost_list.append(1)
    assert factory.cost_list == [1.0]

    w1 = BaseFacility("w1")
    t1 = BaseTask("task1")
    factory1 = BaseFactory(
        "factory1",
        parent_factory=factory,
        targeted_task_list=[t1],
        facility_list=[w1],
        max_space_size=2.0,
        cost_list=[10],
        placed_component_list=[BaseComponent("c")],
        placed_component_id_record=["xxxx"],
    )
    assert factory1.facility_list == [w1]
    assert factory1.targeted_task_list == [t1]
    assert factory1.parent_factory == factory
    assert factory1.max_space_size == 2.0
    assert factory1.cost_list == [10]
    assert factory1.placed_component_list[0].name == "c"
    assert factory1.placed_component_id_record == ["xxxx"]


@pytest.fixture
def dummy_team_for_extracting(scope="function"):
    facility1 = BaseFacility("facility1")
    facility1.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    facility2 = BaseFacility("facility2")
    facility2.state_record_list = [
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
    ]
    facility3 = BaseFacility("facility3")
    facility3.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    facility4 = BaseFacility("facility4")
    facility4.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
    ]
    facility5 = BaseFacility("facility5")
    facility5.state_record_list = [
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
    ]
    return BaseFactory(
        "test", facility_list=[facility1, facility2, facility3, facility4, facility5]
    )


def test_extract_free_facility_list(dummy_team_for_extracting):
    assert len(dummy_team_for_extracting.extract_free_facility_list([5])) == 0
    assert len(dummy_team_for_extracting.extract_free_facility_list([3, 4])) == 2
    assert len(dummy_team_for_extracting.extract_free_facility_list([0, 1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_free_facility_list([0, 1, 4])) == 2


def test_extract_working_facility_list(dummy_team_for_extracting):
    assert len(dummy_team_for_extracting.extract_working_facility_list([0, 1])) == 1
    assert len(dummy_team_for_extracting.extract_working_facility_list([1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_working_facility_list([1, 2, 3])) == 1


def test_set_parent_factory():
    factory = BaseFactory("factory")
    factory.set_parent_factory(BaseFactory("xxx"))
    assert factory.parent_factory.name == "xxx"


def test_add_facility():
    factory = BaseFactory("factory")
    facility = BaseFacility("facility")
    factory.add_facility(facility)
    assert len(factory.facility_list) == 1
    assert facility.factory_id == factory.ID


def test_remove_placed_component():
    c = BaseComponent("c")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    factory = BaseFactory("factory")
    factory.set_placed_component(c)
    assert factory.placed_component_list == [c, c1, c2]
    factory.remove_placed_component(c)
    assert factory.placed_component_list == []


def test_can_put():
    c1 = BaseComponent("c1", space_size=2.0)
    c2 = BaseComponent("c2", space_size=2.0)
    factory = BaseFactory("f", max_space_size=1.0)
    assert factory.can_put(c1) is False
    assert factory.can_put(c2) is False
    factory.max_space_size = 3.0
    assert factory.can_put(c1) is True
    assert factory.can_put(c2) is True
    factory.set_placed_component(c1)
    assert factory.can_put(c2) is False
    factory.max_space_size = 4.0
    assert factory.can_put(c2) is True


def test_extend_targeted_task_list():
    factory = BaseFactory("factory")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    factory.extend_targeted_task_list([task1, task2])
    assert factory.targeted_task_list == [task1, task2]
    assert task1.allocated_factory_list == [factory]
    assert task2.allocated_factory_list == [factory]


def test_append_targeted_task():
    factory = BaseFactory("factory")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    factory.append_targeted_task(task1)
    factory.append_targeted_task(task2)
    assert factory.targeted_task_list == [task1, task2]
    assert task1.allocated_factory_list == [factory]
    assert task2.allocated_factory_list == [factory]


def test_initialize():
    factory = BaseFactory("factory")
    factory.cost_list = [9.0, 7.2]
    w = BaseFacility("w1")
    factory.facility_list = [w]
    w.state = BaseFacilityState.WORKING
    w.cost_list = [9.0, 7.2]
    w.start_time_list = [0]
    w.finish_time_list = [1]
    w.assigned_task_list = [BaseTask("task")]
    factory.initialize()
    assert factory.cost_list == []
    assert w.state == BaseFacilityState.FREE
    assert w.cost_list == []
    assert w.start_time_list == []
    assert w.finish_time_list == []
    assert w.assigned_task_list == []


def test_add_labor_cost():
    factory = BaseFactory("factory")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    factory.facility_list = [w2, w1]
    w1.state = BaseFacilityState.WORKING
    w2.state = BaseFacilityState.FREE
    factory.add_labor_cost()
    assert w1.cost_list == [10.0]
    assert w2.cost_list == [0.0]
    assert factory.cost_list == [10.0]
    factory.add_labor_cost(only_working=False)
    assert factory.cost_list == [10.0, 15.0]
    assert w1.cost_list == [10.0, 10.0]
    assert w2.cost_list == [0.0, 5.0]


def test_str():
    print(BaseFactory("aaaaaaaa"))


def test_get_facility_list():
    # TODO if we have enough time for setting test case...
    factory = BaseFactory("factory")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    factory.facility_list = [w2, w1]
    assert (
        len(
            factory.get_facility_list(
                name="test",
                ID="test",
                factory_id="test",
                cost_per_time=99876,
                solo_working=True,
                workamount_skill_mean_map={},
                workamount_skill_sd_map=[],
                state=BaseFacilityState.WORKING,
                cost_list=[],
                start_time_list=[],
                finish_time_list=[],
                assigned_task_list=[],
                assigned_task_id_record=[],
            )
        )
        == 0
    )


def test_create_data_for_gantt_plotly():
    factory = BaseFactory("factory")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.state_record_list = [
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.state_record_list = [
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    factory.facility_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    factory.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_create_gantt_plotly():
    factory = BaseFactory("factory")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.state_record_list = [
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.state_record_list = [
        BaseFacilityState.WORKING,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.WORKING,
        BaseFacilityState.FREE,
        BaseFacilityState.FREE,
    ]
    factory.facility_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    factory.create_gantt_plotly(init_datetime, timedelta, save_fig_path="test.png")

    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        factory.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_create_data_for_cost_history_plotly():
    factory = BaseFactory("factory")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    factory.facility_list = [w1, w2]
    factory.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    data = factory.create_data_for_cost_history_plotly(init_datetime, timedelta)

    x = [
        (init_datetime + time * timedelta).strftime("%Y-%m-%d %H:%M:%S")
        for time in range(len(factory.cost_list))
    ]
    # w1
    assert data[0].name == w1.name
    assert data[0].x == tuple(x)
    assert data[0].y == tuple(w1.cost_list)

    # w2
    assert data[1].name == w2.name
    assert data[1].x == tuple(x)
    assert data[1].y == tuple(w2.cost_list)


def test_create_cost_history_plotly():
    factory = BaseFactory("factory")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    factory.facility_list = [w1, w2]
    factory.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    factory.create_cost_history_plotly(init_datetime, timedelta)

    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        factory.create_cost_history_plotly(
            init_datetime, timedelta, title="bbbbbbb", save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)
