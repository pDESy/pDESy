#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.base_facility import BaseFacility, BaseFacilityState
from pDESy.model.base_workplace import BaseWorkplace
from pDESy.model.base_component import BaseComponent
from pDESy.model.base_task import BaseTask
import datetime
import os
import pytest


def test_init():
    workplace = BaseWorkplace("workplace")
    assert workplace.name == "workplace"
    assert len(workplace.ID) > 0
    assert workplace.facility_list == []
    assert workplace.targeted_task_list == []
    assert workplace.parent_workplace is None
    assert workplace.max_space_size == 1.0
    assert workplace.cost_list == []
    workplace.cost_list.append(1)
    assert workplace.cost_list == [1.0]

    w1 = BaseFacility("w1")
    t1 = BaseTask("task1")
    workplace1 = BaseWorkplace(
        "workplace1",
        parent_workplace=workplace,
        targeted_task_list=[t1],
        facility_list=[w1],
        max_space_size=2.0,
        cost_list=[10],
        placed_component_list=[BaseComponent("c")],
        placed_component_id_record=["xxxx"],
    )
    assert workplace1.facility_list == [w1]
    assert workplace1.targeted_task_list == [t1]
    assert workplace1.parent_workplace == workplace
    assert workplace1.max_space_size == 2.0
    assert workplace1.cost_list == [10]
    assert workplace1.placed_component_list[0].name == "c"
    assert workplace1.placed_component_id_record == ["xxxx"]


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
    return BaseWorkplace(
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


def test_set_parent_workplace():
    workplace = BaseWorkplace("workplace")
    workplace.set_parent_workplace(BaseWorkplace("xxx"))
    assert workplace.parent_workplace.name == "xxx"


def test_add_facility():
    workplace = BaseWorkplace("workplace")
    facility = BaseFacility("facility")
    workplace.add_facility(facility)
    assert len(workplace.facility_list) == 1
    assert facility.workplace_id == workplace.ID


def test_remove_placed_component():
    c = BaseComponent("c")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    workplace = BaseWorkplace("workplace")
    workplace.set_placed_component(c)
    assert workplace.placed_component_list == [c, c1, c2]
    workplace.remove_placed_component(c)
    assert workplace.placed_component_list == []


def test_can_put():
    c1 = BaseComponent("c1", space_size=2.0)
    c2 = BaseComponent("c2", space_size=2.0)
    workplace = BaseWorkplace("f", max_space_size=1.0)
    assert workplace.can_put(c1) is False
    assert workplace.can_put(c2) is False
    workplace.max_space_size = 3.0
    assert workplace.can_put(c1) is True
    assert workplace.can_put(c2) is True
    workplace.set_placed_component(c1)
    assert workplace.can_put(c2) is False
    workplace.max_space_size = 4.0
    assert workplace.can_put(c2) is True


def test_extend_targeted_task_list():
    workplace = BaseWorkplace("workplace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workplace.extend_targeted_task_list([task1, task2])
    assert workplace.targeted_task_list == [task1, task2]
    assert task1.allocated_workplace_list == [workplace]
    assert task2.allocated_workplace_list == [workplace]


def test_append_targeted_task():
    workplace = BaseWorkplace("workplace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workplace.append_targeted_task(task1)
    workplace.append_targeted_task(task2)
    assert workplace.targeted_task_list == [task1, task2]
    assert task1.allocated_workplace_list == [workplace]
    assert task2.allocated_workplace_list == [workplace]


def test_initialize():
    workplace = BaseWorkplace("workplace")
    workplace.cost_list = [9.0, 7.2]
    w = BaseFacility("w1")
    workplace.facility_list = [w]
    w.state = BaseFacilityState.WORKING
    w.cost_list = [9.0, 7.2]
    w.assigned_task_list = [BaseTask("task")]
    workplace.initialize()
    assert workplace.cost_list == []
    assert w.state == BaseFacilityState.FREE
    assert w.cost_list == []
    assert w.assigned_task_list == []


def test_add_labor_cost():
    workplace = BaseWorkplace("workplace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    workplace.facility_list = [w2, w1]
    w1.state = BaseFacilityState.WORKING
    w2.state = BaseFacilityState.FREE
    workplace.add_labor_cost()
    assert w1.cost_list == [10.0]
    assert w2.cost_list == [0.0]
    assert workplace.cost_list == [10.0]
    workplace.add_labor_cost(only_working=False)
    assert workplace.cost_list == [10.0, 15.0]
    assert w1.cost_list == [10.0, 10.0]
    assert w2.cost_list == [0.0, 5.0]


def test_str():
    print(BaseWorkplace("aaaaaaaa"))


def test_get_facility_list():
    # TODO if we have enough time for setting test case...
    workplace = BaseWorkplace("workplace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    workplace.facility_list = [w2, w1]
    assert (
        len(
            workplace.get_facility_list(
                name="test",
                ID="test",
                workplace_id="test",
                cost_per_time=99876,
                solo_working=True,
                workamount_skill_mean_map={},
                workamount_skill_sd_map=[],
                state=BaseFacilityState.WORKING,
                cost_list=[],
                assigned_task_list=[],
                assigned_task_id_record=[],
            )
        )
        == 0
    )


def test_create_simple_gantt():
    workplace = BaseWorkplace("workplace")
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
    workplace.facility_list = [w1, w2]
    workplace.create_simple_gantt()


def test_create_data_for_gantt_plotly():
    workplace = BaseWorkplace("workplace")
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
    workplace.facility_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    workplace.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_create_gantt_plotly(tmpdir):
    workplace = BaseWorkplace("workplace")
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
    workplace.facility_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    workplace.create_gantt_plotly(init_datetime, timedelta, save_fig_path=os.path.join(str(tmpdir),"test.png"))

    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir),"test." + ext)
        workplace.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )


def test_create_data_for_cost_history_plotly():
    workplace = BaseWorkplace("workplace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    workplace.facility_list = [w1, w2]
    workplace.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    data = workplace.create_data_for_cost_history_plotly(init_datetime, timedelta)

    x = [
        (init_datetime + time * timedelta).strftime("%Y-%m-%d %H:%M:%S")
        for time in range(len(workplace.cost_list))
    ]
    # w1
    assert data[0].name == w1.name
    assert data[0].x == tuple(x)
    assert data[0].y == tuple(w1.cost_list)

    # w2
    assert data[1].name == w2.name
    assert data[1].x == tuple(x)
    assert data[1].y == tuple(w2.cost_list)


def test_create_cost_history_plotly(tmpdir):
    workplace = BaseWorkplace("workplace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    workplace.facility_list = [w1, w2]
    workplace.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    workplace.create_cost_history_plotly(init_datetime, timedelta)

    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir),"test." + ext)
        workplace.create_cost_history_plotly(
            init_datetime, timedelta, title="bbbbbbb", save_fig_path=save_fig_path
        )
