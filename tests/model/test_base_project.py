#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for BaseProject.

This module contains unit tests for the BaseProject class and related functionality.
"""

import datetime
import os

import pytest

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility
from pDESy.model.base_priority_rule import (
    ResourcePriorityRuleMode,
    TaskPriorityRuleMode,
    WorkplacePriorityRuleMode,
)
from pDESy.model.base_product import BaseProduct
from pDESy.model.base_project import BaseProject, BaseProjectStatus
from pDESy.model.base_subproject_task import BaseSubProjectTask
from pDESy.model.base_task import BaseTask
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_workflow import BaseWorkflow
from pDESy.model.base_workplace import BaseWorkplace


@pytest.fixture(name="dummy_project")
def fixture_dummy_project():
    """Fixture for a dummy BaseProject.

    Returns:
        BaseProject: A dummy project instance with components, tasks, teams, workers, and workplaces.
    """
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(minutes=1),
    )

    # BaseComponents in BaseProduct
    c3 = BaseComponent("c3")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3.update_child_component_set({c1, c2})
    project.add_product(BaseProduct(component_set={c1, c2, c3}))

    # BaseTasks in BaseWorkflow
    task1_1 = BaseTask("task1_1", need_facility=True)
    task1_2 = BaseTask("task1_2", worker_priority_rule=ResourcePriorityRuleMode.HSV)
    task2_1 = BaseTask("task2_1")
    task3 = BaseTask("task3", due_time=30)
    task3.add_input_task(task1_2)
    task3.add_input_task(task2_1)
    task1_2.add_input_task(task1_1)
    task0 = BaseTask("auto", auto_task=True, due_time=20)
    project.add_workflow(
        BaseWorkflow(task_set={task1_1, task1_2, task2_1, task3, task0})
    )

    c1.update_targeted_task_set({task1_1, task1_2})
    c2.add_targeted_task(task2_1)
    c3.add_targeted_task(task3)

    # Facilities in workplace
    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
    }

    # Workplace
    workplace = BaseWorkplace("workplace", facility_set={f1})
    workplace.update_targeted_task_set({task1_1, task1_2, task2_1, task3})
    project.add_workplace(workplace)

    # BaseTeam
    team = BaseTeam("team")
    team.update_targeted_task_set({task1_1, task1_2, task2_1, task3})
    project.add_team(team)

    # BaseWorkers in each BaseTeam
    w1 = BaseWorker("w1", team_id=team.ID, cost_per_time=10.0)
    w1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
        task1_2.name: 1.0,
        task2_1.name: 0.0,
        task3.name: 1.0,
    }
    w1.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w1)

    w2 = BaseWorker("w2", team_id=team.ID, cost_per_time=6.0)
    w2.workamount_skill_mean_map = {
        task1_1.name: 1.0,
        task1_2.name: 0.0,
        task2_1.name: 1.0,
        task3.name: 1.0,
    }
    w2.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w2)

    return project


@pytest.fixture(name="dummy_project_multiple")
def fixture_dummy_project_multiple():
    """Fixture for a dummy BaseProject with multiple products and workflows.

    Returns:
        BaseProject: A dummy project instance with multiple products and workflows.
    """
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
    )

    # BaseComponent in BaseProducts
    p1 = project.create_product("product 1")
    c11 = p1.create_component("c11")
    c12 = p1.create_component("c12")
    c13 = p1.create_component("c13")
    c13.update_child_component_set({c11, c12})

    p2 = project.create_product("product 2")
    c21 = p2.create_component("c21")
    c22 = p2.create_component("c22")
    c23 = p2.create_component("c23")
    c23.update_child_component_set({c21, c22})

    # BaseTask in BaseWorkflows
    w1 = project.create_workflow("workflow 1")
    task1_1_1 = w1.create_task("task1_1", need_facility=True)
    task1_1_1.add_target_component(c11)
    task1_1_2 = w1.create_task("task1_2")
    task1_1_2.add_target_component(c11)
    task1_2_1 = w1.create_task("task2_1")
    task1_2_1.add_target_component(c12)
    task1_3 = w1.create_task("task3", due_time=30)
    task1_3.add_target_component(c13)
    task1_3.add_input_task(task1_1_2)
    task1_3.add_input_task(task1_2_1)
    task1_1_2.add_input_task(task1_1_1)
    _ = w1.create_task("auto", auto_task=True, due_time=20)

    w2 = project.create_workflow("workflow 2")
    task2_1_1 = w2.create_task("task1_1", need_facility=True)
    task2_1_1.add_target_component(c21)
    task2_1_2 = w2.create_task("task1_2")
    task2_1_2.add_target_component(c21)
    task2_2_1 = w2.create_task("task2_1")
    task2_2_1.add_target_component(c22)
    task2_3 = w2.create_task("task3", due_time=30)
    task2_3.add_target_component(c23)
    task2_3.add_input_task(task2_1_2)
    task2_3.add_input_task(task2_2_1)
    task2_1_2.add_input_task(task2_1_1)
    _ = w2.create_task("auto", auto_task=True, due_time=20)

    # Facilities in workplace
    workplace1 = project.create_workplace("workplace1")
    f1 = workplace1.create_facility("f1")
    f1.workamount_skill_mean_map = {
        task1_1_1.name: 1.0,
        task2_1_1.name: 1.0,  # same name as task1_1_1, so this is ignored.
    }
    workplace1.update_targeted_task_set({task1_1_1, task1_1_2, task1_2_1, task1_3})

    workplace2 = project.create_workplace("workplace2")
    f2 = workplace1.create_facility("f2")
    f2.workamount_skill_mean_map = {
        task1_1_1.name: 1.0,
        task2_1_1.name: 1.0,  # same name as task1_1_1, so this is ignored.
    }
    workplace2.update_targeted_task_set({task2_1_1, task2_1_2, task2_2_1, task2_3})

    # BaseTeams
    team1 = project.create_team("team1")
    team1.update_targeted_task_set({task1_1_1, task1_1_2, task1_2_1, task1_3})
    worker11 = team1.create_worker("w1", cost_per_time=10.0)
    worker11.workamount_skill_mean_map = {
        task1_1_1.name: 1.0,
        task1_1_2.name: 1.0,
        task1_2_1.name: 1.0,
        task1_3.name: 1.0,
    }
    worker11.facility_skill_map = {f1.name: 1.0}

    team2 = project.create_team("team2")
    team2.update_targeted_task_set({task2_1_1, task2_1_2, task2_2_1, task2_3})
    worker21 = team2.create_worker("w2", cost_per_time=6.0)
    worker21.solo_working = True
    worker21.workamount_skill_mean_map = {
        task2_1_1.name: 1.0,
        task2_1_2.name: 1.0,
        task2_2_1.name: 1.0,
        task2_3.name: 1.0,
    }
    worker21.facility_skill_map = {f2.name: 1.0}

    project.initialize()
    return project


@pytest.fixture(name="dummy_place_check")
def fixture_dummy_place_check():
    """Fixture for a dummy project for place checking.

    Returns:
        BaseProject: A dummy project instance for place checking.
    """
    c3 = BaseComponent("c3", space_size=1.0)
    c1 = BaseComponent("c1", space_size=1.0)
    c2 = BaseComponent("c2", space_size=1.0)
    task1 = BaseTask("t1", need_facility=True)
    task2 = BaseTask("t2", need_facility=True)
    task3 = BaseTask("t3", need_facility=True)

    c1.add_targeted_task(task1)
    c2.add_targeted_task(task2)
    c3.add_targeted_task(task3)

    # Facilities in workplace
    f1 = BaseFacility("f1")
    f1.solo_working = True
    f1.workamount_skill_mean_map = {
        task1.name: 1.0,
        task2.name: 1.0,
        task3.name: 1.0,
    }
    f2 = BaseFacility("f2")
    f2.solo_working = True
    f2.workamount_skill_mean_map = {
        task1.name: 1.0,
        task2.name: 1.0,
        task3.name: 1.0,
    }
    # Workplace
    workplace = BaseWorkplace("workplace", facility_set={f1, f2})
    workplace.update_targeted_task_set({task1, task2, task3})

    # BaseTeams
    team = BaseTeam("team")
    team.update_targeted_task_set({task1, task2, task3})

    # BaseWorkers in each BaseTeam
    w1 = BaseWorker("w1", team_id=team.ID, cost_per_time=10.0)
    w1.workamount_skill_mean_map = {
        task1.name: 1.0,
        task2.name: 1.0,
        task3.name: 1.0,
    }
    w1.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w1)

    w2 = BaseWorker("w2", team_id=team.ID, cost_per_time=6.0)
    w2.workamount_skill_mean_map = {
        task1.name: 1.0,
        task2.name: 1.0,
        task3.name: 1.0,
    }
    w2.facility_skill_map = {f2.name: 1.0}
    team.add_worker(w2)

    # BaseProject including BaseProduct, BaseWorkflow and BaseTeams and BaseWorkplaces
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_set={BaseProduct(component_set={c1, c2, c3})},
        workflow_set={BaseWorkflow(task_set={task1, task2, task3})},
        team_set={team},
        workplace_set={workplace},
    )

    return project


@pytest.fixture(name="dummy_simple_project")
def fixture_dummy_simple_project():
    """Fixture for a dummy simple project.

    Returns:
        BaseProject: A simple dummy project instance.
    """
    c = BaseComponent("c", space_size=1.0)
    task1 = BaseTask("task1", default_work_amount=2.0)
    task2 = BaseTask("task2", default_work_amount=2.0)
    auto_task2 = BaseTask("auto_task2", auto_task=True, default_work_amount=2.0)
    task2.add_input_task(auto_task2)
    task3 = BaseTask("task3", default_work_amount=2.0)
    auto_task3 = BaseTask("auto_task3", auto_task=True, default_work_amount=4.0)
    task3.add_input_task(auto_task3)
    workflow = BaseWorkflow(task_set={task1, task2, task3, auto_task2, auto_task3})
    c.update_targeted_task_set({task1, task2, task3})
    product = BaseProduct(component_set={c})

    # BaseTeams
    team = BaseTeam("team")
    team.update_targeted_task_set({task1, task2, task3})

    # BaseWorkers in each BaseTeam
    w1 = BaseWorker("w1", team_id=team.ID)
    w1.workamount_skill_mean_map = {
        task1.name: 1.0,
    }
    team.add_worker(w1)
    w2 = BaseWorker("w1", team_id=team.ID)
    w2.workamount_skill_mean_map = {
        task2.name: 1.0,
    }
    team.add_worker(w2)
    w3 = BaseWorker("w3", team_id=team.ID)
    w3.workamount_skill_mean_map = {
        task3.name: 1.0,
    }
    team.add_worker(w3)

    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_set={product},
        workflow_set={workflow},
        team_set={team},
    )
    return project


def test_simple_project_simulate(dummy_simple_project):
    """Test the simulation of a simple project.

    Args:
        dummy_simple_project (BaseProject): The dummy simple project fixture.
    """
    dummy_simple_project.simulate()

    # test for print_log
    for workflow in dummy_simple_project.workflow_set:
        workflow.print_all_log_in_chronological_order()
    for product in dummy_simple_project.product_set:
        product.print_all_log_in_chronological_order()
    for team in dummy_simple_project.team_set:
        team.print_all_log_in_chronological_order()
    for workplace in dummy_simple_project.workplace_set:
        workplace.print_all_log_in_chronological_order()
    dummy_simple_project.print_all_log_in_chronological_order()

    # test for print_log
    for workflow in dummy_simple_project.workflow_set:
        workflow.print_all_log_in_chronological_order(backward=True)
    for product in dummy_simple_project.product_set:
        product.print_all_log_in_chronological_order(backward=True)
    for team in dummy_simple_project.team_set:
        team.print_all_log_in_chronological_order(backward=True)
    for workplace in dummy_simple_project.workplace_set:
        workplace.print_all_log_in_chronological_order(backward=True)
    dummy_simple_project.print_all_log_in_chronological_order(backward=True)

    assert dummy_simple_project.time == 6.0
    dummy_simple_project.initialize()
    dummy_simple_project.simulate(absence_time_list=[1, 3, 5, 7, 9])
    assert dummy_simple_project.time == 11.0
    dummy_simple_project.initialize()
    dummy_simple_project.simulate(
        perform_auto_task_while_absence_time=True, absence_time_list=[1, 3, 5, 7, 9]
    )
    assert dummy_simple_project.time == 7.0


def test_init(dummy_project):
    """Test initialization and simulation of BaseProject.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    dummy_project.simulate(
        max_time=100,
    )
    dummy_project.create_gantt_plotly()


def test_initialize(dummy_project):
    """Test initialization/reset of BaseProject.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    dummy_project.initialize()
    assert dummy_project.status == BaseProjectStatus.NONE
    dummy_project.simulate()
    assert dummy_project.status == BaseProjectStatus.FINISHED_SUCCESS
    dummy_project.initialize()
    assert dummy_project.time == 0
    assert dummy_project.cost_record_list == []
    assert dummy_project.status == BaseProjectStatus.NONE


def test_absence_time_list_simulation(dummy_project):
    """Test simulation with absence time list.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    dummy_project.simulate()
    total_time = dummy_project.time
    assert total_time == 25

    absence_time_list = [1, 3, 4]
    dummy_project.simulate(absence_time_list=absence_time_list)
    assert dummy_project.time == total_time + len(absence_time_list)

    dummy_project.remove_absence_time_list()
    assert dummy_project.time == total_time

    dummy_project.insert_absence_time_list(absence_time_list)
    assert dummy_project.time == total_time + len(absence_time_list)

    absence_time_list = [1, 3, 4, 5]
    dummy_project.insert_absence_time_list(absence_time_list)
    assert dummy_project.time == total_time + len(absence_time_list)
    print(dummy_project.absence_time_list)


def test_set_last_datetime(dummy_project):
    """Test setting the last datetime.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    tmp_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    dummy_project.simulate()
    dummy_project.set_last_datetime(
        tmp_datetime, unit_timedelta=datetime.timedelta(days=1)
    )


def test_str():
    """Test string representation of BaseProject."""
    print(BaseProject())


def test_create_gantt_plotly(dummy_project, tmpdir):
    """Test creating a Gantt chart using Plotly.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
        tmpdir: Temporary directory provided by pytest.
    """
    dummy_project.simulate(
        max_time=100,
    )
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.create_gantt_plotly(save_fig_path=save_fig_path)


def test_get_networkx_graph(dummy_project):
    """Test getting a NetworkX graph from BaseProject.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    dummy_project.get_networkx_graph(view_workers=True, view_facilities=True)


def test_draw_networkx(dummy_project, tmpdir):
    """Test drawing a NetworkX graph.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
        tmpdir: Temporary directory provided by pytest.
    """
    for ext in ["png"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.draw_networkx(
            save_fig_path=save_fig_path, view_workers=True, view_facilities=True
        )


def test_get_node_and_edge_trace_for_plotly_network(dummy_project):
    """Test getting node and edge traces for Plotly network.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    dummy_project.get_node_and_edge_trace_for_plotly_network(
        view_workers=True, view_facilities=True
    )


def test_draw_plotly_network(dummy_project, tmpdir):
    """Test drawing a Plotly network.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
        tmpdir: Temporary directory provided by pytest.
    """
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.draw_plotly_network(save_fig_path=save_fig_path)


def test_simulate(dummy_project, dummy_project_multiple):
    """Test simulation of BaseProject and BaseProject with multiple products.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project.simulate(
        max_time=100,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
    )

    # dummy_project_multiple
    dummy_project_multiple.simulate(
        max_time=100,
    )


def test_backward_simulate(dummy_project):
    """Test backward simulation of BaseProject.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    dummy_project.backward_simulate(
        max_time=100,
    )

    dummy_project.backward_simulate(
        max_time=100,
        considering_due_time_of_tail_tasks=True,
    )


def test_simple_write_json(dummy_project):
    """Test writing and reading simple JSON for BaseProject.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    dummy_project.write_simple_json("test.json")
    read_p = BaseProject()
    read_p.read_simple_json("test.json")
    if os.path.exists("test.json"):
        os.remove("test.json")
    dummy_project.simulate(max_time=100)
    read_p.simulate(max_time=100)
    read_p.write_simple_json("test2.json")
    if os.path.exists("test2.json"):
        os.remove("test2.json")


@pytest.fixture(name="project_for_checking_space_judge")
def fixture_project_for_checking_space_judge():
    """Fixture for a project for checking space judge.

    Returns:
        BaseProject: A dummy project instance for space judge checking.
    """
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 4, 2, 8, 0, 0),
        unit_timedelta=datetime.timedelta(minutes=1),
    )
    # Components in Product
    a = BaseComponent("a")
    b = BaseComponent("b")

    # Register Product including Components in Project
    project.product_set = {BaseProduct(component_set={a, b})}

    # Tasks in Workflow
    # define work_amount and whether or not to need facility for each task
    task_a = BaseTask(
        "task_a",
        need_facility=True,
        worker_priority_rule=ResourcePriorityRuleMode.HSV,
        default_work_amount=2,
    )
    task_b = BaseTask(
        "task_b",
        need_facility=True,
        worker_priority_rule=ResourcePriorityRuleMode.HSV,
        default_work_amount=2,
    )

    # Register Workflow including Tasks in Project
    project.workflow_set = {BaseWorkflow(task_set={task_a, task_b})}

    # workplace in workplace model
    # define max_space_size which decide how many components can be placed
    workplace1 = BaseWorkplace("workplace1", max_space_size=3.0)
    workplace2 = BaseWorkplace("workplace2", max_space_size=3.0)

    # facility in workplace model
    # define workplace_id (each facility is placed which workplace) and cost_per_time
    machine1 = BaseFacility(
        "machine1", workplace_id=workplace1.ID, cost_per_time=10, solo_working=True
    )
    machine2 = BaseFacility(
        "machine2", workplace_id=workplace2.ID, cost_per_time=10, solo_working=True
    )

    # define each facility task skill value
    machine1.workamount_skill_mean_map = {task_a.name: 1.0, task_b.name: 1.0}
    machine2.workamount_skill_mean_map = {task_a.name: 1.0, task_b.name: 1.0}

    # define facilities belonging to each workplace
    workplace1.add_facility(machine1)
    workplace2.add_facility(machine2)

    # Team in team mode
    team = BaseTeam("factory_A")

    # worker in team model
    # define cost_per_time and add each worker to the relevant team
    w1 = BaseWorker("w1", cost_per_time=10.0)
    team.add_worker(w1)
    w2 = BaseWorker("w2", cost_per_time=10.0)
    team.add_worker(w2)

    # define each worker task skill value
    # (Set the skill value of an average worker as 1.0)
    w1.workamount_skill_mean_map = {task_a.name: 1.0, task_b.name: 1.0}
    w2.workamount_skill_mean_map = {task_a.name: 1.0, task_b.name: 1.0}

    # define each worker facility skill value
    w1.facility_skill_map = {machine1.name: 1.0}
    w2.facility_skill_map = {machine2.name: 1.0}

    # Register Teams and Workplaces in Project
    project.team_set = {team}
    project.workplace_set = {workplace1, workplace2}

    # Component <-> Task
    a.add_targeted_task(task_a)
    b.add_targeted_task(task_b)

    # Team <-> Task
    team.update_targeted_task_set({task_a, task_b})

    # Workplace <-> Task
    workplace1.update_targeted_task_set({task_a, task_b})
    workplace2.update_targeted_task_set({task_a, task_b})

    return project


def test_project_for_checking_space_judge(project_for_checking_space_judge):
    """Test project for checking space judge.

    Args:
        project_for_checking_space_judge (BaseProject): The dummy project fixture.
    """
    task0 = next(
        (
            task
            for task in project_for_checking_space_judge.get_all_task_set()
            if task.name == "task_a"
        ),
        None,
    )
    task1 = next(
        (
            task
            for task in project_for_checking_space_judge.get_all_task_set()
            if task.name == "task_b"
        ),
        None,
    )
    task0.workplace_priority_rule = WorkplacePriorityRuleMode.FSS
    task1.workplace_priority_rule = WorkplacePriorityRuleMode.FSS
    project_for_checking_space_judge.simulate(max_time=100)
    assert task0.state_record_list[0] == task1.state_record_list[0]
    task0.workplace_priority_rule = WorkplacePriorityRuleMode.SSP
    task1.workplace_priority_rule = WorkplacePriorityRuleMode.SSP
    project_for_checking_space_judge.simulate(max_time=100)
    assert task0.state_record_list[0] != task1.state_record_list[0]


@pytest.fixture(name="dummy_conveyor_project")
def fixture_dummy_conveyor_project():
    """Fixture for a dummy conveyor project.

    Returns:
        BaseProject: A dummy conveyor project instance.
    """
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    task_a1 = BaseTask("A1", need_facility=True, default_work_amount=10)
    task_a2 = BaseTask("A2", need_facility=True, default_work_amount=3)
    task_a3 = BaseTask("A3", need_facility=True, default_work_amount=3)
    task_b1 = BaseTask("B1", need_facility=True, default_work_amount=3)
    task_b2 = BaseTask("B2", need_facility=True, default_work_amount=5)
    task_b3 = BaseTask("B3", need_facility=True, default_work_amount=3)

    c1.update_targeted_task_set({task_a1, task_b1})
    c2.update_targeted_task_set({task_a2, task_b2})
    c3.update_targeted_task_set({task_a3, task_b3})

    task_b1.add_input_task(task_a1)
    task_b2.add_input_task(task_a2)
    task_b3.add_input_task(task_a3)

    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }

    f2 = BaseFacility("f2")
    f2.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }

    f3 = BaseFacility("f3")
    f3.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }
    f4 = BaseFacility("f4")
    f4.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }

    # Workplace
    wp1 = BaseWorkplace("workplace1", facility_set={f1})
    wp1.update_targeted_task_set({task_a1, task_a2, task_a3})
    wp2 = BaseWorkplace("workplace2", facility_set={f2})
    wp2.update_targeted_task_set({task_a1, task_a2, task_a3})
    wp3 = BaseWorkplace("workplace3", facility_set={f3})
    wp3.update_targeted_task_set({task_b1, task_b2, task_b3})
    wp4 = BaseWorkplace("workplace4", facility_set={f4})
    wp4.update_targeted_task_set({task_b1, task_b2, task_b3})

    wp3.add_input_workplace(wp1)
    wp4.add_input_workplace(wp2)

    # BaseTeams
    team = BaseTeam("team")
    team_set = {team}
    team.update_targeted_task_set(
        {task_a1, task_a2, task_a3, task_b1, task_b2, task_b3}
    )

    # BaseWorkers in each BaseTeam
    w1 = BaseWorker("w1", team_id=team.ID)
    w1.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }
    w1.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w1)

    w2 = BaseWorker("w2", team_id=team.ID)
    w2.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }
    w2.facility_skill_map = {f2.name: 1.0}
    team.add_worker(w2)

    w3 = BaseWorker("w3", team_id=team.ID)
    w3.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }
    w3.facility_skill_map = {f3.name: 1.0}
    team.add_worker(w3)

    w4 = BaseWorker("w4", team_id=team.ID)
    w4.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }
    w4.facility_skill_map = {f4.name: 1.0}
    team.add_worker(w4)

    workplace_set = {wp1, wp2, wp3, wp4}
    # BaseProject including BaseProduct, BaseWorkflow and BaseTeams and BaseWorkplaces
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 7, 18, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_set={BaseProduct(component_set={c1, c2, c3})},
        workflow_set={
            BaseWorkflow(
                task_set={task_a1, task_a2, task_a3, task_b1, task_b2, task_b3}
            )
        },
        team_set=team_set,
        workplace_set=workplace_set,
    )
    return project


def test_component_place_check_1(dummy_conveyor_project):
    """Test component place check 1.

    Args:
        dummy_conveyor_project (BaseProject): The dummy conveyor project fixture.
    """
    dummy_conveyor_project.simulate(
        max_time=100,
        # weekend_working=False,
    )
    wp1 = next(
        wp for wp in dummy_conveyor_project.workplace_set if wp.name == "workplace1"
    )
    wp2 = next(
        wp for wp in dummy_conveyor_project.workplace_set if wp.name == "workplace2"
    )
    wp3 = next(
        wp for wp in dummy_conveyor_project.workplace_set if wp.name == "workplace3"
    )
    wp4 = next(
        wp for wp in dummy_conveyor_project.workplace_set if wp.name == "workplace4"
    )

    component_wp1_list = []
    wp1_c_id_record_list = wp1.placed_component_id_set_record_list
    for c_id_record_list in wp1_c_id_record_list:
        component_wp1_list.extend(c_id_record_list)

    component_wp2_list = []
    wp2_c_id_record_list = wp2.placed_component_id_set_record_list
    for c_id_record_list in wp2_c_id_record_list:
        component_wp2_list.extend(c_id_record_list)

    component_wp3_list = []
    wp3_c_id_record_list = wp3.placed_component_id_set_record_list
    for c_id_record_list in wp3_c_id_record_list:
        component_wp3_list.extend(c_id_record_list)

    component_wp4_list = []
    wp4_c_id_record_list = wp4.placed_component_id_set_record_list
    for c_id_record_list in wp4_c_id_record_list:
        component_wp4_list.extend(c_id_record_list)

    assert set(component_wp1_list) == set(component_wp3_list)
    assert set(component_wp2_list) == set(component_wp4_list)

    # backward
    dummy_conveyor_project.backward_simulate(
        max_time=100,
    )


@pytest.fixture(name="dummy_conveyor_project_with_child_component")
def fixture_dummy_conveyor_project_with_child_component():
    """Fixture for a dummy conveyor project with child components.

    Returns:
        BaseProject: A dummy conveyor project instance with child components.
    """
    c1_1 = BaseComponent("c1_1")
    c1_2 = BaseComponent("c1_2")
    c2_1 = BaseComponent("c2_1")
    c2_2 = BaseComponent("c2_2")
    c3_1 = BaseComponent("c3_1")
    c3_2 = BaseComponent("c3_2")

    c1_2.add_child_component(c1_1)
    c2_2.add_child_component(c2_1)
    c3_2.add_child_component(c3_1)

    task_a1 = BaseTask("A1", need_facility=True, default_work_amount=6)
    task_a2 = BaseTask("A2", need_facility=True, default_work_amount=2)
    task_a3 = BaseTask("A3", need_facility=True, default_work_amount=2)
    task_b1 = BaseTask("B1", need_facility=True, default_work_amount=2)
    task_b2 = BaseTask("B2", need_facility=True, default_work_amount=7)
    task_b3 = BaseTask("B3", need_facility=True, default_work_amount=2)

    c1_1.add_targeted_task(task_a1)
    c1_2.add_targeted_task(task_b1)
    c2_1.add_targeted_task(task_a2)
    c2_2.add_targeted_task(task_b2)
    c3_1.add_targeted_task(task_a3)
    c3_2.add_targeted_task(task_b3)

    task_b1.add_input_task(task_a1)
    task_b2.add_input_task(task_a2)
    task_b3.add_input_task(task_a3)

    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }

    f2 = BaseFacility("f2")
    f2.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }

    f3 = BaseFacility("f3")
    f3.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }
    f4 = BaseFacility("f4")
    f4.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }

    # Workplace
    wp1 = BaseWorkplace("workplace1", facility_set={f1}, max_space_size=1.0)
    wp1.update_targeted_task_set({task_a1, task_a2, task_a3})
    wp2 = BaseWorkplace("workplace2", facility_set={f2}, max_space_size=2.0)
    wp2.update_targeted_task_set({task_a1, task_a2, task_a3})
    wp3 = BaseWorkplace("workplace3", facility_set={f3}, max_space_size=4.0)
    wp3.update_targeted_task_set({task_b1, task_b2, task_b3})
    wp4 = BaseWorkplace("workplace4", facility_set={f4}, max_space_size=4.0)
    wp4.update_targeted_task_set({task_b1, task_b2, task_b3})

    wp3.add_input_workplace(wp1)
    wp4.add_input_workplace(wp2)

    # BaseTeams
    team = BaseTeam("team")
    team_set = {team}
    team.update_targeted_task_set(
        {task_a1, task_a2, task_a3, task_b1, task_b2, task_b3}
    )

    # BaseWorkers in each BaseTeam
    w1 = BaseWorker("w1", team_id=team.ID)
    w1.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }
    w1.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w1)

    w2 = BaseWorker("w2", team_id=team.ID)
    w2.workamount_skill_mean_map = {
        task_a1.name: 1.0,
        task_a2.name: 1.0,
        task_a3.name: 1.0,
    }
    w2.facility_skill_map = {f2.name: 1.0}
    team.add_worker(w2)

    w3 = BaseWorker("w3", team_id=team.ID)
    w3.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }
    w3.facility_skill_map = {f3.name: 1.0}
    team.add_worker(w3)

    w4 = BaseWorker("w4", team_id=team.ID)
    w4.workamount_skill_mean_map = {
        task_b1.name: 1.0,
        task_b2.name: 1.0,
        task_b3.name: 1.0,
    }
    w4.facility_skill_map = {f4.name: 1.0}
    team.add_worker(w4)

    workplace_set = {wp1, wp2, wp3, wp4}
    # BaseProject including BaseProduct, BaseWorkflow and BaseTeams and BaseWorkplaces
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 8, 20, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_set={BaseProduct(component_set={c1_1, c1_2, c2_1, c2_2, c3_1, c3_2})},
        workflow_set={
            BaseWorkflow(
                task_set={task_a1, task_a2, task_a3, task_b1, task_b2, task_b3}
            )
        },
        team_set=team_set,
        workplace_set=workplace_set,
    )
    return project


def test_component_place_check_2(dummy_conveyor_project_with_child_component):
    """Test component place check 2.

    Args:
        dummy_conveyor_project_with_child_component (BaseProject): The dummy conveyor project with child components fixture.
    """
    dummy_conveyor_project_with_child_component.simulate(
        max_time=100,
    )

    # backward
    dummy_conveyor_project_with_child_component.backward_simulate(
        max_time=100,
    )


def test_subproject_task(dummy_project):
    """Test the subproject task.

    Args:
        dummy_project (BaseProject): The dummy project fixture.
    """
    file_path = ["sub1.json", "sub2.json", "total.json"]
    dummy_project.simulate()
    dummy_project.write_simple_json(file_path[0])
    dummy_project.unit_timedelta = datetime.timedelta(minutes=2)
    dummy_project.simulate()
    dummy_project.write_simple_json(file_path[1])

    # make project including two sub projects
    project = BaseProject(unit_timedelta=datetime.timedelta(minutes=10))
    sub1 = BaseSubProjectTask("sub1")
    sub1.set_all_attributes_from_json(file_path[0])
    sub1.set_work_amount_progress_of_unit_step_time(dummy_project.unit_timedelta)
    sub2 = BaseSubProjectTask("sub2")
    sub2.set_all_attributes_from_json(file_path[1])
    sub2.set_work_amount_progress_of_unit_step_time(dummy_project.unit_timedelta)
    sub2.add_input_task(sub1)
    project.workflow = BaseWorkflow()
    project.workflow.task_set = {sub1, sub2}
    project.simulate()
    project.write_simple_json(file_path[2])
    project2 = BaseProject()
    project2.read_simple_json(file_path[2])

    for file_p in file_path:
        if os.path.exists(file_p):
            os.remove(file_p)


def test_print_mermaid_diagram(dummy_project_multiple, dummy_conveyor_project):
    """Test printing Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
        dummy_conveyor_project (BaseProject): The dummy conveyor project fixture.
    """
    dummy_project_multiple.print_mermaid_diagram(orientations="LR", subgraph=True)
    dummy_project_multiple.print_target_mermaid_diagram(
        target_product_set=dummy_project_multiple.product_set,
        target_workflow_set=dummy_project_multiple.workflow_set,
        target_team_set=dummy_project_multiple.team_set,
        orientations="TB",
        subgraph=False,
    )
    dummy_conveyor_project.print_mermaid_diagram()


def test_print_target_product_related_mermaid_diagram(dummy_project_multiple):
    """Test printing target product related Mermaid diagram.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_target_product_related_mermaid_diagram(
        target_product_set=dummy_project_multiple.product_set,
        orientations="TB",
        subgraph=False,
    )


def test_print_target_team_related_mermaid_diagram(dummy_project_multiple):
    """Test printing target team related Mermaid diagram.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_target_team_related_mermaid_diagram(
        target_team_set=dummy_project_multiple.team_set,
        orientations="TB",
        subgraph=False,
    )


def test_print_target_workplace_related_mermaid_diagram(dummy_project_multiple):
    """Test printing target workplace related Mermaid diagram.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_target_workplace_related_mermaid_diagram(
        target_workplace_set=dummy_project_multiple.workplace_set,
        orientations="TB",
        subgraph=False,
    )


def test_print_target_workflow_related_mermaid_diagram(dummy_project_multiple):
    """Test printing target workflow related Mermaid diagram.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_target_workflow_related_mermaid_diagram(
        target_workflow_set=dummy_project_multiple.workflow_set,
        orientations="TB",
        subgraph=False,
    )


def test_print_all_product_mermaid_diagram(dummy_project_multiple):
    """Test printing all product Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_all_product_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_workflow_mermaid_diagram(dummy_project_multiple):
    """Test printing all workflow Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_all_workflow_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_team_mermaid_diagram(dummy_project_multiple):
    """Test printing all team Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_all_team_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_workplace_mermaid_diagram(dummy_project_multiple):
    """Test printing all workplace Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.print_all_workplace_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_xxxx_gantt_mermaid_diagram(dummy_project_multiple):
    """Test printing all Gantt Mermaid diagrams for products, workflows, teams, and workplaces.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_product_gantt_mermaid(range_time=(8, 11))
    dummy_project_multiple.print_all_workflow_gantt_mermaid(range_time=(8, 11))
    dummy_project_multiple.print_all_team_gantt_mermaid(range_time=(8, 11))
    dummy_project_multiple.print_all_workplace_gantt_mermaid(range_time=(8, 11))


def test_print_all_product_gantt_mermaid_diagram(dummy_project_multiple):
    """Test printing all product Gantt Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_product_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


def test_print_all_workflow_gantt_mermaid_diagram(dummy_project_multiple):
    """Test printing all workflow Gantt Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_workflow_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


def test_print_all_team_gantt_mermaid_diagram(dummy_project_multiple):
    """Test printing all team Gantt Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_team_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


def test_print_all_workplace_gantt_mermaid_diagram(dummy_project_multiple):
    """Test printing all workplace Gantt Mermaid diagrams.

    Args:
        dummy_project_multiple (BaseProject): The dummy project with multiple products fixture.
    """
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_workplace_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


@pytest.fixture(name="dummy_auto_task_project")
def fixture_dummy_auto_task_project():
    """Fixture for a dummy auto task project.

    Returns:
        BaseProject: A dummy project instance with an auto task.
    """
    task1 = BaseTask("task1", default_work_amount=2.0, auto_task=True)
    workflow = BaseWorkflow(task_set={task1})

    component = BaseComponent("c")
    component.add_targeted_task(task1)
    product = BaseProduct(component_set={component})

    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_set={product},
        workflow_set={workflow},
    )
    return project
