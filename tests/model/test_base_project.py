#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from pDESy.model.base_project import BaseProject
import datetime
import os
from pDESy.model.base_component import BaseComponent
from pDESy.model.base_task import BaseTask
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_product import BaseProduct
from pDESy.model.base_workflow import BaseWorkflow
from pDESy.model.base_organization import BaseOrganization
from pDESy.model.base_factory import BaseFactory
from pDESy.model.base_facility import BaseFacility


@pytest.fixture
def dummy_project(scope="function"):
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

    # Facilities in factory
    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
    }
    # factory.facility_list.append(f1)

    # Factory in BaseOrganization
    factory = BaseFactory("factory", facility_list=[f1])
    factory.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

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
    team.worker_list.append(w1)

    w2 = BaseWorker("w2", team_id=team.ID, cost_per_time=6.0)
    w2.workamount_skill_mean_map = {
        task1_1.name: 1.0,
        task1_2.name: 0.0,
        task2_1.name: 1.0,
        task3.name: 1.0,
    }
    w2.facility_skill_map = {f1.name: 1.0}
    team.worker_list.append(w2)

    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct([c3, c1, c2]),
        workflow=BaseWorkflow([task1_1, task1_2, task2_1, task3, task0]),
        organization=BaseOrganization(team_list=[team], factory_list=[factory]),
        time=10,
        cost_list=[10],
    )
    project.initialize()
    # project.product = BaseProduct([c3, c1, c2])
    # project.workflow = BaseWorkflow([task1_1, task1_2, task2_1, task3])
    # project.organization = BaseOrganization(team_list=[team], factory_list=[factory])
    return project


@pytest.fixture
def dummy_project2(scope="function"):
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

    # Facilities in factory
    f1 = BaseFacility("f1")
    f1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
    }
    # factory.facility_list.append(f1)

    # Factory in BaseOrganization
    factory = BaseFactory("factory", facility_list=[f1])
    factory.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

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
    team.worker_list.append(w1)

    w2 = BaseWorker("w2", team_id=team.ID, cost_per_time=6.0)
    w2.solo_working = True
    w2.workamount_skill_mean_map = {
        task1_1.name: 1.0,
        task1_2.name: 0.0,
        task2_1.name: 1.0,
        task3.name: 1.0,
    }
    w2.facility_skill_map = {f1.name: 1.0}
    team.worker_list.append(w2)

    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct([c3, c1, c2]),
        workflow=BaseWorkflow([task1_1, task1_2, task2_1, task3, task0]),
        organization=BaseOrganization(team_list=[team], factory_list=[factory]),
        time=10,
        log_txt="aaa",
        cost_list=[10],
    )
    project.initialize()
    # project.product = BaseProduct([c3, c1, c2])
    # project.workflow = BaseWorkflow([task1_1, task1_2, task2_1, task3])
    # project.organization = BaseOrganization(team_list=[team], factory_list=[factory])
    return project


@pytest.fixture
def dummy_place_check():
    c3 = BaseComponent("c3", space_size=1.0)
    c1 = BaseComponent("c1", space_size=1.0)
    c2 = BaseComponent("c2", space_size=1.0)
    task1 = BaseTask("t1", need_facility=True)
    task2 = BaseTask("t2", need_facility=True)
    task3 = BaseTask("t3", need_facility=True)

    c1.append_targeted_task(task1)
    c2.append_targeted_task(task2)
    c3.append_targeted_task(task3)

    # Facilities in factory
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
    # Factory in BaseOrganization
    factory = BaseFactory("factory", facility_list=[f1, f2])
    factory.extend_targeted_task_list([task1, task2, task3])

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
    team.worker_list.append(w1)

    w2 = BaseWorker("w2", team_id=team.ID, cost_per_time=6.0)
    w2.workamount_skill_mean_map = {
        task1.name: 1.0,
        task2.name: 1.0,
        task3.name: 1.0,
    }
    w2.facility_skill_map = {f2.name: 1.0}
    team.worker_list.append(w2)

    # BaseProject including BaseProduct, BaseWorkflow and Organization
    project = BaseProject(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct([c1, c2, c3]),
        workflow=BaseWorkflow([task1, task2, task3]),
        organization=BaseOrganization(team_list=[team], factory_list=[factory]),
    )

    return project


def test_place_check(dummy_place_check):
    # factory space size = 1.5
    dummy_place_check.organization.factory_list[0].max_space_size = 1.5
    dummy_place_check.simulate(max_time=100)
    # factory space size = 2
    dummy_place_check.organization.factory_list[0].max_space_size = 2.0
    dummy_place_check.simulate(max_time=100)


def test_init(dummy_project):
    dummy_project.simulate(
        max_time=100,
        task_performed_mode="multi-workers",
    )
    dummy_project.create_gantt_plotly()


def test_initialize(dummy_project):
    dummy_project.simulate()
    dummy_project.initialize()
    assert dummy_project.time == 0
    assert dummy_project.cost_list == []


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
    print(BaseProject())


def test_is_business_time():
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    p = BaseProject(init_datetime=init_datetime, unit_timedelta=timedelta)

    # 2020/4/1 8:00:00
    assert p.is_business_time(init_datetime, weekend_working=True) is True
    assert (
        p.is_business_time(
            init_datetime, weekend_working=True, work_start_hour=8, work_finish_hour=18
        )
        is True
    )
    assert (
        p.is_business_time(
            init_datetime, weekend_working=True, work_start_hour=9, work_finish_hour=18
        )
        is False
    )

    # 2020/4/1 8:00:00
    assert p.is_business_time(init_datetime, weekend_working=False) is True
    assert (
        p.is_business_time(
            init_datetime, weekend_working=False, work_start_hour=8, work_finish_hour=18
        )
        is True
    )
    assert (
        p.is_business_time(
            init_datetime, weekend_working=False, work_start_hour=9, work_finish_hour=18
        )
        is False
    )

    # 2020/4/4 8:00:00
    saturday_datetime = datetime.datetime(2020, 4, 4, 8, 0, 0)
    assert p.is_business_time(saturday_datetime, weekend_working=False) is False
    assert (
        p.is_business_time(
            saturday_datetime,
            weekend_working=False,
            work_start_hour=8,
            work_finish_hour=18,
        )
        is False
    )
    assert (
        p.is_business_time(
            saturday_datetime,
            weekend_working=False,
            work_start_hour=9,
            work_finish_hour=18,
        )
        is False
    )


def test_create_gantt_plotly(dummy_project):
    dummy_project.simulate(
        max_time=100,
        weekend_working=False,
    )
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        dummy_project.create_gantt_plotly(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_get_networkx_graph(dummy_project):
    dummy_project.get_networkx_graph(view_workers=True, view_facilities=True)
    # TODO
    # assert...


def test_draw_networkx(dummy_project):
    for ext in ["png"]:
        save_fig_path = "test." + ext
        dummy_project.draw_networkx(
            save_fig_path=save_fig_path, view_workers=True, view_facilities=True
        )
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_get_node_and_edge_trace_for_plotly_network(dummy_project):
    dummy_project.get_node_and_edge_trace_for_plotly_network(
        view_workers=True, view_facilities=True
    )
    # TODO
    # assert...


def test_draw_plotly_network(dummy_project):
    for ext in ["png", "html", "json"]:
        save_fig_path = "test." + ext
        dummy_project.draw_plotly_network(save_fig_path=save_fig_path)
        if os.path.exists(save_fig_path):
            os.remove(save_fig_path)


def test_simulate(dummy_project, dummy_project2):
    dummy_project.simulate(
        max_time=100,
        work_start_hour=7,
        work_finish_hour=18,
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
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=10,
            task_performed_mode="multi-workers",
        )

    # dummy_project2
    dummy_project2.simulate(
        max_time=100,
        task_performed_mode="multi-workers",
        work_start_hour=7,
        work_finish_hour=18,
    )


def test_baskward_simulate(dummy_project):
    dummy_project.backward_simulate(
        max_time=100,
        task_performed_mode="multi-workers",
        work_start_hour=7,
        work_finish_hour=18,
    )

    dummy_project.backward_simulate(
        max_time=100,
        task_performed_mode="multi-workers",
        work_start_hour=7,
        work_finish_hour=18,
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
    # assert dummy_project.organization.factory_list[0].facility_list[
    #     0
    # ].start_time_list == [5]
    # assert dummy_project.organization.factory_list[0].facility_list[
    #     0
    # ].finish_time_list == [14]


def test_output_simlog(dummy_project):
    dummy_project.simulate(
        max_time=100,
        task_performed_mode="multi-workers",
        work_start_hour=7,
        work_finish_hour=18,
    )
    dummy_project.output_simlog("test.txt")
    if os.path.exists("test.txt"):
        os.remove("test.txt")


def test_simple_write_json(dummy_project):

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
