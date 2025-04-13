# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_base_subproject."""

import datetime
import os


from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility

from pDESy.model.base_product import BaseProduct
from pDESy.model.base_project import BaseProject
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

    # BaseWorkplace
    workplace = BaseWorkplace("workplace", facility_list=[f1])
    workplace.extend_targeted_task_list([task1_1, task1_2, task2_1, task3])

    # BaseTeams
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
        unit_timedelta=datetime.timedelta(days=1),
        product=BaseProduct(component_list=[c3, c1, c2]),
        workflow=BaseWorkflow(task_list=[task1_1, task1_2, task2_1, task3, task0]),
        team_list=[team],
        workplace_list=[workplace],
        time=10,
        cost_list=[10],
    )
    project.initialize()
    return project


def test_set_all_attributes_from_json(dummy_project):
    """test_set_all_attributes_from_json."""
    # make subproject data
    sub_proj1_path = "sub_proj1.json"
    dummy_project.write_simple_json(sub_proj1_path)
    sub_proj1 = BaseSubProjectTask()

    absence_time_list = [0, 1, 2]
    dummy_project.simulate(absence_time_list=absence_time_list)
    dummy_project.write_simple_json(sub_proj1_path)
    sub_proj1 = BaseSubProjectTask()
    sub_proj1.set_all_attributes_from_json(sub_proj1_path)
    assert sub_proj1.default_work_amount == dummy_project.time - len(absence_time_list)
    assert sub_proj1.unit_timedelta == dummy_project.unit_timedelta

    if os.path.exists(sub_proj1_path):
        os.remove(sub_proj1_path)


def test_set_work_amount_progress_of_unit_step_time(dummy_project):
    sub_proj1_path = "sub_proj1.json"
    absence_time_list = [0, 1, 2]
    dummy_project.simulate(absence_time_list=absence_time_list)
    dummy_project.write_simple_json(sub_proj1_path)
    sub_proj1 = BaseSubProjectTask()
    sub_proj1.set_all_attributes_from_json(sub_proj1_path)
    sub_proj1.set_work_amount_progress_of_unit_step_time(datetime.timedelta(hours=1))
    assert sub_proj1.work_amount_progress_of_unit_step_time == 1 / 24

    if os.path.exists(sub_proj1_path):
        os.remove(sub_proj1_path)
