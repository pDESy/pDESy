#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_base_project."""

import datetime
import os

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility
from pDESy.model.base_organization import BaseOrganization
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

import pytest


@pytest.fixture
def dummy_project(scope="function"):
    """dummy_project."""
    # BaseComponents in BaseProduct
    c3 = BaseComponent("c3")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3.extend_child_component_list([c1, c2])

    # BaseTasks in BaseWorkflow
    task1_1 = BaseTask("task1_1", need_facility=True)
    task1_2 = BaseTask("task1_2", worker_priority_rule=ResourcePriorityRuleMode.HSV)
    task2_1 = BaseTask("task2_1")
    task3 = BaseTask("task3", due_time=30)
    task3.extend_input_task_list([task1_2, task2_1])
    task1_2.append_input_task(task1_1)
    task0 = BaseTask("auto", auto_task=True, due_time=20)

    c1.extend_targeted_task_list([task1_1, task1_2])
    c2.append_targeted_task(task2_1)
    c3.append_targeted_task(task3)

    # Facilities in workplace
    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
    }

    # Workplace in BaseOrganization
    workplace = BaseWorkplace("workplace", facility_list=[f1])
    workplace.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

    # BaseTeams in BaseOrganization
    team = BaseTeam("team")
    team.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

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

    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(minutes=1),
        product=BaseProduct([c3, c1, c2]),
        workflow=BaseWorkflow([task1_1, task1_2, task2_1, task3, task0]),
        organization=BaseOrganization(team_list=[team], workplace_list=[workplace]),
        time=10,
        cost_list=[10],
    )
    project.initialize()
    # project.product = BaseProduct([c3, c1, c2])
    # project.workflow = BaseWorkflow([task1_1, task1_2, task2_1, task3])
    # project.organization = BaseOrganization(team_list=[team], workplace_list=[workplace])
    return project


@pytest.fixture
def dummy_project2(scope="function"):
    """dummy_project2."""
    # BaseComponents in BaseProduct
    c3 = BaseComponent("c3")
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3.extend_child_component_list([c1, c2])

    # BaseTasks in BaseWorkflow
    task1_1 = BaseTask("task1_1", need_facility=True)
    task1_2 = BaseTask("task1_2")
    task2_1 = BaseTask("task2_1")
    task3 = BaseTask("task3", due_time=30)
    task3.extend_input_task_list([task1_2, task2_1])
    task1_2.append_input_task(task1_1)
    task0 = BaseTask("auto", auto_task=True, due_time=20)

    c1.extend_targeted_task_list([task1_1, task1_2])
    c2.append_targeted_task(task2_1)
    c3.append_targeted_task(task3)

    # Facilities in workplace
    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
    }

    # Workplace in BaseOrganization
    workplace = BaseWorkplace("workplace", facility_list=[f1])
    workplace.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

    # BaseTeams in BaseOrganization
    team = BaseTeam("team")
    team.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

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
    w2.solo_working = True
    w2.workamount_skill_mean_map = {
        task1_1.name: 1.0,
        task1_2.name: 0.0,
        task2_1.name: 1.0,
        task3.name: 1.0,
    }
    w2.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w2)

    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct([c3, c1, c2]),
        workflow=BaseWorkflow([task1_1, task1_2, task2_1, task3, task0]),
        organization=BaseOrganization(team_list=[team], workplace_list=[workplace]),
        time=10,
        cost_list=[10],
    )
    project.initialize()
    # project.product = BaseProduct([c3, c1, c2])
    # project.workflow = BaseWorkflow([task1_1, task1_2, task2_1, task3])
    # project.organization = BaseOrganization(team_list=[team], workplace_list=[workplace])
    return project


@pytest.fixture
def dummy_place_check():
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
    # Workplace in BaseOrganization
    workplace = BaseWorkplace("workplace", facility_list=[f1, f2])
    workplace.extend_targeted_task_list([task1, task2, task3])

    # BaseTeams in BaseOrganization
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

    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct([c1, c2, c3]),
        workflow=BaseWorkflow([task1, task2, task3]),
        organization=BaseOrganization(team_list=[team], workplace_list=[workplace]),
    )

    return project


@pytest.fixture
def dummy_simple_project(scope="function"):
    c = BaseComponent("c", space_size=1.0)
    task1 = BaseTask("task1", default_work_amount=2.0)
    task2 = BaseTask("task2", default_work_amount=2.0)
    auto_task2 = BaseTask("auto_task2", auto_task=True, default_work_amount=2.0)
    task2.append_input_task(auto_task2)
    task3 = BaseTask("task3", default_work_amount=2.0)
    auto_task3 = BaseTask("auto_task3", auto_task=True, default_work_amount=4.0)
    task3.append_input_task(auto_task3)
    workflow = BaseWorkflow([task1, task2, task3, auto_task2, auto_task3])
    c.extend_targeted_task_list([task1, task2, task3])
    product = BaseProduct([c])

    # BaseTeams in BaseOrganization
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
        product=product,
        workflow=workflow,
        organization=BaseOrganization(team_list=[team]),
    )
    return project


def test_simple_project_simulate(dummy_simple_project):
    dummy_simple_project.simulate()

    # test for print_log
    dummy_simple_project.workflow.print_all_log_in_chronological_order()
    dummy_simple_project.product.print_all_log_in_chronological_order()
    dummy_simple_project.organization.print_all_log_in_chronological_order()
    dummy_simple_project.print_all_log_in_chronological_order()

    # test for print_log
    dummy_simple_project.workflow.print_all_log_in_chronological_order(backward=True)
    dummy_simple_project.product.print_all_log_in_chronological_order(backward=True)
    dummy_simple_project.organization.print_all_log_in_chronological_order(
        backward=True
    )
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
    dummy_place_check.organization.workplace_list[0].max_space_size = 1.5
    dummy_place_check.simulate(max_time=100)
    # workplace space size = 2
    dummy_place_check.organization.workplace_list[0].max_space_size = 2.0
    dummy_place_check.simulate(max_time=100)


def test_init(dummy_project):
    """test_init."""
    dummy_project.simulate(
        max_time=100,
        task_performed_mode="multi-workers",
    )
    dummy_project.create_gantt_plotly()


def test_initialize(dummy_project):
    """test_initialize."""
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


# def test_read_pDESy_web_json():
#     project = BaseProject(
#         init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
#         unit_timedelta=datetime.timedelta(days=1),
#     )
#     project.read_pDESy_web_json("tests/sample_from_pDESy_web.json")
#     project.simulate(
#         max_time=1000,
#         worker_performing_mode="single-task",
#         task_performed_mode="multi-workers",
#     )
#     project.create_gantt_plotly()


# def test_read_pDES_json():
#     project = BaseProject(
#         init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
#         unit_timedelta=datetime.timedelta(days=1),
#     )
#     project.read_pDES_json("tests/sample_converted_from_pDES_by_utilities-online.json")
#     project.simulate(
#         max_time=1000,
#         worker_performing_mode="single-task",
#         task_performed_mode="multi-workers",
#     )
#     project.create_gantt_plotly()


def test_str():
    """test_str."""
    print(BaseProject())


# def test_is_business_time():
#     """test_is_business_time."""
#     init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
#     timedelta = datetime.timedelta(days=1)
#     p = BaseProject(init_datetime=init_datetime, unit_timedelta=timedelta)

#     # 2020/4/1 8:00:00
#     assert p.is_business_time(init_datetime, weekend_working=True) is True
#     assert (
#         p.is_business_time(
#             init_datetime, weekend_working=True, work_start_hour=8, work_finish_hour=18
#         )
#         is True
#     )
#     assert (
#         p.is_business_time(
#             init_datetime, weekend_working=True, work_start_hour=9, work_finish_hour=18
#         )
#         is False
#     )

#     # 2020/4/1 8:00:00
#     assert p.is_business_time(init_datetime, weekend_working=False) is True
#     assert (
#         p.is_business_time(
#             init_datetime, weekend_working=False, work_start_hour=8, work_finish_hour=18
#         )
#         is True
#     )
#     assert (
#         p.is_business_time(
#             init_datetime, weekend_working=False, work_start_hour=9, work_finish_hour=18
#         )
#         is False
#     )

#     # 2020/4/4 8:00:00
#     saturday_datetime = datetime.datetime(2020, 4, 4, 8, 0, 0)
#     assert p.is_business_time(saturday_datetime, weekend_working=False) is False
#     assert (
#         p.is_business_time(
#             saturday_datetime,
#             weekend_working=False,
#             work_start_hour=8,
#             work_finish_hour=18,
#         )
#         is False
#     )
#     assert (
#         p.is_business_time(
#             saturday_datetime,
#             weekend_working=False,
#             work_start_hour=9,
#             work_finish_hour=18,
#         )
#         is False
#     )


def test_create_gantt_plotly(dummy_project, tmpdir):
    """test_create_gantt_plotly."""
    dummy_project.simulate(
        max_time=100,
        # weekend_working=False,
    )
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.create_gantt_plotly(save_fig_path=save_fig_path)


def test_get_networkx_graph(dummy_project):
    """test_get_networkx_graph."""
    dummy_project.get_networkx_graph(view_workers=True, view_facilities=True)
    # TODO
    # assert...


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
    # TODO
    # assert...


def test_draw_plotly_network(dummy_project, tmpdir):
    """test_draw_plotly_network."""
    for ext in ["png", "html", "json"]:
        save_fig_path = os.path.join(str(tmpdir), "test." + ext)
        dummy_project.draw_plotly_network(save_fig_path=save_fig_path)


def test_simulate(dummy_project, dummy_project2):
    """test_simulate."""
    dummy_project.simulate(
        max_time=100,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        # work_start_hour=7,
        # work_finish_hour=18,
    )

    # mode=?? -> Error
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=100,
            task_performed_mode="single-worker",
        )

    # mode=?? -> Error (not yet implemented)
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=100,
            task_performed_mode="multi-aaaaa",
        )

    # time is over max_time
    # with pytest.raises(Exception):
    #     dummy_project.simulate(
    #         max_time=10,
    #         task_performed_mode="multi-workers",
    #     )

    # dummy_project2
    dummy_project2.simulate(
        max_time=100,
        task_performed_mode="multi-workers",
        # work_start_hour=7,
        # work_finish_hour=18,
    )


def test_baskward_simulate(dummy_project):
    """test_baskward_simulate."""
    dummy_project.backward_simulate(
        max_time=100,
        task_performed_mode="multi-workers",
        # work_start_hour=7,
        # work_finish_hour=18,
    )

    dummy_project.backward_simulate(
        max_time=100,
        task_performed_mode="multi-workers",
        # work_start_hour=7,
        # work_finish_hour=18,
        considering_due_time_of_tail_tasks=True,
    )
    # assert dummy_project.workflow.task_list[0].ready_time_list == [4]
    # assert dummy_project.workflow.task_list[0].start_time_list == [5]
    # assert dummy_project.workflow.task_list[0].finish_time_list == [14]
    # assert dummy_project.workflow.task_list[1].ready_time_list == [14]
    # assert dummy_project.workflow.task_list[1].start_time_list == [15]
    # assert dummy_project.workflow.task_list[1].finish_time_list == [24]
    # assert dummy_project.workflow.task_list[2].ready_time_list == [4]
    # assert dummy_project.workflow.task_list[2].start_time_list == [15]
    # assert dummy_project.workflow.task_list[2].finish_time_list == [24]
    # assert dummy_project.workflow.task_list[3].ready_time_list == [24]
    # assert dummy_project.workflow.task_list[3].start_time_list == [25]
    # assert dummy_project.workflow.task_list[3].finish_time_list == [29]
    # assert dummy_project.workflow.task_list[4].ready_time_list == [4]
    # assert dummy_project.workflow.task_list[4].start_time_list == [10]
    # assert dummy_project.workflow.task_list[4].finish_time_list == [19]
    # assert dummy_project.workflow.task_list[5].ready_time_list == [19]
    # assert dummy_project.workflow.task_list[5].start_time_list == [20]
    # assert dummy_project.workflow.task_list[5].finish_time_list == [29]

    # assert dummy_project.organization.team_list[0].worker_list[0].start_time_list == [
    #     5,
    #     15,
    #     25,
    # ]
    # assert dummy_project.organization.team_list[0].worker_list[0].finish_time_list == [
    #     14,
    #     24,
    #     29,
    # ]
    # assert dummy_project.organization.team_list[0].worker_list[1].start_time_list == [
    #     15,
    #     25,
    # ]
    # assert dummy_project.organization.team_list[0].worker_list[1].finish_time_list == [
    #     24,
    #     29,
    # ]
    # assert dummy_project.organization.workplace_list[0].facility_list[
    #     0
    # ].start_time_list == [5]
    # assert dummy_project.organization.workplace_list[0].facility_list[
    #     0
    # ].finish_time_list == [14]


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


@pytest.fixture
def project_for_checking_space_judge(cope="function"):
    """project_for_checking_space_judge."""
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 4, 2, 8, 0, 0),
        unit_timedelta=datetime.timedelta(minutes=1),
    )
    # Components in Product
    a = BaseComponent("a")
    b = BaseComponent("b")

    # Register Product including Components in Project
    project.product = BaseProduct([a, b])

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
    project.workflow = BaseWorkflow([task_a, task_b])

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

    # define facilities belonging to wach workplace
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

    # Register Organization including Team in Project
    team_list = [team]
    workplace_list = [workplace1, workplace2]
    project.organization = BaseOrganization(team_list, workplace_list)

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
    task_list = project_for_checking_space_judge.workflow.task_list
    task_list[0].workplace_priority_rule = WorkplacePriorityRuleMode.FSS
    task_list[1].workplace_priority_rule = WorkplacePriorityRuleMode.FSS
    project_for_checking_space_judge.simulate(max_time=100)
    assert task_list[0].state_record_list[0] == task_list[1].state_record_list[0]
    task_list[0].workplace_priority_rule = WorkplacePriorityRuleMode.SSP
    task_list[1].workplace_priority_rule = WorkplacePriorityRuleMode.SSP
    project_for_checking_space_judge.simulate(max_time=100)
    assert task_list[0].state_record_list[0] != task_list[1].state_record_list[0]


@pytest.fixture
def dummy_conveyor_project():
    """dummy_conveyor_project."""
    c1 = BaseComponent("c1")
    c2 = BaseComponent("c2")
    c3 = BaseComponent("c3")
    taskA1 = BaseTask("A1", need_facility=True, default_work_amount=10)
    taskA2 = BaseTask("A2", need_facility=True, default_work_amount=3)
    taskA3 = BaseTask("A3", need_facility=True, default_work_amount=3)
    taskB1 = BaseTask("B1", need_facility=True, default_work_amount=3)
    taskB2 = BaseTask("B2", need_facility=True, default_work_amount=5)
    taskB3 = BaseTask("B3", need_facility=True, default_work_amount=3)

    c1.extend_targeted_task_list([taskA1, taskB1])
    c2.extend_targeted_task_list([taskA2, taskB2])
    c3.extend_targeted_task_list([taskA3, taskB3])

    taskB1.append_input_task(taskA1)
    taskB2.append_input_task(taskA2)
    taskB3.append_input_task(taskA3)

    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }

    f2 = BaseFacility("f2")
    f2.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }

    f3 = BaseFacility("f3")
    f3.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }
    f4 = BaseFacility("f4")
    f4.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }

    # Workplace in BaseOrganization
    wp1 = BaseWorkplace("workplace1", facility_list=[f1])
    wp1.extend_targeted_task_list([taskA1, taskA2, taskA3])
    wp2 = BaseWorkplace("workplace2", facility_list=[f2])
    wp2.extend_targeted_task_list([taskA1, taskA2, taskA3])
    wp3 = BaseWorkplace("workplace3", facility_list=[f3])
    wp3.extend_targeted_task_list([taskB1, taskB2, taskB3])
    wp4 = BaseWorkplace("workplace4", facility_list=[f4])
    wp4.extend_targeted_task_list([taskB1, taskB2, taskB3])

    wp3.append_input_workplace(wp1)
    wp4.append_input_workplace(wp2)

    # BaseTeams in BaseOrganization
    team = BaseTeam("team")
    team_list = [team]
    team.extend_targeted_task_list([taskA1, taskA2, taskA3, taskB1, taskB2, taskB3])

    # BaseWorkers in each BaseTeam
    w1 = BaseWorker("w1", team_id=team.ID)
    w1.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }
    w1.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w1)

    w2 = BaseWorker("w2", team_id=team.ID)
    w2.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }
    w2.facility_skill_map = {f2.name: 1.0}
    team.add_worker(w2)

    w3 = BaseWorker("w3", team_id=team.ID)
    w3.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }
    w3.facility_skill_map = {f3.name: 1.0}
    team.add_worker(w3)

    w4 = BaseWorker("w4", team_id=team.ID)
    w4.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }
    w4.facility_skill_map = {f4.name: 1.0}
    team.add_worker(w4)

    workplace_list = [wp1, wp2, wp3, wp4]
    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 7, 18, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct([c1, c2, c3]),
        workflow=BaseWorkflow([taskA1, taskA2, taskA3, taskB1, taskB2, taskB3]),
        organization=BaseOrganization(team_list, workplace_list),
    )
    return project


def test_component_place_check_1(dummy_conveyor_project):
    """test_component_place_check_1."""
    dummy_conveyor_project.simulate(
        max_time=100,
        # weekend_working=False,
    )

    component_wp1_list = []
    wp1 = dummy_conveyor_project.organization.workplace_list[0]
    wp1_c_id_record = wp1.placed_component_id_record
    for c_id_record in wp1_c_id_record:
        component_wp1_list.extend(c_id_record)

    component_wp2_list = []
    wp2 = dummy_conveyor_project.organization.workplace_list[1]
    wp2_c_id_record = wp2.placed_component_id_record
    for c_id_record in wp2_c_id_record:
        component_wp2_list.extend(c_id_record)

    component_wp3_list = []
    wp3 = dummy_conveyor_project.organization.workplace_list[2]
    wp3_c_id_record = wp3.placed_component_id_record
    for c_id_record in wp3_c_id_record:
        component_wp3_list.extend(c_id_record)

    component_wp4_list = []
    wp4 = dummy_conveyor_project.organization.workplace_list[3]
    wp4_c_id_record = wp4.placed_component_id_record
    for c_id_record in wp4_c_id_record:
        component_wp4_list.extend(c_id_record)

    assert set(component_wp1_list) == set(component_wp3_list)
    assert set(component_wp2_list) == set(component_wp4_list)


@pytest.fixture
def dummy_conveyor_project_with_child_component():
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

    taskA1 = BaseTask("A1", need_facility=True, default_work_amount=6)
    taskA2 = BaseTask("A2", need_facility=True, default_work_amount=2)
    taskA3 = BaseTask("A3", need_facility=True, default_work_amount=2)
    taskB1 = BaseTask("B1", need_facility=True, default_work_amount=2)
    taskB2 = BaseTask("B2", need_facility=True, default_work_amount=7)
    taskB3 = BaseTask("B3", need_facility=True, default_work_amount=2)

    c1_1.append_targeted_task(taskA1)
    c1_2.append_targeted_task(taskB1)
    c2_1.append_targeted_task(taskA2)
    c2_2.append_targeted_task(taskB2)
    c3_1.append_targeted_task(taskA3)
    c3_2.append_targeted_task(taskB3)

    taskB1.append_input_task(taskA1)
    taskB2.append_input_task(taskA2)
    taskB3.append_input_task(taskA3)

    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }

    f2 = BaseFacility("f2")
    f2.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }

    f3 = BaseFacility("f3")
    f3.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }
    f4 = BaseFacility("f4")
    f4.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }

    # Workplace in BaseOrganization
    wp1 = BaseWorkplace("workplace1", facility_list=[f1], max_space_size=1.0)
    wp1.extend_targeted_task_list([taskA1, taskA2, taskA3])
    wp2 = BaseWorkplace("workplace2", facility_list=[f2], max_space_size=2.0)
    wp2.extend_targeted_task_list([taskA1, taskA2, taskA3])
    wp3 = BaseWorkplace("workplace3", facility_list=[f3], max_space_size=4.0)
    wp3.extend_targeted_task_list([taskB1, taskB2, taskB3])
    wp4 = BaseWorkplace("workplace4", facility_list=[f4], max_space_size=4.0)
    wp4.extend_targeted_task_list([taskB1, taskB2, taskB3])

    wp3.append_input_workplace(wp1)
    wp4.append_input_workplace(wp2)

    # BaseTeams in BaseOrganization
    team = BaseTeam("team")
    team_list = [team]
    team.extend_targeted_task_list([taskA1, taskA2, taskA3, taskB1, taskB2, taskB3])

    # BaseWorkers in each BaseTeam
    w1 = BaseWorker("w1", team_id=team.ID)
    w1.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }
    w1.facility_skill_map = {f1.name: 1.0}
    team.add_worker(w1)

    w2 = BaseWorker("w2", team_id=team.ID)
    w2.workamount_skill_mean_map = {
        taskA1.name: 1.0,
        taskA2.name: 1.0,
        taskA3.name: 1.0,
    }
    w2.facility_skill_map = {f2.name: 1.0}
    team.add_worker(w2)

    w3 = BaseWorker("w3", team_id=team.ID)
    w3.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }
    w3.facility_skill_map = {f3.name: 1.0}
    team.add_worker(w3)

    w4 = BaseWorker("w4", team_id=team.ID)
    w4.workamount_skill_mean_map = {
        taskB1.name: 1.0,
        taskB2.name: 1.0,
        taskB3.name: 1.0,
    }
    w4.facility_skill_map = {f4.name: 1.0}
    team.add_worker(w4)

    workplace_list = [wp1, wp2, wp3, wp4]
    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2021, 8, 20, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct([c1_1, c1_2, c2_1, c2_2, c3_1, c3_2]),
        workflow=BaseWorkflow([taskA1, taskA2, taskA3, taskB1, taskB2, taskB3]),
        organization=BaseOrganization(team_list, workplace_list),
    )
    return project


def test_component_place_check_2(dummy_conveyor_project_with_child_component):
    """test_component_place_check_2."""
    dummy_conveyor_project_with_child_component.simulate(
        max_time=100,  # weekend_working=False
    )

    component_wp1_list = []
    wp1 = dummy_conveyor_project_with_child_component.organization.workplace_list[0]
    wp1_c_id_record = wp1.placed_component_id_record
    for c_id_record in wp1_c_id_record:
        component_wp1_list.extend(c_id_record)

    component_wp2_list = []
    wp2 = dummy_conveyor_project_with_child_component.organization.workplace_list[1]
    wp2_c_id_record = wp2.placed_component_id_record
    for c_id_record in wp2_c_id_record:
        component_wp2_list.extend(c_id_record)

    component_wp3_list = []
    wp3 = dummy_conveyor_project_with_child_component.organization.workplace_list[2]
    wp3_c_id_record = wp3.placed_component_id_record
    for c_id_record in wp3_c_id_record:
        component_wp3_list.extend(c_id_record)

    component_wp4_list = []
    wp4 = dummy_conveyor_project_with_child_component.organization.workplace_list[3]
    wp4_c_id_record = wp4.placed_component_id_record
    for c_id_record in wp4_c_id_record:
        component_wp4_list.extend(c_id_record)

    # TODO
    # assert set(component_wp1_list) <= set(component_wp3_list)
    # assert set(component_wp2_list) <= set(component_wp4_list)


def test_subproject_task(dummy_project):
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
    sub2.append_input_task(sub1)
    project.workflow = BaseWorkflow()
    project.workflow.task_list = [sub1, sub2]
    project.simulate()
    project.write_simple_json(file_path[2])
    project2 = BaseProject()
    project2.read_simple_json(file_path[2])

    for file_p in file_path:
        if os.path.exists(file_p):
            os.remove(file_p)
