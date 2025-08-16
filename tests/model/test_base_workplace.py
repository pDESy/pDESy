#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test_base_workplace."""

import datetime
import os

import pytest

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility, BaseFacilityState
from pDESy.model.base_task import BaseTask
from pDESy.model.base_workplace import BaseWorkplace


def test_init():
    """test_init."""
    workplace = BaseWorkplace("workplace")
    assert workplace.name == "workplace"
    assert len(workplace.ID) > 0
    assert workplace.facility_list == []
    assert workplace.targeted_task_id_list == []
    assert workplace.parent_workplace_id is None
    assert workplace.input_workplace_id_list == []
    assert workplace.cost_list == []
    workplace.cost_list.append(1)
    assert workplace.cost_list == [1.0]

    w1 = BaseFacility("w1")
    t1 = BaseTask("task1")
    workplace1 = BaseWorkplace(
        "workplace1",
        parent_workplace_id=workplace.ID,
        targeted_task_id_list=[t1.ID],
        facility_list=[w1],
        max_space_size=2.0,
        cost_list=[10],
        placed_component_list=[BaseComponent("c")],
        placed_component_id_record=["xxxx"],
    )
    assert workplace1.facility_list == [w1]
    assert workplace1.targeted_task_id_list == [t1.ID]
    assert workplace1.parent_workplace_id == workplace.ID
    assert workplace1.max_space_size == 2.0
    assert workplace1.cost_list == [10]
    assert workplace1.placed_component_list[0].name == "c"
    assert workplace1.placed_component_id_record == ["xxxx"]


@pytest.fixture(name="dummy_team_for_extracting")
def fixture_dummy_team_for_extracting():
    """dummy_team_for_extracting."""
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
    """test_extract_free_facility_list."""
    assert len(dummy_team_for_extracting.extract_free_facility_list([5])) == 0
    assert len(dummy_team_for_extracting.extract_free_facility_list([3, 4])) == 2
    assert len(dummy_team_for_extracting.extract_free_facility_list([0, 1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_free_facility_list([0, 1, 4])) == 2


def test_extract_working_facility_list(dummy_team_for_extracting):
    """test_extract_working_facility_list."""
    assert len(dummy_team_for_extracting.extract_working_facility_list([0, 1])) == 1
    assert len(dummy_team_for_extracting.extract_working_facility_list([1, 2])) == 2
    assert len(dummy_team_for_extracting.extract_working_facility_list([1, 2, 3])) == 1


def test_set_parent_workplace():
    """test_set_parent_workplace."""
    workplace = BaseWorkplace("workplace")
    parent_workplace = BaseWorkplace("parent_workplace")
    workplace.set_parent_workplace(parent_workplace)
    assert workplace.parent_workplace_id == parent_workplace.ID


def test_add_facility():
    """test_add_facility."""
    workplace = BaseWorkplace("workplace")
    facility = BaseFacility("facility")
    workplace.add_facility(facility)
    assert len(workplace.facility_list) == 1
    assert facility.workplace_id == workplace.ID


def test_extend_targeted_task_list():
    """test_extend_targeted_task_list."""
    workplace = BaseWorkplace("workplace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workplace.extend_targeted_task_list([task1, task2])
    assert workplace.targeted_task_id_list == [task1.ID, task2.ID]
    assert task1.allocated_workplace_id_list == [workplace.ID]
    assert task2.allocated_workplace_id_list == [workplace.ID]


def test_append_targeted_task():
    """test_append_targeted_task."""
    workplace = BaseWorkplace("workplace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workplace.append_targeted_task(task1)
    workplace.append_targeted_task(task2)
    assert workplace.targeted_task_id_list == [task1.ID, task2.ID]
    assert task1.allocated_workplace_id_list == [workplace.ID]
    assert task2.allocated_workplace_id_list == [workplace.ID]


def test_initialize():
    """test_initialize."""
    workplace = BaseWorkplace("workplace")
    workplace.cost_list = [9.0, 7.2]
    w = BaseFacility("w1")
    workplace.facility_list = [w]
    w.state = BaseFacilityState.WORKING
    w.cost_list = [9.0, 7.2]
    w.assigned_task_id_list = [BaseTask("task").ID]
    workplace.initialize()
    assert workplace.cost_list == []
    assert w.state == BaseFacilityState.FREE
    assert w.cost_list == []
    assert w.assigned_task_id_list == []


def test_add_labor_cost():
    """test_add_labor_cost."""
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
    """test_str."""
    print(BaseWorkplace("dummy_base_workflow"))


def test_get_facility_list():
    """test_get_facility_list."""
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
                assigned_task_id_list=[],
                assigned_task_id_record=[],
            )
        )
        == 0
    )


def test_plot_simple_gantt():
    """test_plot_simple_gantt."""
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
    workplace.plot_simple_gantt()


def test_create_data_for_gantt_plotly():
    """test_create_data_for_gantt_plotly."""
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
    """test_create_gantt_plotly."""
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
    workplace.create_gantt_plotly(
        init_datetime, timedelta, save_fig_path=os.path.join(str(tmpdir), "test.png")
    )

    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        workplace.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )


def test_create_data_for_cost_history_plotly():
    """test_create_data_for_cost_history_plotly."""
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
    """test_create_cost_history_plotly."""
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
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        workplace.create_cost_history_plotly(
            init_datetime, timedelta, title="bbbbbbb", save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_append_input_workplace():
    """test_append_input_workplace."""
    workplace = BaseWorkplace("workplace")
    workplace1 = BaseWorkplace("workplace1")
    workplace2 = BaseWorkplace("workplace2")
    workplace.append_input_workplace(workplace1)
    workplace.append_input_workplace(workplace2)
    assert workplace.input_workplace_id_list == [workplace1.ID, workplace2.ID]


def test_extend_input_workplace_list():
    """test_extend_input_workplace_list."""
    workplace11 = BaseWorkplace("workplace11")
    workplace12 = BaseWorkplace("workplace12")
    workplace2 = BaseWorkplace("workplace2")
    workplace2.extend_input_workplace_list([workplace11, workplace12])
    assert workplace2.input_workplace_id_list == [workplace11.ID, workplace12.ID]


def test_remove_insert_absence_time_list():
    """test_remove_insert_absence_time_list."""
    f1 = BaseFacility("w1", "----")
    f1.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    f1.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    f1.state_record_list = [2, 1, 2, 1, 1, 2]

    f2 = BaseFacility("w1", "----")
    f2.cost_list = [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    f2.assigned_task_id_record = ["aa", "bb", "cc", "dd", "ee", "ff"]
    f2.state_record_list = [2, 1, 2, 1, 1, 2]

    workplace = BaseWorkplace("aa", facility_list=[f1, f2])
    workplace.cost_list = [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]

    absence_time_list = [1, 3, 4]
    workplace.remove_absence_time_list(absence_time_list)
    assert workplace.cost_list == [2.0, 2.0, 2.0]
    assert f1.cost_list == [1.0, 1.0, 1.0]
    assert f1.assigned_task_id_record == ["aa", "cc", "ff"]
    assert f1.state_record_list == [2, 2, 2]
    assert f2.cost_list == [1.0, 1.0, 1.0]
    assert f2.assigned_task_id_record == ["aa", "cc", "ff"]
    assert f2.state_record_list == [2, 2, 2]

    workplace.insert_absence_time_list(absence_time_list)
    assert workplace.cost_list == [2.0, 0.0, 2.0, 0.0, 0.0, 2.0]
    assert f1.cost_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert f1.assigned_task_id_record == ["aa", "aa", "cc", "cc", "cc", "ff"]
    assert f1.state_record_list == [2, 0, 2, 0, 0, 2]
    assert f2.cost_list == [1.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert f2.assigned_task_id_record == ["aa", "aa", "cc", "cc", "cc", "ff"]
    assert f2.state_record_list == [2, 0, 2, 0, 0, 2]


def test_print_mermaid_diagram(dummy_team_for_extracting):
    """test_print_mermaid_diagram."""
    dummy_team_for_extracting.print_mermaid_diagram(orientations="LR", subgraph=True)
    dummy_team_for_extracting.print_target_facility_mermaid_diagram(
        [
            dummy_team_for_extracting.facility_list[0],
            dummy_team_for_extracting.facility_list[1],
        ],
        orientations="TB",
        subgraph=True,
    )
