#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from pDESy.model.project import Project
import datetime
import os
from pDESy.model.component import Component
from pDESy.model.task import Task
from pDESy.model.team import Team
from pDESy.model.worker import Worker
from pDESy.model.product import Product
from pDESy.model.workflow import Workflow
from pDESy.model.organization import Organization
from pDESy.model.base_factory import BaseFactory
from pDESy.model.base_facility import BaseFacility


@pytest.fixture
def dummy_project(scope="function"):
    # Components in Product
    c3 = Component("c3")
    c1 = Component("c1")
    c2 = Component("c2")
    c3.extend_child_component_list([c1, c2])

    # Tasks in Workflow
    task1_1 = Task("task1_1", need_facility=True)
    task1_2 = Task("task1_2")
    task2_1 = Task("task2_1")
    task3 = Task("task3")
    task3.extend_input_task_list([task1_2, task2_1])
    task1_2.append_input_task(task1_1)

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

    # Teams in Organization
    team = Team("team")
    team.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

    # Workers in each Team
    w1 = Worker("w1", team_id=team.ID, cost_per_time=10.0)
    w1.workamount_skill_mean_map = {
        task1_1.name: 1.0,
        task1_2.name: 1.0,
        task2_1.name: 0.0,
        task3.name: 1.0,
    }
    w1.facility_skill_map = {f1.name: 1.0}
    team.worker_list.append(w1)

    w2 = Worker("w2", team_id=team.ID, cost_per_time=6.0)
    w2.workamount_skill_mean_map = {
        task1_1.name: 1.0,
        task1_2.name: 0.0,
        task2_1.name: 1.0,
        task3.name: 1.0,
    }
    w2.facility_skill_map = {f1.name: 1.0}
    team.worker_list.append(w2)

    # Project including Product, Workflow and Organization
    project = Project(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
    )
    project.product = Product([c3, c1, c2])
    project.workflow = Workflow([task1_1, task1_2, task2_1, task3])
    project.organization = Organization(team_list=[team], factory_list=[factory])
    return project


def test_init():
    project = Project(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
        file_path="tests/sample_converted_from_pDES_by_utilities-online.json",
    )
    project.simulate(
        max_time=1000,
        worker_performing_mode="single-task",
        task_performed_mode="multi-workers",
    )
    project.create_gantt_plotly()


def test_initialize(dummy_project):
    dummy_project.simulate()
    dummy_project.initialize()
    assert dummy_project.time == 0
    assert dummy_project.cost_list == []


def test_read_pDESy_web_json():
    project = Project(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
    )
    project.read_pDESy_web_json("tests/sample_from_pDESy_web.json")
    project.simulate(
        max_time=1000,
        worker_performing_mode="single-task",
        task_performed_mode="multi-workers",
    )
    project.create_gantt_plotly()


def test_read_pDES_json():
    project = Project(
        init_datetime=datetime.datetime(2020, 4, 1, 8, 0, 0),
        unit_timedelta=datetime.timedelta(days=1),
    )
    project.read_pDES_json("tests/sample_converted_from_pDES_by_utilities-online.json")
    project.simulate(
        max_time=1000,
        worker_performing_mode="single-task",
        task_performed_mode="multi-workers",
    )
    project.create_gantt_plotly()


def test_str():
    print(Project())


def test_is_business_time():
    init_datetime = datetime.datetime(2020, 4, 1, 8, 0, 0)
    timedelta = datetime.timedelta(days=1)
    p = Project(init_datetime=init_datetime, unit_timedelta=timedelta)

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
        max_time=1000,
        worker_performing_mode="single-task",
        task_performed_mode="single-worker",
        print_debug=True,
        weekend_working=False,
    )
    dummy_project.create_gantt_plotly(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_networkx_graph(dummy_project):
    dummy_project.get_networkx_graph()
    # TODO
    # assert...


def test_draw_networkx(dummy_project):
    dummy_project.draw_networkx(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_get_node_and_edge_trace_for_ploty_network(dummy_project):
    dummy_project.get_node_and_edge_trace_for_ploty_network()
    # TODO
    # assert...


def test_draw_plotly_network(dummy_project):
    dummy_project.draw_plotly_network(save_fig_path="test.png")
    if os.path.exists("test.png"):
        os.remove("test.png")


def test_simulate(dummy_project):
    dummy_project.simulate(
        max_time=100,
        worker_performing_mode="single-task",
        task_performed_mode="multi-workers",
        work_start_hour=7,
        work_finish_hour=18,
        print_debug=True,
    )

    # mode=3 -> Error (not yet implemented)
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=100,
            worker_performing_mode="multi-task",
            task_performed_mode="single-worker",
            print_debug=True,
        )

    # mode=4 -> Error (not yet implemented)
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=100,
            worker_performing_mode="multi-task",
            task_performed_mode="multi-workers",
            print_debug=True,
        )

    # mode=?? -> Error
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=100,
            worker_performing_mode="xxxx",
            task_performed_mode="multi-workers",
            print_debug=True,
        )

    # mode=?? -> Error (not yet implemented)
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=100,
            worker_performing_mode="multi-task",
            task_performed_mode="xxx-workers",
            print_debug=True,
        )

    # time is over max_time
    with pytest.raises(Exception):
        dummy_project.simulate(
            max_time=10,
            worker_performing_mode="single-task",
            task_performed_mode="multi-workers",
            print_debug=True,
        )


def test___perform_and_update_TaskPerformedBySingleTaskWorker():
    # this method is tested in other test code..
    pass


def test___is_allocated():
    # this method is tested in other test code..
    pass


def test___perform_and_update_TaskPerformedBySingleTaskWorkers():
    # this method is tested in other test code..
    pass
