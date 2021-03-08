#!/usr/bin/python
# -*- coding: utf-8 -*-

from pDESy.model.base_facility import BaseFacility, BaseFacilityState
from pDESy.model.base_workspace import BaseWorkspace
from pDESy.model.base_component import BaseComponent
from pDESy.model.base_task import BaseTask
import datetime
import os
import pytest


def test_init():
    workspace = BaseWorkspace("workspace")
    assert workspace.name == "workspace"
    assert len(workspace.ID) > 0
    assert workspace.facility_list == []
    assert workspace.targeted_task_list == []
    assert workspace.parent_workspace is None
    assert workspace.max_space_size == 1.0
    assert workspace.cost_list == []
    workspace.cost_list.append(1)
    assert workspace.cost_list == [1.0]

    w1 = BaseFacility("w1")
    t1 = BaseTask("task1")
    workspace1 = BaseWorkspace(
        "workspace1",
        parent_workspace=workspace,
        targeted_task_list=[t1],
        facility_list=[w1],
        max_space_size=2.0,
        cost_list=[10],
        placed_component_list=[BaseComponent("c")],
        placed_component_id_record=["xxxx"],
    )
    assert workspace1.facility_list == [w1]
    assert workspace1.targeted_task_list == [t1]
    assert workspace1.parent_workspace == workspace
    assert workspace1.max_space_size == 2.0
    assert workspace1.cost_list == [10]
    assert workspace1.placed_component_list[0].name == "c"
    assert workspace1.placed_component_id_record == ["xxxx"]


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
    return BaseWorkspace(
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


def test_set_parent_workspace():
    workspace = BaseWorkspace("workspace")
    workspace.set_parent_workspace(BaseWorkspace("xxx"))
    assert workspace.parent_workspace.name == "xxx"


def test_add_facility():
    workspace = BaseWorkspace("workspace")
    facility = BaseFacility("facility")
    workspace.add_facility(facility)
    assert len(workspace.facility_list) == 1
    assert facility.workspace_id == workspace.ID


def test_remove_placed_component():
    c = BaseComponent("c")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c.append_child_component(c1)
    c1.append_child_component(c2)
    workspace = BaseWorkspace("workspace")
    workspace.set_placed_component(c)
    assert workspace.placed_component_list == [c, c1, c2]
    workspace.remove_placed_component(c)
    assert workspace.placed_component_list == []


def test_can_put():
    c1 = BaseComponent("c1", space_size=2.0)
    c2 = BaseComponent("c2", space_size=2.0)
    workspace = BaseWorkspace("f", max_space_size=1.0)
    assert workspace.can_put(c1) is False
    assert workspace.can_put(c2) is False
    workspace.max_space_size = 3.0
    assert workspace.can_put(c1) is True
    assert workspace.can_put(c2) is True
    workspace.set_placed_component(c1)
    assert workspace.can_put(c2) is False
    workspace.max_space_size = 4.0
    assert workspace.can_put(c2) is True


def test_extend_targeted_task_list():
    workspace = BaseWorkspace("workspace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workspace.extend_targeted_task_list([task1, task2])
    assert workspace.targeted_task_list == [task1, task2]
    assert task1.allocated_workspace_list == [workspace]
    assert task2.allocated_workspace_list == [workspace]


def test_append_targeted_task():
    workspace = BaseWorkspace("workspace")
    task1 = BaseTask("task1")
    task2 = BaseTask("task2")
    workspace.append_targeted_task(task1)
    workspace.append_targeted_task(task2)
    assert workspace.targeted_task_list == [task1, task2]
    assert task1.allocated_workspace_list == [workspace]
    assert task2.allocated_workspace_list == [workspace]


def test_initialize():
    workspace = BaseWorkspace("workspace")
    workspace.cost_list = [9.0, 7.2]
    w = BaseFacility("w1")
    workspace.facility_list = [w]
    w.state = BaseFacilityState.WORKING
    w.cost_list = [9.0, 7.2]
    w.assigned_task_list = [BaseTask("task")]
    workspace.initialize()
    assert workspace.cost_list == []
    assert w.state == BaseFacilityState.FREE
    assert w.cost_list == []
    assert w.assigned_task_list == []


def test_add_labor_cost():
    workspace = BaseWorkspace("workspace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    workspace.facility_list = [w2, w1]
    w1.state = BaseFacilityState.WORKING
    w2.state = BaseFacilityState.FREE
    workspace.add_labor_cost()
    assert w1.cost_list == [10.0]
    assert w2.cost_list == [0.0]
    assert workspace.cost_list == [10.0]
    workspace.add_labor_cost(only_working=False)
    assert workspace.cost_list == [10.0, 15.0]
    assert w1.cost_list == [10.0, 10.0]
    assert w2.cost_list == [0.0, 5.0]


def test_str():
    print(BaseWorkspace("aaaaaaaa"))


def test_get_facility_list():
    # TODO if we have enough time for setting test case...
    workspace = BaseWorkspace("workspace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w2 = BaseFacility("w2", cost_per_time=5.0)
    workspace.facility_list = [w2, w1]
    assert (
        len(
            workspace.get_facility_list(
                name="test",
                ID="test",
                workspace_id="test",
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
    workspace = BaseWorkspace("workspace")
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
    workspace.facility_list = [w1, w2]
    workspace.create_simple_gantt()


def test_create_data_for_gantt_plotly():
    workspace = BaseWorkspace("workspace")
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
    workspace.facility_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    workspace.create_data_for_gantt_plotly(init_datetime, timedelta)


def test_create_gantt_plotly():
    workspace = BaseWorkspace("workspace")
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
    workspace.facility_list = [w1, w2]

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    workspace.create_gantt_plotly(init_datetime, timedelta, save_fig_path="test.png")

    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        workspace.create_gantt_plotly(
            init_datetime, timedelta, save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_create_data_for_cost_history_plotly():
    workspace = BaseWorkspace("workspace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    workspace.facility_list = [w1, w2]
    workspace.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    data = workspace.create_data_for_cost_history_plotly(init_datetime, timedelta)

    x = [
        (init_datetime + time * timedelta).strftime("%Y-%m-%d %H:%M:%S")
        for time in range(len(workspace.cost_list))
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
    workspace = BaseWorkspace("workspace")
    w1 = BaseFacility("w1", cost_per_time=10.0)
    w1.cost_list = [0, 0, 10, 10, 0, 10]
    w2 = BaseFacility("w2", cost_per_time=5.0)
    w2.cost_list = [5, 5, 0, 0, 5, 5]
    workspace.facility_list = [w1, w2]
    workspace.cost_list = list(map(sum, zip(w1.cost_list, w2.cost_list)))

    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    workspace.create_cost_history_plotly(init_datetime, timedelta)

    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        workspace.create_cost_history_plotly(
            init_datetime, timedelta, title="bbbbbbb", save_fig_path=save_fig_path
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)
