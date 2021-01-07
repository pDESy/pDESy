#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_project import BaseProject
from .component import Component
from .task import Task
from .worker import Worker
from .team import Team
from .product import Product
from .workflow import Workflow
from .organization import Organization
import json


class Project(BaseProject):
    """Project
    Project class for expressing target project
    including product, organization and workflow.
    This class is implemented from BaseProject.

    Args:
        file_path (str, optional):
            File path of this project data for reading.
            Defaults to None. (New Project)
        init_datetime (datetime.datetime, optional):
            Start datetime of project.
            Defaults to None -> datetime.datetime.now().
        unit_timedelta (datetime.timedelta, optional):
            Unit time of simulation.
            Defaults to None -> datetime.timedelta(minutes=1).
        product (BaseProduct, optional):
            BaseProduct in this project.
            Defaults to None. (New Project)
        organization (BaseOrganization, optional):
            BaseOrganization in this project.
            Defaults to None. (New Project)
        workflow (BaseWorkflow, optional):
            BaseWorkflow in this project.
            Defaults to None. (New Project)
        time (int, optional):
            Simulation time executing this method.
            Defaults to 0.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this project's cost in simulation.
            Defaults to None -> [].
        encoding (str, optional)
            encoding for reading json file.
            Default to None.
    """

    def __init__(
        self,
        file_path=None,
        # Basic parameters
        init_datetime=None,
        unit_timedelta=None,
        # Basic variables
        product=None,
        organization=None,
        workflow=None,
        time=0,
        cost_list=None,
        # For this class
        encoding=None,
    ):
        super().__init__(
            file_path=file_path,
            init_datetime=init_datetime,
            unit_timedelta=unit_timedelta,
            product=product,
            organization=organization,
            workflow=workflow,
            time=time,
            cost_list=cost_list,
        )
        if file_path is not None:
            self.read_pDES_json(file_path, encoding=encoding)

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of Project.

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        super().initialize(state_info=state_info, log_info=log_info)

    def simulate(
        self,
        task_performed_mode="multi-workers",
        error_tol=1e-10,
        print_debug=False,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
        max_time=10000,
    ):
        super().simulate(
            task_performed_mode=task_performed_mode,
            error_tol=error_tol,
            print_debug=print_debug,
            weekend_working=weekend_working,
            work_start_hour=work_start_hour,
            work_finish_hour=work_finish_hour,
            max_time=max_time,
        )

    def read_pDESy_web_json(self, file_path: str, encoding=None):
        """
        @override from BaseProject
        Add the code of reading advanced parameters.

        Args:
            file_path (str):
                file path by getting pDESy.org
            encoding ([type], optional):
                Defaults to None -> utf-8.
        TODO:
            pDESy.org for describing project in web browser should be developed...
        """
        encoding = encoding if encoding is not None else "utf-8"
        pdes_json = open(file_path, "r", encoding=encoding)
        data = json.load(pdes_json)

        # Get Product information including Components without dependency
        cd_list = list(filter(lambda node: node["type"] == "Component", data))
        component_list = [
            Component(
                cd["name"],
                ID=cd["id"],
                error_tolerance=float(cd["userData"]["errorTolerance"]),
            )
            for cd in cd_list
        ]

        # Get Workflow information including Tasks without dependency
        td_list = list(filter(lambda node: node["type"] == "Task", data))
        task_list = [
            Task(
                td["name"],
                ID=td["id"],
                default_work_amount=float(td["userData"]["workAmount"]),
                default_progress=float(td["userData"]["progress"]),
                additional_work_amount=float(td["userData"]["additionalWorkAmount"]),
            )
            for td in td_list
        ]

        # Get Organization information including Teams without dependency
        team_list = []
        ted_list = list(filter(lambda node: node["type"] == "Team", data))
        for team_data in ted_list:
            worker_list = []
            worker_list_data = team_data["userData"]["WorkerList"]
            if type(worker_list_data["Worker"]) is dict:
                worker_list_data["Worker"] = [worker_list_data["Worker"]]
            for worker_data in worker_list_data["Worker"]:
                work_amount_skill_mean_info = {}
                work_amount_skill_sd_info = {}
                quality_skill_mean_info = {}
                quality_skill_sd_info = {}
                if "WorkAmountSkill" in worker_data:
                    if type(worker_data["WorkAmountSkill"]) is list:
                        for skill_data in worker_data["WorkAmountSkill"]:
                            work_amount_skill_mean_info[skill_data["-name"]] = float(
                                skill_data["-value"]
                            )
                            work_amount_skill_sd_info[skill_data["-name"]] = float(
                                skill_data["-value_sd"]
                            )
                    elif type(worker_data["WorkAmountSkill"]) is dict:
                        work_amount_skill_mean_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value"])
                        work_amount_skill_sd_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
                if "QualitySkill" in worker_data:
                    if type(worker_data["QualitySkill"]) is list:
                        for skill_data in worker_data["QualitySkill"]:
                            quality_skill_mean_info[skill_data["-name"]] = float(
                                skill_data["-value"]
                            )
                            quality_skill_sd_info[skill_data["-name"]] = float(
                                skill_data["-value_sd"]
                            )
                    elif type(worker_data["QualitySkill"]) is dict:
                        quality_skill_mean_info[
                            worker_data["QualitySkill"]["-name"]
                        ] = float(worker_data["QualitySkill"]["-value"])
                        quality_skill_sd_info[
                            worker_data["QualitySkill"]["-name"]
                        ] = float(worker_data["QualitySkill"]["-value_sd"])
                worker_list.append(
                    Worker(
                        worker_data["Name"],
                        team_id=team_data["id"],
                        cost_per_time=float(worker_data["Cost"]),
                        workamount_skill_mean_map=work_amount_skill_mean_info,
                        workamount_skill_sd_map=work_amount_skill_sd_info,
                        quality_skill_mean_map=quality_skill_mean_info,
                    )
                )
            team_list.append(
                Team(team_data["name"], ID=team_data["id"], worker_list=worker_list)
            )

        # Get Links information including
        # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
        l_list = list(filter(lambda node: node["type"] == "draw2d.Connection", data))
        for link in l_list:
            org_id = link["source"]["node"]
            org_type = list(filter(lambda node: node["id"] == org_id, data))[0]["type"]
            dst_id = link["target"]["node"]
            dst_type = list(filter(lambda node: node["id"] == dst_id, data))[0]["type"]
            if org_type == "Component" and dst_type == "Component":
                org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
                dst_c = list(filter(lambda c: c.ID == dst_id, component_list))[0]
                org_c.parent_component_list.append(dst_c)
                dst_c.child_component_list.append(org_c)
            elif org_type == "Task" and dst_type == "Task":
                org_task = list(filter(lambda c: c.ID == org_id, task_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                # org_task.output_task_list.append(dst_task)
                dst_task.append_input_task(org_task)
            elif org_type == "Team" and dst_type == "Team":
                org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
                dst_team = list(filter(lambda c: c.ID == dst_id, team_list))[0]
                # org_task.output_task_id_list.append(dst_task.ID)
                dst_team.parent_team_id = org_team.ID
            elif org_type == "Component" and dst_type == "Task":
                org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_c.targeted_task_list.append(dst_task)
                dst_task.target_component = org_c
            elif org_type == "Team" and dst_type == "Task":
                org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_team.targeted_task_list.append(dst_task)
                dst_task.allocated_team_list.append(org_team)

        # Aggregate
        self.product = Product(component_list)
        self.workflow = Workflow(task_list)
        self.organization = Organization(team_list)

    def read_pDES_json(self, file_path: str, encoding=None):
        """
        @override from BaseProject
        Add the code of reading advanced parameters.

        Args:
            file_path (str):
                file path by getting pDES and converted to json
            encoding ([type], optional):
                Defaults to None -> utf-8.
        """
        encoding = encoding if encoding is not None else "utf-8"
        pdes_json = open(file_path, "r", encoding=encoding)
        data = json.load(pdes_json)

        # Get Product information including Components without dependency
        cd_list = data["ProjectDiagram"]["NodeElementList"]["ComponentNode"]
        component_list = [
            Component(
                cd["Name"], ID=cd["-id"], error_tolerance=float(cd["ErrorTolerance"])
            )
            for cd in cd_list
        ]

        # Get Workflow information including Tasks without dependency
        td_list = data["ProjectDiagram"]["NodeElementList"]["TaskNode"]
        task_list = [
            Task(
                td["Name"],
                ID=td["-id"],
                default_work_amount=float(td["WorkAmount"]),
                default_progress=float(td["Progress"]),
                additional_work_amount=float(td["AdditionalWorkAmount"]),
            )
            for td in td_list
        ]

        # Get Organization information including Teams without dependency
        team_list = []
        ted_list = data["ProjectDiagram"]["NodeElementList"]["TeamNode"]
        for team_data in ted_list:
            worker_list = []
            worker_list_data = team_data["WorkerList"]
            if type(worker_list_data["Worker"]) is dict:
                worker_list_data["Worker"] = [worker_list_data["Worker"]]
            for worker_data in worker_list_data["Worker"]:
                work_amount_skill_mean_info = {}
                work_amount_skill_sd_info = {}
                quality_skill_mean_info = {}
                quality_skill_sd_info = {}
                if "WorkAmountSkill" in worker_data:
                    if type(worker_data["WorkAmountSkill"]) is list:
                        for skill_data in worker_data["WorkAmountSkill"]:
                            work_amount_skill_mean_info[skill_data["-name"]] = float(
                                skill_data["-value"]
                            )
                            work_amount_skill_sd_info[skill_data["-name"]] = float(
                                skill_data["-value_sd"]
                            )
                    elif type(worker_data["WorkAmountSkill"]) is dict:
                        work_amount_skill_mean_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value"])
                        work_amount_skill_sd_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
                if "QualitySkill" in worker_data:
                    if type(worker_data["QualitySkill"]) is list:
                        for skill_data in worker_data["QualitySkill"]:
                            quality_skill_mean_info[skill_data["-name"]] = float(
                                skill_data["-value"]
                            )
                            quality_skill_sd_info[skill_data["-name"]] = float(
                                skill_data["-value_sd"]
                            )
                    elif type(worker_data["QualitySkill"]) is dict:
                        quality_skill_mean_info[
                            worker_data["QualitySkill"]["-name"]
                        ] = float(worker_data["QualitySkill"]["-value"])
                        quality_skill_sd_info[
                            worker_data["QualitySkill"]["-name"]
                        ] = float(worker_data["QualitySkill"]["-value_sd"])
                worker_list.append(
                    Worker(
                        worker_data["Name"],
                        team_id=team_data["-id"],
                        cost_per_time=float(worker_data["Cost"]),
                        workamount_skill_mean_map=work_amount_skill_mean_info,
                        workamount_skill_sd_map=work_amount_skill_sd_info,
                        quality_skill_mean_map=quality_skill_mean_info,
                    )
                )
            team_list.append(
                Team(team_data["Name"], ID=team_data["-id"], worker_list=worker_list)
            )
        self.organization = Organization(team_list)

        # Get Links information including
        # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
        l_list = data["ProjectDiagram"]["LinkList"]["Link"]
        for link in l_list:
            if link["-type"] == "ComponentLink":
                org_c = list(filter(lambda c: c.ID == link["-org"], component_list))[0]
                dst_c = list(filter(lambda c: c.ID == link["-dst"], component_list))[0]
                org_c.parent_component_list.append(dst_c)
                dst_c.child_component_list.append(org_c)
            elif link["-type"] == "TaskLink":
                org_task = list(filter(lambda c: c.ID == link["-org"], task_list))[0]
                dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
                # org_task.output_task_list.append(dst_task)
                dst_task.append_input_task(org_task)
            elif link["-type"] == "TeamLink":
                org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
                dst_team = list(filter(lambda c: c.ID == link["-dst"], team_list))[0]
                # org_task.output_task_id_list.append(dst_task.ID)
                dst_team.get_work_amount_skill_progress_team_id = org_team.ID
            elif link["-type"] == "TargetComponentLink":
                org_c = list(filter(lambda c: c.ID == link["-org"], component_list))[0]
                dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
                org_c.targeted_task_list.append(dst_task)
                dst_task.target_component = org_c
            elif link["-type"] == "AllocationLink":
                org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
                dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
                org_team.targeted_task_list.append(dst_task)
                dst_task.allocated_team_list.append(org_team)

        # Aggregate
        self.product = Product(component_list)
        self.workflow = Workflow(task_list)
        self.organization = Organization(team_list)
