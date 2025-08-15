#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_base_project."""

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
from pDESy.model.base_task import BaseTask, BaseTaskState
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_workflow import BaseWorkflow
from pDESy.model.base_workplace import BaseWorkplace


@pytest.fixture(name="dummy_project")
def fixture_dummy_project():
    """dummy_project."""
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(minutes=1),
    )

    # BaseComponents in BaseProduct
    c3 = BaseComponent("c3")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3.extend_child_component_list([c1, c2])
    project.append_product(BaseProduct(component_list=[c1, c2, c3]))

    # BaseTasks in BaseWorkflow
    task1_1 = BaseTask("task1_1", need_facility=True)
    task1_2 = BaseTask("task1_2", worker_priority_rule=ResourcePriorityRuleMode.HSV)
    task2_1 = BaseTask("task2_1")
    task3 = BaseTask("task3", due_time=30)
    task3.append_input_task_dependency(task1_2)
    task3.append_input_task_dependency(task2_1)
    task1_2.append_input_task_dependency(task1_1)
    task0 = BaseTask("auto", auto_task=True, due_time=20)
    project.append_workflow(
        BaseWorkflow(task_list=[task1_1, task1_2, task2_1, task3, task0])
    )

    c1.extend_targeted_task_list([task1_1, task1_2])
    c2.append_targeted_task(task2_1)
    c3.append_targeted_task(task3)

    # Facilities in workplace
    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
    }

    # Workplace
    workplace = BaseWorkplace("workplace", facility_list=[f1])
    workplace.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])
    project.append_workplace(workplace)

    # BaseTeam
    team = BaseTeam("team")
    team.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])
    project.append_team(team)

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
    """dummy_project_multiple."""
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
    )

    # BaseComponent in BaseProducts
    c13 = BaseComponent("c3")
    c11 = BaseComponent("c1")
    c12 = BaseComponent("c2")
    c13.extend_child_component_list([c11, c12])
    p1 = BaseProduct(name="product 1", component_list=[c11, c12, c13])

    c23 = BaseComponent("c3")
    c21 = BaseComponent("c1")
    c22 = BaseComponent("c2")
    c23.extend_child_component_list([c21, c22])
    p2 = BaseProduct(name="product2", component_list=[c21, c22, c23])

    project.extend_product_list([p1, p2])

    # BaseTask in BaseWorkflows
    task1_1_1 = BaseTask("task1_1", need_facility=True)
    task1_1_2 = BaseTask("task1_2")
    task1_2_1 = BaseTask("task2_1")
    task1_3 = BaseTask("task3", due_time=30)
    task1_3.append_input_task_dependency(task1_1_2)
    task1_3.append_input_task_dependency(task1_2_1)
    task1_1_2.append_input_task_dependency(task1_1_1)
    task1_0 = BaseTask("auto", auto_task=True, due_time=20)
    w1 = BaseWorkflow(
        name="workflow 1", task_list=[task1_1_1, task1_1_2, task1_2_1, task1_3, task1_0]
    )
    c11.extend_targeted_task_list([task1_1_1, task1_1_2])
    c12.append_targeted_task(task1_2_1)
    c13.append_targeted_task(task1_3)

    task2_1_1 = BaseTask("task1_1", need_facility=True)
    task2_1_2 = BaseTask("task1_2")
    task2_2_1 = BaseTask("task2_1")
    task2_3 = BaseTask("task3", due_time=30)
    task2_3.append_input_task_dependency(task2_1_2)
    task2_3.append_input_task_dependency(task2_2_1)
    task2_1_2.append_input_task_dependency(task2_1_1)
    task2_0 = BaseTask("auto", auto_task=True, due_time=20)
    w2 = BaseWorkflow(
        name="workflow 2", task_list=[task2_1_1, task2_1_2, task2_2_1, task2_3, task2_0]
    )
    c21.extend_targeted_task_list([task2_1_1, task2_1_2])
    c22.append_targeted_task(task2_2_1)
    c23.append_targeted_task(task2_3)

    project.extend_workflow_list([w1, w2])

    # Facilities in workplace
    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task1_1_1.name: 1.0,
        task2_1_1.name: 1.0,  # same name as task1_1_1, so this is ignored.
    }
    workplace1 = BaseWorkplace("workplace1", facility_list=[f1])
    workplace1.extend_targeted_task_list([task1_1_1, task1_1_2, task1_2_1, task1_3])

    f2 = BaseFacility("f2")
    f2.workamount_skill_mean_map = {
        task1_1_1.name: 1.0,
        task2_1_1.name: 1.0,  # same name as task1_1_1, so this is ignored.
    }
    workplace2 = BaseWorkplace("workplace2", facility_list=[f2])
    workplace2.extend_targeted_task_list([task2_1_1, task2_1_2, task2_2_1, task2_3])

    project.extend_workplace_list([workplace1, workplace2])

    # BaseTeams
    team1 = BaseTeam("team1")
    team1.extend_targeted_task_list([task1_1_1, task1_1_2, task1_2_1, task1_3])
    worker11 = BaseWorker("w11", cost_per_time=10.0)
    worker11.workamount_skill_mean_map = {
        task1_1_1.name: 1.0,
        task1_1_2.name: 1.0,
        task1_2_1.name: 1.0,
        task1_3.name: 1.0,
    }
    worker11.facility_skill_map = {f1.name: 1.0}
    team1.add_worker(worker11)

    team2 = BaseTeam("team2")
    team2.extend_targeted_task_list([task2_1_1, task2_1_2, task2_2_1, task2_3])
    worker21 = BaseWorker("w2", cost_per_time=6.0)
    worker21.solo_working = True
    worker21.workamount_skill_mean_map = {
        task2_1_1.name: 1.0,
        task2_1_2.name: 1.0,
        task2_2_1.name: 1.0,
        task2_3.name: 1.0,
    }
    worker21.facility_skill_map = {f2.name: 1.0}
    team2.add_worker(worker21)

    project.extend_team_list([team1, team2])

    project.initialize()
    return project


@pytest.fixture(name="dummy_place_check")
def fixture_dummy_place_check():
    """dummy_place_check."""
    c3 = BaseComponent("c3", space_size=1.0)
    c1 = BaseComponent("c1", space_size=1.0)
    c2 = BaseComponent("c2", space_size=1.0)
    task1 = BaseTask("t1", need_facility=True)
    task2 = BaseTask("t2", need_facility=True)
    task3 = BaseTask("t3", need_facility=True)

    c1.append_targeted_task(task1)
    c2.append_targeted_task(task2)
    c3.append_targeted_task(task3)

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
    workplace = BaseWorkplace("workplace", facility_list=[f1, f2])
    workplace.extend_targeted_task_list([task1, task2, task3])

    # BaseTeams
    team = BaseTeam("team")
    team.extend_targeted_task_list([task1, task2, task3])

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
        product_list=[BaseProduct(component_list=[c1, c2, c3])],
        workflow_list=[BaseWorkflow(task_list=[task1, task2, task3])],
        team_list=[team],
        workplace_list=[workplace],
    )

    return project


@pytest.fixture(name="dummy_simple_project")
def fixture_dummy_simple_project():
    """Create a dummy simple project."""
    c = BaseComponent("c", space_size=1.0)
    task1 = BaseTask("task1", default_work_amount=2.0)
    task2 = BaseTask("task2", default_work_amount=2.0)
    auto_task2 = BaseTask("auto_task2", auto_task=True, default_work_amount=2.0)
    task2.append_input_task_dependency(auto_task2)
    task3 = BaseTask("task3", default_work_amount=2.0)
    auto_task3 = BaseTask("auto_task3", auto_task=True, default_work_amount=4.0)
    task3.append_input_task_dependency(auto_task3)
    workflow = BaseWorkflow(task_list=[task1, task2, task3, auto_task2, auto_task3])
    c.extend_targeted_task_list([task1, task2, task3])
    product = BaseProduct(component_list=[c])

    # BaseTeams
    team = BaseTeam("team")
    team.extend_targeted_task_list([task1, task2, task3])

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
        product_list=[product],
        workflow_list=[workflow],
        team_list=[team],
    )
    return project


def test_simple_project_simulate(dummy_simple_project):
    """Test the simulation of a simple project."""
    dummy_simple_project.simulate()

    # test for print_log
    for workflow in dummy_simple_project.workflow_list:
        workflow.print_all_log_in_chronological_order()
    for product in dummy_simple_project.product_list:
        product.print_all_log_in_chronological_order()
    for team in dummy_simple_project.team_list:
        team.print_all_log_in_chronological_order()
    for workplace in dummy_simple_project.workplace_list:
        workplace.print_all_log_in_chronological_order()
    dummy_simple_project.print_all_log_in_chronological_order()

    # test for print_log
    for workflow in dummy_simple_project.workflow_list:
        workflow.print_all_log_in_chronological_order(backward=True)
    for product in dummy_simple_project.product_list:
        product.print_all_log_in_chronological_order(backward=True)
    for team in dummy_simple_project.team_list:
        team.print_all_log_in_chronological_order(backward=True)
    for workplace in dummy_simple_project.workplace_list:
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


def test_place_check(dummy_place_check):
    """test_place_check."""
    # workplace space size = 1.5
    dummy_place_check.workplace_list[0].max_space_size = 1.5
    dummy_place_check.simulate(max_time=100)
    # workplace space size = 2
    dummy_place_check.workplace_list[0].max_space_size = 2.0
    dummy_place_check.simulate(max_time=100)


def test_init(dummy_project):
    """test_init."""
    dummy_project.simulate(
        max_time=100,
    )
    dummy_project.create_gantt_plotly()


def test_initialize(dummy_project):
    """test_initialize."""
    dummy_project.initialize()
    assert dummy_project.status == BaseProjectStatus.NONE
    dummy_project.simulate()
    assert dummy_project.status == BaseProjectStatus.FINISHED_SUCCESS
    dummy_project.initialize()
    assert dummy_project.time == 0
    assert dummy_project.cost_list == []
    assert dummy_project.status == BaseProjectStatus.NONE


def test_absence_time_list_simulation(dummy_project):
    """test_absence_time_list_simulation"""
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
    """test_set_last_datetime."""
    tmp_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    dummy_project.simulate()
    dummy_project.set_last_datetime(
        tmp_datetime, unit_timedelta=datetime.timedelta(days=1)
    )


def test_str():
    """test_str."""
    print(BaseProject())


def test_create_gantt_plotly(dummy_project, tmpdir):
    """test_create_gantt_plotly."""
    dummy_project.simulate(
        max_time=100,
    )
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.create_gantt_plotly(save_fig_path=save_fig_path)


def test_get_networkx_graph(dummy_project):
    """test_get_networkx_graph."""
    dummy_project.get_networkx_graph(view_workers=True, view_facilities=True)


def test_draw_networkx(dummy_project, tmpdir):
    """test_draw_networkx."""
    for ext in ["png"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.draw_networkx(
            save_fig_path=save_fig_path, view_workers=True, view_facilities=True
        )


def test_get_node_and_edge_trace_for_plotly_network(dummy_project):
    """test_get_node_and_edge_trace_for_plotly_network."""
    dummy_project.get_node_and_edge_trace_for_plotly_network(
        view_workers=True, view_facilities=True
    )


def test_draw_plotly_network(dummy_project, tmpdir):
    """test_draw_plotly_network."""
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.draw_plotly_network(save_fig_path=save_fig_path)


def test_simulate(dummy_project, dummy_project_multiple):
    """test_simulate."""
    dummy_project.simulate(
        max_time=100,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
    )

    # dummy_project_multiple
    dummy_project_multiple.simulate(
        max_time=100,
    )


def test_backward_simulate(dummy_project):
    """test_backward_simulate."""
    dummy_project.backward_simulate(
        max_time=100,
    )

    dummy_project.backward_simulate(
        max_time=100,
        considering_due_time_of_tail_tasks=True,
    )


def test_simple_write_json(dummy_project):
    """test_simple_write_json."""
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
    """project_for_checking_space_judge."""
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 4, 2, 8, 0, 0),
        unit_timedelta=datetime.timedelta(minutes=1),
    )
    # Components in Product
    a = BaseComponent("a")
    b = BaseComponent("b")

    # Register Product including Components in Project
    project.product_list = [BaseProduct(component_list=[a, b])]

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
    project.workflow_list = [BaseWorkflow(task_list=[task_a, task_b])]

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
    project.team_list = [team]
    project.workplace_list = [workplace1, workplace2]

    # Component <-> Task
    a.append_targeted_task(task_a)
    b.append_targeted_task(task_b)

    # Team <-> Task
    team.extend_targeted_task_list([task_a, task_b])

    # Workplace <-> Task
    workplace1.extend_targeted_task_list([task_a, task_b])
    workplace2.extend_targeted_task_list([task_a, task_b])

    return project


def test_project_for_checking_space_judge(project_for_checking_space_judge):
    """test_project_for_checking_space_judge."""
    task_list = project_for_checking_space_judge.get_all_task_list()
    task_list[0].workplace_priority_rule = WorkplacePriorityRuleMode.FSS
    task_list[1].workplace_priority_rule = WorkplacePriorityRuleMode.FSS
    project_for_checking_space_judge.simulate(max_time=100)
    assert task_list[0].state_record_list[0] == task_list[1].state_record_list[0]
    task_list[0].workplace_priority_rule = WorkplacePriorityRuleMode.SSP
    task_list[1].workplace_priority_rule = WorkplacePriorityRuleMode.SSP
    project_for_checking_space_judge.simulate(max_time=100)
    assert task_list[0].state_record_list[0] != task_list[1].state_record_list[0]


@pytest.fixture(name="dummy_conveyor_project")
def fixture_dummy_conveyor_project():
    """dummy_conveyor_project."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    task_a1 = BaseTask("A1", need_facility=True, default_work_amount=10)
    task_a2 = BaseTask("A2", need_facility=True, default_work_amount=3)
    task_a3 = BaseTask("A3", need_facility=True, default_work_amount=3)
    task_b1 = BaseTask("B1", need_facility=True, default_work_amount=3)
    task_b2 = BaseTask("B2", need_facility=True, default_work_amount=5)
    task_b3 = BaseTask("B3", need_facility=True, default_work_amount=3)

    c1.extend_targeted_task_list([task_a1, task_b1])
    c2.extend_targeted_task_list([task_a2, task_b2])
    c3.extend_targeted_task_list([task_a3, task_b3])

    task_b1.append_input_task_dependency(task_a1)
    task_b2.append_input_task_dependency(task_a2)
    task_b3.append_input_task_dependency(task_a3)

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
    wp1 = BaseWorkplace("workplace1", facility_list=[f1])
    wp1.extend_targeted_task_list([task_a1, task_a2, task_a3])
    wp2 = BaseWorkplace("workplace2", facility_list=[f2])
    wp2.extend_targeted_task_list([task_a1, task_a2, task_a3])
    wp3 = BaseWorkplace("workplace3", facility_list=[f3])
    wp3.extend_targeted_task_list([task_b1, task_b2, task_b3])
    wp4 = BaseWorkplace("workplace4", facility_list=[f4])
    wp4.extend_targeted_task_list([task_b1, task_b2, task_b3])

    wp3.append_input_workplace(wp1)
    wp4.append_input_workplace(wp2)

    # BaseTeams
    team = BaseTeam("team")
    team_list = [team]
    team.extend_targeted_task_list(
        [task_a1, task_a2, task_a3, task_b1, task_b2, task_b3]
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

    workplace_list = [wp1, wp2, wp3, wp4]
    # BaseProject including BaseProduct, BaseWorkflow and BaseTeams and BaseWorkplaces
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 7, 18, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_list=[BaseProduct(component_list=[c1, c2, c3])],
        workflow_list=[
            BaseWorkflow(
                task_list=[task_a1, task_a2, task_a3, task_b1, task_b2, task_b3]
            )
        ],
        team_list=team_list,
        workplace_list=workplace_list,
    )
    return project


def test_component_place_check_1(dummy_conveyor_project):
    """test_component_place_check_1."""
    dummy_conveyor_project.simulate(
        max_time=100,
        # weekend_working=False,
    )

    component_wp1_list = []
    wp1 = dummy_conveyor_project.workplace_list[0]
    wp1_c_id_record = wp1.placed_component_id_record
    for c_id_record in wp1_c_id_record:
        component_wp1_list.extend(c_id_record)

    component_wp2_list = []
    wp2 = dummy_conveyor_project.workplace_list[1]
    wp2_c_id_record = wp2.placed_component_id_record
    for c_id_record in wp2_c_id_record:
        component_wp2_list.extend(c_id_record)

    component_wp3_list = []
    wp3 = dummy_conveyor_project.workplace_list[2]
    wp3_c_id_record = wp3.placed_component_id_record
    for c_id_record in wp3_c_id_record:
        component_wp3_list.extend(c_id_record)

    component_wp4_list = []
    wp4 = dummy_conveyor_project.workplace_list[3]
    wp4_c_id_record = wp4.placed_component_id_record
    for c_id_record in wp4_c_id_record:
        component_wp4_list.extend(c_id_record)

    assert set(component_wp1_list) == set(component_wp3_list)
    assert set(component_wp2_list) == set(component_wp4_list)

    # backward
    dummy_conveyor_project.backward_simulate(
        max_time=100,
    )


@pytest.fixture(name="dummy_conveyor_project_with_child_component")
def fixture_dummy_conveyor_project_with_child_component():
    """dummy_conveyor_project_with_child_component."""
    c1_1 = BaseComponent("c1_1")
    c1_2 = BaseComponent("c1_2")
    c2_1 = BaseComponent("c2_1")
    c2_2 = BaseComponent("c2_2")
    c3_1 = BaseComponent("c3_1")
    c3_2 = BaseComponent("c3_2")

    c1_2.append_child_component(c1_1)
    c2_2.append_child_component(c2_1)
    c3_2.append_child_component(c3_1)

    task_a1 = BaseTask("A1", need_facility=True, default_work_amount=6)
    task_a2 = BaseTask("A2", need_facility=True, default_work_amount=2)
    task_a3 = BaseTask("A3", need_facility=True, default_work_amount=2)
    task_b1 = BaseTask("B1", need_facility=True, default_work_amount=2)
    task_b2 = BaseTask("B2", need_facility=True, default_work_amount=7)
    task_b3 = BaseTask("B3", need_facility=True, default_work_amount=2)

    c1_1.append_targeted_task(task_a1)
    c1_2.append_targeted_task(task_b1)
    c2_1.append_targeted_task(task_a2)
    c2_2.append_targeted_task(task_b2)
    c3_1.append_targeted_task(task_a3)
    c3_2.append_targeted_task(task_b3)

    task_b1.append_input_task_dependency(task_a1)
    task_b2.append_input_task_dependency(task_a2)
    task_b3.append_input_task_dependency(task_a3)

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
    wp1 = BaseWorkplace("workplace1", facility_list=[f1], max_space_size=1.0)
    wp1.extend_targeted_task_list([task_a1, task_a2, task_a3])
    wp2 = BaseWorkplace("workplace2", facility_list=[f2], max_space_size=2.0)
    wp2.extend_targeted_task_list([task_a1, task_a2, task_a3])
    wp3 = BaseWorkplace("workplace3", facility_list=[f3], max_space_size=4.0)
    wp3.extend_targeted_task_list([task_b1, task_b2, task_b3])
    wp4 = BaseWorkplace("workplace4", facility_list=[f4], max_space_size=4.0)
    wp4.extend_targeted_task_list([task_b1, task_b2, task_b3])

    wp3.append_input_workplace(wp1)
    wp4.append_input_workplace(wp2)

    # BaseTeams
    team = BaseTeam("team")
    team_list = [team]
    team.extend_targeted_task_list(
        [task_a1, task_a2, task_a3, task_b1, task_b2, task_b3]
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

    workplace_list = [wp1, wp2, wp3, wp4]
    # BaseProject including BaseProduct, BaseWorkflow and BaseTeams and BaseWorkplaces
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 8, 20, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_list=[BaseProduct(component_list=[c1_1, c1_2, c2_1, c2_2, c3_1, c3_2])],
        workflow_list=[
            BaseWorkflow(
                task_list=[task_a1, task_a2, task_a3, task_b1, task_b2, task_b3]
            )
        ],
        team_list=team_list,
        workplace_list=workplace_list,
    )
    return project


def test_component_place_check_2(dummy_conveyor_project_with_child_component):
    """test_component_place_check_2."""
    dummy_conveyor_project_with_child_component.simulate(
        max_time=100,
    )

    component_wp1_list = []
    wp1 = dummy_conveyor_project_with_child_component.workplace_list[0]
    wp1_c_id_record = wp1.placed_component_id_record
    for c_id_record in wp1_c_id_record:
        component_wp1_list.extend(c_id_record)

    component_wp2_list = []
    wp2 = dummy_conveyor_project_with_child_component.workplace_list[1]
    wp2_c_id_record = wp2.placed_component_id_record
    for c_id_record in wp2_c_id_record:
        component_wp2_list.extend(c_id_record)

    component_wp3_list = []
    wp3 = dummy_conveyor_project_with_child_component.workplace_list[2]
    wp3_c_id_record = wp3.placed_component_id_record
    for c_id_record in wp3_c_id_record:
        component_wp3_list.extend(c_id_record)

    component_wp4_list = []
    wp4 = dummy_conveyor_project_with_child_component.workplace_list[3]
    wp4_c_id_record = wp4.placed_component_id_record
    for c_id_record in wp4_c_id_record:
        component_wp4_list.extend(c_id_record)

    # backward
    dummy_conveyor_project_with_child_component.backward_simulate(
        max_time=100,
    )


def test_subproject_task(dummy_project):
    """Test the subproject task."""
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
    sub2.append_input_task_dependency(sub1)
    project.workflow = BaseWorkflow()
    project.workflow.task_list = [sub1, sub2]
    project.simulate()
    project.write_simple_json(file_path[2])
    project2 = BaseProject()
    project2.read_simple_json(file_path[2])

    for file_p in file_path:
        if os.path.exists(file_p):
            os.remove(file_p)


def test_print_mermaid_diagram(dummy_project_multiple, dummy_conveyor_project):
    """test_print_mermaid_diagram."""
    dummy_project_multiple.print_mermaid_diagram(orientations="LR", subgraph=True)
    dummy_project_multiple.print_target_mermaid_diagram(
        target_product_list=[dummy_project_multiple.product_list[0]],
        target_workflow_list=[dummy_project_multiple.workflow_list[0]],
        target_team_list=[dummy_project_multiple.team_list[1]],
        orientations="TB",
        subgraph=False,
    )
    dummy_conveyor_project.print_mermaid_diagram()


def test_print_target_product_related_mermaid_diagram(dummy_project_multiple):
    """test_print_target_product_related_mermaid_diagram."""
    dummy_project_multiple.print_target_product_related_mermaid_diagram(
        target_product_list=[dummy_project_multiple.product_list[0]],
        orientations="TB",
        subgraph=False,
    )


def test_print_target_team_related_mermaid_diagram(dummy_project_multiple):
    """test_print_target_team_related_mermaid_diagram."""
    dummy_project_multiple.print_target_team_related_mermaid_diagram(
        target_team_list=[dummy_project_multiple.team_list[1]],
        orientations="TB",
        subgraph=False,
    )


def test_print_target_workplace_related_mermaid_diagram(dummy_project_multiple):
    """test_print_target_workplace_related_mermaid_diagram."""
    dummy_project_multiple.print_target_workplace_related_mermaid_diagram(
        target_workplace_list=[dummy_project_multiple.workplace_list[0]],
        orientations="TB",
        subgraph=False,
    )


def test_print_target_workflow_related_mermaid_diagram(dummy_project_multiple):
    """test_print_target_workflow_related_mermaid_diagram."""
    dummy_project_multiple.print_target_workflow_related_mermaid_diagram(
        target_workflow_list=[dummy_project_multiple.workflow_list[1]],
        orientations="TB",
        subgraph=False,
    )


def test_print_all_product_mermaid_diagram(dummy_project_multiple):
    """test_print_all_product_mermaid_diagram."""
    dummy_project_multiple.print_all_product_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_workflow_mermaid_diagram(dummy_project_multiple):
    """test_print_all_workflow_mermaid_diagram."""
    dummy_project_multiple.print_all_workflow_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_team_mermaid_diagram(dummy_project_multiple):
    """test_print_all_team_mermaid_diagram."""
    dummy_project_multiple.print_all_team_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_workplace_mermaid_diagram(dummy_project_multiple):
    """test_print_all_workplace_mermaid_diagram."""
    dummy_project_multiple.print_all_workplace_mermaid_diagram(
        orientations="TB",
        subgraph=True,
    )


def test_print_all_xxxx_gantt_mermaid_diagram(dummy_project_multiple):
    """test_print_all_workflow_gantt_mermaid_diagram."""
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_product_gantt_mermaid(range_time=(8, 11))
    dummy_project_multiple.print_all_workflow_gantt_mermaid(range_time=(8, 11))
    dummy_project_multiple.print_all_team_gantt_mermaid(range_time=(8, 11))
    dummy_project_multiple.print_all_workplace_gantt_mermaid(range_time=(8, 11))


def test_print_all_product_gantt_mermaid_diagram(dummy_project_multiple):
    """test_print_all_product_gantt_mermaid_diagram."""
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_product_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


def test_print_all_workflow_gantt_mermaid_diagram(dummy_project_multiple):
    """test_print_all_workflow_gantt_mermaid_diagram."""
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_workflow_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


def test_print_all_team_gantt_mermaid_diagram(dummy_project_multiple):
    """test_print_all_team_gantt_mermaid_diagram."""
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_team_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


def test_print_all_workplace_gantt_mermaid_diagram(dummy_project_multiple):
    """test_print_all_workplace_gantt_mermaid_diagram."""
    dummy_project_multiple.simulate(max_time=100)
    dummy_project_multiple.print_all_workplace_gantt_mermaid(
        range_time=(8, 11),
        detailed_info=True,
    )


@pytest.fixture(name="dummy_auto_task_project")
def fixture_dummy_auto_task_project():
    """dummy_auto_task_project."""
    task1 = BaseTask("task1", default_work_amount=2.0, auto_task=True)
    workflow = BaseWorkflow(task_list=[task1])

    component = BaseComponent("c")
    component.append_targeted_task(task1)
    product = BaseProduct(component_list=[component])

    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product_list=[product],
        workflow_list=[workflow],
    )
    return project


def test_auto_task(dummy_auto_task_project):
    """test_auto_task."""
    dummy_auto_task_project.simulate()
    assert (
        dummy_auto_task_project.workflow_list[0].task_list[0].state
        == BaseTaskState.FINISHED
    )
