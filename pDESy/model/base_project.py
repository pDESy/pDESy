#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_project."""

import datetime
import itertools
import json
import sys
from typing import Optional
import uuid
import warnings
from abc import ABCMeta
from enum import IntEnum

from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt

import networkx as nx

import plotly.figure_factory as ff
import plotly.graph_objects as go

from .base_component import BaseComponent, BaseComponentState
from .base_facility import BaseFacility, BaseFacilityState
from .base_priority_rule import (
    TaskPriorityRuleMode,
    sort_worker_list,
    sort_facility_list,
    sort_task_list,
    sort_workplace_list,
)
from .base_product import BaseProduct
from .base_task import BaseTask, BaseTaskDependency, BaseTaskState
from .base_team import BaseTeam
from .base_worker import BaseWorker, BaseWorkerState
from .base_workflow import BaseWorkflow
from .base_workplace import BaseWorkplace


class SimulationMode(IntEnum):
    """SimulationMode."""

    NONE = 0
    FORWARD = 1
    BACKWARD = -1


class BaseProjectStatus(IntEnum):
    """BaseProjectStatus."""

    NONE = 0
    FINISHED_SUCCESS = 1
    FINISHED_FAILURE = -1


class BaseProject(object, metaclass=ABCMeta):
    """BaseProject.

    BaseProject class for expressing target project
    including product, workflow, team_set and workplace_set.
    This class will be used as template.
    """

    def __init__(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        init_datetime: datetime.datetime = None,
        unit_timedelta: datetime.timedelta = None,
        absence_time_list: list[int] = None,
        perform_auto_task_while_absence_time: bool = None,
        # Basic variables
        product_set: set[BaseProduct] = None,
        workflow_set: set[BaseWorkflow] = None,
        team_set: set[BaseTeam] = None,
        workplace_set: set[BaseWorkplace] = None,
        time: int = 0,
        cost_record_list: list[float] = None,
        simulation_mode: SimulationMode = None,
        status: BaseProjectStatus = None,
    ):
        """
        Initializes a BaseProject instance.

        Args:
            name (str, optional): Name of this project. Defaults to "Project".
            ID (str, optional): Project ID. Defaults to a generated UUID.
            init_datetime (datetime.datetime, optional): Start datetime. Defaults to now.
            unit_timedelta (datetime.timedelta, optional): Simulation unit time. Defaults to 1 minute.
            absence_time_list (List[int], optional): List of absence times. Defaults to [].
            perform_auto_task_while_absence_time (bool, optional): Whether to perform auto tasks during absence. Defaults to False.
            product_set (set[BaseProduct], optional): Set of products. Defaults to set().
            workflow_set (set[BaseWorkflow], optional): Set of workflows. Defaults to set().
            team_set (set[BaseTeam], optional): Set of teams. Defaults to set().
            workplace_set (set[BaseWorkplace], optional): Set of workplaces. Defaults to set().
            time (int, optional): Simulation time. Defaults to 0.
            cost_record_list (List[float], optional): Cost history. Defaults to [].
            simulation_mode (SimulationMode, optional): Simulation mode. Defaults to SimulationMode.NONE.
            status (BaseProjectStatus, optional): Project status. Defaults to BaseProjectStatus.NONE.
        """
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "Project"
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.init_datetime = (
            init_datetime if init_datetime is not None else datetime.datetime.now()
        )
        self.unit_timedelta = (
            unit_timedelta
            if unit_timedelta is not None
            else datetime.timedelta(minutes=1)
        )
        if absence_time_list is not None:
            self.absence_time_list = absence_time_list
        else:
            self.absence_time_list = []

        if perform_auto_task_while_absence_time is not None:
            self.perform_auto_task_while_absence_time = (
                perform_auto_task_while_absence_time
            )
        else:
            self.perform_auto_task_while_absence_time = False

        # Changeable variable on simulation
        # --
        # Basic variables
        self.product_set = product_set if product_set is not None else set()
        self.workflow_set = workflow_set if workflow_set is not None else set()
        self.team_set = team_set if team_set is not None else set()
        self.workplace_set = workplace_set if workplace_set is not None else set()

        if time != int(0):
            self.time = time
        else:
            self.time = int(0)

        if cost_record_list is not None:
            self.cost_record_list = cost_record_list
        else:
            self.cost_record_list = []

        if simulation_mode is not None:
            self.simulation_mode = simulation_mode
        else:
            self.simulation_mode = SimulationMode.NONE

        if status is not None:
            self.status = status
        else:
            self.status = BaseProjectStatus.NONE

        self.__initialize_child_instance_set_id_instance_dict()

    def __initialize_child_instance_set_id_instance_dict(self):
        self.component_set = self.get_all_component_set()
        self.task_set = self.get_all_task_set()
        self.worker_set = self.get_all_worker_set()
        self.facility_set = self.get_all_facility_set()

        self.product_dict = {p.ID: p for p in self.product_set}
        self.workflow_dict = {w.ID: w for w in self.workflow_set}
        self.team_dict = {team.ID: team for team in self.team_set}
        self.workplace_dict = {wp.ID: wp for wp in self.workplace_set}
        self.component_dict = {c.ID: c for c in self.component_set}
        self.task_dict = {t.ID: t for t in self.task_set}
        self.worker_dict = {w.ID: w for w in self.worker_set}
        self.facility_dict = {f.ID: f for f in self.facility_set}

    def __str__(self):
        """
        Returns a string representation of the project.

        Returns:
            str: Time and name lists of product, workflow, team, and workplace.
        """
        return (
            f"TIME: {self.time}\n"
            f"PRODUCT\n{self.product_set}\n\n"
            f"Workflow\n{self.workflow_set}\n\n"
            f"TEAM\n{self.team_set}\n\n"
            f"WORKPLACE\n{self.workplace_set}"
        )

    def append_product(self, product: BaseProduct):
        """
        Append product to this project.

        Args:
            product (BaseProduct): Product to append.

        Raises:
            TypeError: If product is not an instance of BaseProduct.
            DeprecationWarning: This method is deprecated. Use add_product instead.
        """
        warnings.warn(
            "append_product is deprecated. Use add_product instead.",
            DeprecationWarning,
        )
        if not isinstance(product, BaseProduct):
            raise TypeError("product should be BaseProduct")
        self.product_set.add(product)

    def extend_product_list(self, product_set: list[BaseProduct]):
        """
        Extend product list to this project.

        Args:
            product_set (set[BaseProduct]): List of products to extend.

        Raises:
            TypeError: If any item in product_set is not a BaseProduct.
            DeprecationWarning: This method is deprecated. Use update_product_set instead.
        """
        warnings.warn(
            "extend_product_set is deprecated. Use update_product_set instead.",
            DeprecationWarning,
        )
        if not all(isinstance(product, BaseProduct) for product in product_set):
            raise TypeError("All items in product_set should be BaseProduct")
        self.product_set.extend(product_set)

    def append_workflow(self, workflow: BaseWorkflow):
        """
        Append workflow to this project.

        Args:
            workflow (BaseWorkflow): Workflow to append.

        Raises:
            TypeError: If workflow is not an instance of BaseWorkflow.
            DeprecationWarning: This method is deprecated. Use add_workflow instead.
        """
        warnings.warn(
            "append_workflow is deprecated. Use add_workflow instead.",
            DeprecationWarning,
        )
        if not isinstance(workflow, BaseWorkflow):
            raise TypeError("workflow should be BaseWorkflow")
        self.workflow_set.add(workflow)

    def extend_workflow_list(self, workflow_set: list[BaseWorkflow]):
        """
        Extend workflow list to this project.

        Args:
            workflow_set (list[BaseWorkflow]): List of workflows to extend.

        Raises:
            TypeError: If any item in workflow_set is not a BaseWorkflow.
            DeprecationWarning: This method is deprecated. Use update_workflow_set instead.
        """
        warnings.warn(
            "extend_workflow_list is deprecated. Use update_workflow_set instead.",
            DeprecationWarning,
        )
        if not all(isinstance(workflow, BaseWorkflow) for workflow in workflow_set):
            raise TypeError("All items in workflow_set should be BaseWorkflow")
        self.workflow_set.update(workflow_set)

    def append_team(self, team: BaseTeam):
        """
        Append team to this project.

        Args:
            team (BaseTeam): Team to append.

        Raises:
            TypeError: If team is not an instance of BaseTeam.
            DeprecationWarning: This method is deprecated. Use add_team instead.
        """
        warnings.warn(
            "append_team is deprecated. Use add_team instead.",
            DeprecationWarning,
        )
        if not isinstance(team, BaseTeam):
            raise TypeError("team should be BaseTeam")
        self.team_set.add(team)

    def extend_team_list(self, team_set: list[BaseTeam]):
        """
        Extend team list to this project.

        Args:
            team_set (list[BaseTeam]): List of teams to extend.

        Raises:
            TypeError: If any item in team_set is not a BaseTeam.
            DeprecationWarning: This method is deprecated. Use update_team_set instead.
        """
        warnings.warn(
            "extend_team_set is deprecated. Use update_team_set instead.",
            DeprecationWarning,
        )
        if not all(isinstance(team, BaseTeam) for team in team_set):
            raise TypeError("All items in team_set should be BaseTeam")
        self.team_set.update(team_set)

    def append_workplace(self, workplace: BaseWorkplace):
        """
        Append workplace to this project.

        Args:
            workplace (BaseWorkplace): Workplace to append.

        Raises:
            TypeError: If workplace is not an instance of BaseWorkplace.
            DeprecationWarning: This method is deprecated. Use add_workplace instead.
        """
        warnings.warn(
            "append_workplace is deprecated. Use add_workplace instead.",
            DeprecationWarning,
        )
        if not isinstance(workplace, BaseWorkplace):
            raise TypeError("workplace should be BaseWorkplace")
        self.workplace_set.add(workplace)

    def extend_workplace_list(self, workplace_set: list[BaseWorkplace]):
        """
        Extend workplace list to this project.

        Args:
            workplace_set (list[BaseWorkplace]): List of workplaces to extend.

        Raises:
            TypeError: If any item in workplace_set is not a BaseWorkplace.
            DeprecationWarning: This method is deprecated. Use update_workplace_set instead.
        """
        warnings.warn(
            "extend_workplace_set is deprecated. Use update_workplace_set instead.",
            DeprecationWarning,
        )
        if not all(isinstance(workplace, BaseWorkplace) for workplace in workplace_set):
            raise TypeError("All items in workplace_set should be BaseWorkplace")
        self.workplace_set.update(workplace_set)

    def create_product(
        self, name: str = None, ID: str = None, component_set: set[BaseComponent] = None
    ):
        """
        Create a new product and add it to the project.

        Args:
            name (str, optional): Name of the product.
            ID (str, optional): ID of the product.
            component_set (set[BaseComponent], optional): Set of components to include in the product.

        Returns:
            BaseProduct: The created product.
        """
        product = BaseProduct(name=name, ID=ID, component_set=component_set)
        self.add_product(product)
        return product

    def add_product(self, product: BaseProduct):
        """
        Add product to this project.

        Args:
            product (BaseProduct): Product to add.

        Raises:
            TypeError: If product is not an instance of BaseProduct.
        """
        if not isinstance(product, BaseProduct):
            raise TypeError("product should be BaseProduct")
        self.product_set.add(product)

    def update_product_set(self, product_set: set[BaseProduct]):
        """
        Update product set to this project.

        Args:
            product_set (set[BaseProduct]): Set of products to update.

        Raises:
            TypeError: If any item in product_set is not a BaseProduct.
        """
        if not all(isinstance(product, BaseProduct) for product in product_set):
            raise TypeError("All items in product_set should be BaseProduct")
        self.product_set.update(product_set)

    def create_workflow(
        self,
        name: str = None,
        ID: str = None,
        task_set: set[BaseTask] = None,
        # Basic variables
        critical_path_length: float = 0.0,
    ):
        """
        Create a new workflow and add it to the project.

        Args:
            name (str, optional): Name of this workflow. Defaults to None -> "Workflow".
            ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
            task_set (set[BaseTask], optional): List of BaseTask in this BaseWorkflow. Default to None -> set().
            critical_path_length (float, optional): Critical path length of PERT/CPM. Defaults to 0.0.

        Returns:
            BaseWorkflow: The created workflow.
        """
        workflow = BaseWorkflow(
            name=name,
            ID=ID,
            task_set=task_set,
            critical_path_length=critical_path_length,
        )
        self.add_workflow(workflow)
        return workflow

    def add_workflow(self, workflow: BaseWorkflow):
        """
        Add workflow to this project.

        Args:
            workflow (BaseWorkflow): Workflow to add.

        Raises:
            TypeError: If workflow is not an instance of BaseWorkflow.
        """
        if not isinstance(workflow, BaseWorkflow):
            raise TypeError("workflow should be BaseWorkflow")
        self.workflow_set.add(workflow)

    def update_workflow_set(self, workflow_set: set[BaseWorkflow]):
        """
        Update workflow set to this project.

        Args:
            workflow_set (set[BaseWorkflow]): Set of workflows to update.

        Raises:
            TypeError: If any item in workflow_set is not a BaseWorkflow.
        """
        if not all(isinstance(workflow, BaseWorkflow) for workflow in workflow_set):
            raise TypeError("All items in workflow_set should be BaseWorkflow")
        self.workflow_set.update(workflow_set)

    def create_team(
        self,
        name: str = None,
        ID: str = None,
        worker_set: set[BaseWorker] = None,
        targeted_task_id_set: set[str] = None,
        parent_team_id: str = None,
        cost_record_list: list[float] = None,
    ):
        """
        Create a new team and add it to the project.

        Args:
            name (str, optional): Name of this team. Defaults to None -> "New Team".
            ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
            worker_set (set[BaseWorker], optional): Set of BaseWorkers who belong to this team. Defaults to None -> set().
            targeted_task_id_set (set[str], optional): Targeted BaseTasks id set. Defaults to None -> set().
            parent_team_id (str, optional): Parent team id of this team. Defaults to None.
            cost_record_list (List[float], optional): History or record of this team's cost in simulation. Defaults to None -> [].

        Returns:
            BaseTeam: The created team.
        """
        team = BaseTeam(
            name=name,
            ID=ID,
            worker_set=worker_set,
            targeted_task_id_set=targeted_task_id_set,
            parent_team_id=parent_team_id,
            cost_record_list=cost_record_list,
        )
        self.add_team(team)
        return team

    def add_team(self, team: BaseTeam):
        """
        Add team to this project.

        Args:
            team (BaseTeam): Team to add.

        Raises:
            TypeError: If team is not an instance of BaseTeam.
        """
        if not isinstance(team, BaseTeam):
            raise TypeError("team should be BaseTeam")
        self.team_set.add(team)

    def update_team_set(self, team_set: set[BaseTeam]):
        """
        Update team set to this project.

        Args:
            team_set (set[BaseTeam]): Set of teams to update.

        Raises:
            TypeError: If any item in team_set is not a BaseTeam.
        """
        if not all(isinstance(team, BaseTeam) for team in team_set):
            raise TypeError("All items in team_set should be BaseTeam")
        self.team_set.update(team_set)

    def create_workplace(
        self,
        name: str = None,
        ID: str = None,
        facility_set: set[BaseFacility] = None,
        targeted_task_id_set: set[str] = None,
        parent_workplace_id: str = None,
        max_space_size: float = None,
        input_workplace_id_set: set[str] = None,
        # Basic variables
        available_space_size: float = None,
        cost_record_list: list[float] = None,
        placed_component_id_set: set[str] = None,
        placed_component_id_set_record_list: list[list[str]] = None,
    ):
        """
        Create a new workplace and add it to the project.

        Args:
            name (str, optional): Name of this workplace. Defaults to None -> "New Workplace".
            ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
            facility_set (set[BaseFacility], optional): List of BaseFacility who belong to this workplace. Defaults to None -> set().
            targeted_task_id_set (set[str], optional): Targeted BaseTasks id set. Defaults to None -> set().
            parent_workplace_id (str, optional): Parent workplace id of this workplace. Defaults to None.
            max_space_size (float, optional): Max size of space for placing components. Default to None -> 1.0.
            input_workplace_id_set (set[str], optional): Input BaseWorkplace id set. Defaults to None -> set().
            available_space_size (float, optional): Available space size in this workplace. Defaults to None -> max_space_size.
            placed_component_id_set (set[str], optional): Components id which places to this workplace in simulation. Defaults to None -> set().
            placed_component_id_set_record_list (List[List[str]], optional): Record of placed components ID in simulation. Defaults to None -> [].
            cost_record_list (List[float], optional): History or record of this workplace's cost in simulation. Defaults to None -> [].

        Returns:
            BaseWorkplace: The created workplace.
        """
        workplace = BaseWorkplace(
            name=name,
            ID=ID,
            facility_set=facility_set,
            targeted_task_id_set=targeted_task_id_set,
            parent_workplace_id=parent_workplace_id,
            max_space_size=max_space_size,
            input_workplace_id_set=input_workplace_id_set,
            available_space_size=available_space_size,
            placed_component_id_set=placed_component_id_set,
            placed_component_id_set_record_list=placed_component_id_set_record_list,
            cost_record_list=cost_record_list,
        )
        self.add_workplace(workplace)
        return workplace

    def add_workplace(self, workplace: BaseWorkplace):
        """
        Add workplace to this project.

        Args:
            workplace (BaseWorkplace): Workplace to add.

        Raises:
            TypeError: If workplace is not an instance of BaseWorkplace.
        """
        if not isinstance(workplace, BaseWorkplace):
            raise TypeError("workplace should be BaseWorkplace")
        self.workplace_set.add(workplace)

    def update_workplace_set(self, workplace_set: set[BaseWorkplace]):
        """
        Update workplace set to this project.

        Args:
            workplace_set (set[BaseWorkplace]): Set of workplaces to update.

        Raises:
            TypeError: If any item in workplace_set is not a BaseWorkplace.
        """
        if not all(isinstance(workplace, BaseWorkplace) for workplace in workplace_set):
            raise TypeError("All items in workplace_set should be BaseWorkplace")
        self.workplace_set.update(workplace_set)

    def initialize(self, state_info: bool = True, log_info: bool = True):
        """
        Initialize the changeable variables of BaseProject.

        This method resets the simulation state and/or log information for the project and all its elements
        (products, workflows, teams, workplaces). If `log_info` is True, time, cost records, simulation mode,
        and status are reset. If `state_info` is True, state information of all elements is initialized.

        Args:
            state_info (bool, optional): Whether to initialize state information of the project and its elements.
                Defaults to True.
            log_info (bool, optional): Whether to initialize log information (time, cost, mode, status).
                Defaults to True.
        """

        if log_info:
            self.time = 0
            self.cost_record_list = []
            self.simulation_mode = SimulationMode.NONE
            self.status = BaseProjectStatus.NONE

        self.__initialize_child_instance_set_id_instance_dict()

        # product should be initialized after initializing workflow
        for workflow in self.workflow_set:
            workflow.initialize(state_info=state_info, log_info=log_info)
            self.check_state_workflow(workflow, BaseTaskState.READY)
        for product in self.product_set:
            product.initialize(state_info=state_info, log_info=log_info)
            for component in product.component_set:
                self.check_state_component(component)
        for team in self.team_set:
            team.initialize(state_info=state_info, log_info=log_info)
        for workplace in self.workplace_set:
            workplace.initialize(state_info=state_info, log_info=log_info)

    def check_state_component(self, component: BaseComponent):
        """
        Check and update the state of a component based on its targeted tasks.

        Args:
            component (BaseComponent): The component whose state will be checked and updated.
        """
        targeted_task_set = self.get_target_task_set(component.targeted_task_id_set)

        any_ready = False
        all_finished = True
        all_working = True
        for t in targeted_task_set:
            if t.state == BaseTaskState.WORKING:
                component.state = BaseComponentState.WORKING
                return
            if t.state is not BaseTaskState.FINISHED:
                all_finished = False
            if t.state is not BaseTaskState.WORKING:
                all_working = False
            if t.state is BaseTaskState.READY:
                any_ready = True

        if all_finished:
            component.state = BaseComponentState.FINISHED
        elif (not all_working) and (not all_finished) and any_ready:
            component.state = BaseComponentState.READY

    def simulate(
        self,
        task_priority_rule: TaskPriorityRuleMode = TaskPriorityRuleMode.TSLACK,
        error_tol: float = 1e-10,
        work_amount_limit_per_unit_time: float = 1e10,
        count_auto_task_in_work_amount_limit: bool = False,
        absence_time_list: list[int] | None = None,
        perform_auto_task_while_absence_time: bool = False,
        initialize_state_info: bool = True,
        initialize_log_info: bool = True,
        max_time: int = 10000,
        unit_time: int = 1,
        progress_bar: bool = False,
    ):
        """
        Simulate this BaseProject.

        Args:
            task_priority_rule (TaskPriorityRule, optional):
                Task priority rule for simulation. Defaults to TaskPriorityRule.TSLACK.
            error_tol (float, optional):
                Measures against numerical error. Defaults to 1e-10.
            work_amount_limit_per_unit_time (float, optional):
                Upper limit on the total remaining work amount that can be in the
                WORKING state at any given time. When this limit is reached,
                additional tasks that would otherwise transition from READY to
                WORKING remain in the READY state until enough work is completed
                (i.e., the total remaining work of WORKING tasks falls below the
                limit). Defaults to 1e10.
            count_auto_task_in_work_amount_limit (bool, optional):
                Whether auto tasks should be counted toward the work amount limit.
                Defaults to False.
            absence_time_list (List[int], optional):
                List of absence times in simulation. Defaults to None (workers work every time).
            perform_auto_task_while_absence_time (bool, optional):
                Whether to perform auto tasks during absence time. Defaults to False.
            initialize_state_info (bool, optional):
                Whether to initialize state info of this project. Defaults to True.
            initialize_log_info (bool, optional):
                Whether to initialize log info of this project. Defaults to True.
            max_time (int, optional):
                Maximum simulation time. Defaults to 10000.
            unit_time (int, optional):
                Unit time of simulation. Defaults to 1.
            progress_bar (bool, optional):
                Whether to show progress bar during simulation. Defaults to False.
        """
        if absence_time_list is None:
            absence_time_list = []

        self.initialize(state_info=initialize_state_info, log_info=initialize_log_info)

        self.simulation_mode = SimulationMode.FORWARD

        self.absence_time_list = absence_time_list

        self.perform_auto_task_while_absence_time = perform_auto_task_while_absence_time

        pbar = (
            tqdm(total=max_time, desc="Simulating", unit="time")
            if progress_bar
            else None
        )

        try:
            while True:
                # 0. Update status
                self.__update()

                # 1. Check finished or not
                state_list = set(map(lambda task: task.state, self.task_set))
                if all(state == BaseTaskState.FINISHED for state in state_list):
                    self.status = BaseProjectStatus.FINISHED_SUCCESS
                    if pbar is not None:
                        pbar.n = self.time
                        pbar.refresh()
                        pbar.set_description("Completed")
                    return

                # Time over check
                if self.time >= max_time:
                    self.status = BaseProjectStatus.FINISHED_FAILURE
                    warnings.warn(
                        "Time Over! Please check your simulation model or increase max_time value"
                    )
                    if pbar is not None:
                        pbar.n = self.time
                        pbar.refresh()
                        pbar.set_description("Time Over")
                    return

                # check now is business time or not
                working = True

                if self.time in absence_time_list:
                    working = False

                # check and update state of each worker and facility
                if working:
                    for team in self.team_set:
                        team.check_update_state_from_absence_time_list(self.time)
                    for workplace in self.workplace_set:
                        workplace.check_update_state_from_absence_time_list(self.time)
                else:
                    for team in self.team_set:
                        team.set_absence_state_to_all_workers()
                    for workplace in self.workplace_set:
                        workplace.set_absence_state_to_all_facilities()

                # 2. Allocate free workers to READY tasks
                if working:
                    self.__allocate(
                        task_priority_rule=task_priority_rule,
                    )

                # Update state of task newly allocated workers and facilities (READY -> WORKING)
                # Calculate total work amount once before processing all workflows
                total_work_amount_in_working_tasks = sum(
                    task.remaining_work_amount
                    for task in self.task_set
                    if task.state == BaseTaskState.WORKING
                    and (
                        count_auto_task_in_work_amount_limit
                        or not task.auto_task
                    )
                )
                for workflow in self.workflow_set:
                    total_work_amount_in_working_tasks = self.check_state_workflow(
                        workflow,
                        BaseTaskState.WORKING,
                        work_amount_limit_per_unit_time,
                        total_work_amount_in_working_tasks,
                        count_auto_task_in_work_amount_limit,
                    )
                for product in self.product_set:
                    # product should be checked after checking workflow state
                    for component in product.component_set:
                        self.check_state_component(component)

                # 3. Pay cost to all workers and facilities in this time
                cost_this_time = 0.0

                add_zero_to_all_workers = False
                add_zero_to_all_facilities = False
                if not working:
                    add_zero_to_all_workers = True
                    add_zero_to_all_facilities = True

                for team in self.team_set:
                    cost_this_time += team.add_labor_cost(
                        only_working=True,
                        add_zero_to_all_workers=add_zero_to_all_workers,
                    )
                for workplace in self.workplace_set:
                    cost_this_time += workplace.add_labor_cost(
                        only_working=True,
                        add_zero_to_all_facilities=add_zero_to_all_facilities,
                    )
                self.cost_record_list.append(cost_this_time)

                # 4, Perform
                if working:
                    self.__perform(only_auto_task=False)
                elif perform_auto_task_while_absence_time:
                    self.__perform(only_auto_task=True)

                # 5. Record
                self.__record(working=working)

                # 6. Update time
                self.time = self.time + unit_time

                if pbar is not None:
                    pbar.update(unit_time)

        finally:
            if pbar is not None:
                pbar.close()

    def backward_simulate(
        self,
        task_priority_rule: TaskPriorityRuleMode = TaskPriorityRuleMode.TSLACK,
        error_tol: float = 1e-10,
        work_amount_limit_per_unit_time: float = 1e10,
        count_auto_task_in_work_amount_limit: bool = False,
        absence_time_list: list[int] | None = None,
        perform_auto_task_while_absence_time: bool = False,
        initialize_state_info: bool = True,
        initialize_log_info: bool = True,
        max_time: int = 10000,
        unit_time: int = 1,
        progress_bar: bool = False,
        considering_due_time_of_tail_tasks: bool = False,
        reverse_log_information: bool = True,
    ):
        """
        Simulate this BaseProject using backward simulation.

        Args:
            task_priority_rule (TaskPriorityRuleMode, optional):
                Task priority rule for simulation. Defaults to TaskPriorityRuleMode.TSLACK.
            error_tol (float, optional):
                Measures against numerical error. Defaults to 1e-10.
            work_amount_limit_per_unit_time (float, optional):
                Upper limit on the total remaining work amount that can be in the
                WORKING state at any given time. When this limit is reached,
                additional tasks that would otherwise transition from READY to
                WORKING remain in the READY state until enough work is completed
                (i.e., the total remaining work of WORKING tasks falls below the
                limit). Defaults to 1e10.
            count_auto_task_in_work_amount_limit (bool, optional):
                Whether auto tasks should be counted toward the work amount limit.
                Defaults to False.
            absence_time_list (list[int], optional):
                List of absence times in simulation. Defaults to None (workers work every time).
            perform_auto_task_while_absence_time (bool, optional):
                Whether to perform auto tasks during absence time. Defaults to False.
            initialize_state_info (bool, optional):
                Whether to initialize state info of this project. Defaults to True.
            initialize_log_info (bool, optional):
                Whether to initialize log info of this project. Defaults to True.
            max_time (int, optional):
                Maximum simulation time. Defaults to 10000.
            unit_time (int, optional):
                Unit time of simulation. Defaults to 1.
            progress_bar (bool, optional):
                Whether to show progress bar during simulation. Defaults to False.
            considering_due_time_of_tail_tasks (bool, optional):
                Whether to consider due time of tail tasks. Defaults to False.
            reverse_log_information (bool, optional):
                Whether to reverse simulation log information after simulation. Defaults to True.

        Note:
            This function is experimental and mainly for research use.
            It may not be suitable for simulations considering rework.
        """
        if absence_time_list is None:
            absence_time_list = []

        for workflow in self.workflow_set:
            workflow.reverse_dependencies()

        # reverse_dependency of workplace
        for workplace in self.workplace_set:
            workplace.original_input_workplace_id_set = getattr(
                workplace, "input_workplace_id_set", set()
            )
            workplace.original_output_workplace_id_set = getattr(
                workplace, "output_workplace_id_set", set()
            )
            tmp_input = getattr(workplace, "input_workplace_id_set", set())
            setattr(workplace, "output_workplace_id_set", tmp_input)
            tmp_input = getattr(workplace, "input_workplace_id_set", set())
            setattr(workplace, "input_workplace_id_set", set())

        auto_task_removing_after_simulation = set()
        try:
            if considering_due_time_of_tail_tasks:
                # Add dummy task for considering the difference of due_time
                for workflow in self.workflow_set:
                    tail_task_set = set(
                        filter(
                            lambda task: len(task.input_task_id_dependency_set) == 0,
                            workflow.task_set,
                        )
                    )
                    max_due_time = max({task.due_time for task in tail_task_set})
                    for tail_task in tail_task_set:
                        if tail_task.due_time < max_due_time:
                            auto_task = BaseTask(
                                "auto",
                                auto_task=True,
                                default_work_amount=max_due_time - tail_task.due_time,
                            )
                            tail_task.add_input_task(
                                auto_task, task_dependency_mode=BaseTaskDependency.FS
                            )
                            auto_task_removing_after_simulation.add(auto_task)
                            workflow.task_set.add(auto_task)

            self.simulate(
                task_priority_rule=task_priority_rule,
                error_tol=error_tol,
                work_amount_limit_per_unit_time=work_amount_limit_per_unit_time,
                count_auto_task_in_work_amount_limit=count_auto_task_in_work_amount_limit,
                absence_time_list=absence_time_list,
                perform_auto_task_while_absence_time=perform_auto_task_while_absence_time,
                initialize_log_info=initialize_log_info,
                initialize_state_info=initialize_state_info,
                max_time=max_time,
                unit_time=unit_time,
                progress_bar=progress_bar,
            )

        finally:
            self.simulation_mode = SimulationMode.BACKWARD
            for auto_task in auto_task_removing_after_simulation:
                auto_task_output_task_set = [
                    (task, dependency)
                    for task in self.task_set
                    for input_task_id, dependency in task.input_task_id_dependency_set
                    if input_task_id == auto_task.ID
                ]
                for task, dependency in auto_task_output_task_set:
                    task.input_task_id_dependency_set.remove((auto_task.ID, dependency))
                for workflow in self.workflow_set:
                    if auto_task in workflow.task_set:
                        workflow.task_set.remove(auto_task)
            if reverse_log_information:
                self.reverse_log_information()

            for workflow in self.workflow_set:
                workflow.reverse_dependencies()

            # reverse_dependency of workplace
            for workplace in self.workplace_set:
                setattr(
                    workplace,
                    "input_workplace_id_set",
                    getattr(workplace, "original_input_workplace_id_set", set()),
                )
                setattr(
                    workplace,
                    "output_workplace_id_set",
                    getattr(workplace, "original_output_workplace_id_set", set()),
                )
                if hasattr(workplace, "original_input_workplace_id_set"):
                    del workplace.original_input_workplace_id_set
                if hasattr(workplace, "original_output_workplace_id_set"):
                    del workplace.original_output_workplace_id_set

    def reverse_log_information(self):
        """
        Reverse the log information for the project and all its elements.

        This method reverses the order of cost records, absence time list, and calls
        reverse_log_information for all products, workflows, teams, and workplaces.
        It is mainly used after backward simulation to align log information with forward time order.
        """
        self.cost_record_list.reverse()
        total_step_length = len(self.cost_record_list)
        self.absence_time_list = sorted(
            list(
                filter(
                    lambda abs_time: abs_time >= 0,
                    map(
                        lambda abs_time: total_step_length - abs_time - 1,
                        self.absence_time_list,
                    ),
                )
            )
        )
        for product in self.product_set:
            product.reverse_log_information()
        for workflow in self.workflow_set:
            workflow.reverse_log_information()
        for team in self.team_set:
            team.reverse_log_information()
        for workplace in self.workplace_set:
            workplace.reverse_log_information()

    def __perform(
        self,
        only_auto_task: bool = False,
        seed=None,
        increase_component_error: float = 1.0,
    ):
        for workflow in self.workflow_set:

            for task in workflow.task_set:
                if only_auto_task:
                    if task.auto_task:
                        self.__perform_task(task, seed=seed)
                else:
                    self.__perform_task(
                        task,
                        seed=seed,
                        increase_component_error=increase_component_error,
                    )

    def __perform_task(
        self, task: BaseTask, seed=None, increase_component_error: float = 1.0
    ):
        if task.state == BaseTaskState.WORKING:
            work_amount_progress = 0.0
            no_error_probability = 1.0
            if task.auto_task:
                work_amount_progress = task.work_amount_progress_of_unit_step_time
            else:
                if task.need_facility:
                    for (
                        worker_id,
                        facility_id,
                    ) in task.allocated_worker_facility_id_tuple_set:
                        worker = self.worker_dict.get(worker_id, None)
                        w_progress = self.get_work_amount_skill_progress(
                            worker, task.name, seed=seed
                        )
                        facility = self.facility_dict.get(facility_id, None)
                        f_progress = self.get_work_amount_skill_progress(
                            facility, task.name, seed=seed
                        )
                        work_amount_progress += w_progress * f_progress
                        no_error_probability = (
                            no_error_probability
                            - worker.get_quality_skill_point(task.name, seed=seed)
                        )
                else:
                    for worker_id, _ in task.allocated_worker_facility_id_tuple_set:
                        worker = self.worker_dict.get(worker_id, None)
                        work_amount_progress = (
                            work_amount_progress
                            + self.get_work_amount_skill_progress(
                                worker, task.name, seed=seed
                            )
                        )
                        no_error_probability = (
                            no_error_probability
                            - worker.get_quality_skill_point(task.name, seed=seed)
                        )

            task.remaining_work_amount = (
                task.remaining_work_amount - work_amount_progress
            )

            if task.target_component_id is not None:
                target_component = self.component_dict.get(
                    task.target_component_id, None
                )
                target_component.update_error_value(
                    no_error_probability, increase_component_error, seed=seed
                )

    def get_work_amount_skill_progress(self, resource, task_name: str, seed=None):
        """
        Get the progress of work amount contributed by a resource for a task in this time step.

        If the resource (worker or facility) is assigned to multiple tasks at the same time,
        the progress `p_r(t)` is calculated as:

            p_r(t) = ps_r(t) / N_r(t)

        where:
            - ps_r(t): Progress if the resource has only this task at this time.
            - N_r(t): Number of tasks assigned to the resource at this time.

        Args:
            resource (BaseWorker or BaseFacility): The resource whose skill progress is calculated.
            task_name (str): Name of the task.
            seed (int, optional): Random seed for reproducibility. Defaults to None.

        Returns:
            float: Progress of work amount contributed by the resource in this time step.
        """
        if seed is not None:
            np.random.seed(seed=seed)
        if not resource.has_workamount_skill(task_name):
            return 0.0
        if resource.state == BaseWorkerState.ABSENCE:
            return 0.0
        skill_mean = resource.workamount_skill_mean_map[task_name]
        if task_name not in resource.workamount_skill_sd_map:
            skill_sd = 0
        else:
            skill_sd = resource.workamount_skill_sd_map[task_name]
        base_progress = np.random.normal(skill_mean, skill_sd)
        assigned_task_id_set = set()
        if isinstance(resource, BaseWorker):
            assigned_task_id_set = {
                t[0] for t in resource.assigned_task_facility_id_tuple_set
            }
        elif isinstance(resource, BaseFacility):
            assigned_task_id_set = {
                t[0] for t in resource.assigned_task_worker_id_tuple_set
            }
        sum_of_working_task_in_this_time = sum(
            (
                self.task_dict.get(task_id, None) is not None
                and (
                    self.task_dict[task_id].state == BaseTaskState.WORKING
                    or self.task_dict[task_id].state
                    == BaseTaskState.WORKING_ADDITIONALLY
                )
            )
            for task_id in assigned_task_id_set
        )
        return base_progress / float(sum_of_working_task_in_this_time)

    def __record(self, working: bool = True):
        for workflow in self.workflow_set:
            workflow.record(working)
        for team in self.team_set:
            team.record_assigned_task_id()
            team.record_all_worker_state(working=working)
        for workplace in self.workplace_set:
            workplace.record_assigned_task_id()
            workplace.record_placed_component_id()
            workplace.record_all_facility_state(working=working)
        for product in self.product_set:
            product.record(working)

    def __update(self):
        for workflow in self.workflow_set:
            self.check_state_workflow(workflow, BaseTaskState.FINISHED)
        for product in self.product_set:
            # product should be checked after checking workflow state
            for component in product.component_set:
                self.check_state_component(component)
        self.__check_removing_placed_workplace()
        for workflow in self.workflow_set:
            self.check_state_workflow(workflow, BaseTaskState.READY)
        for product in self.product_set:
            # product should be checked after checking workflow state
            for component in product.component_set:
                self.check_state_component(component)
        for workflow in self.workflow_set:
            workflow.update_pert_data(self.time)

    def __check_removing_placed_workplace(self):
        """
        Check removing this product from placed_workplace or not.
        If all tasks of this product is finished, this product will be removed automatically.
        """

        all_children_components_id = set()
        for c in self.component_set:
            all_children_components_id.update(c.child_component_id_set)

        top_component_set = [
            component
            for component in self.component_set
            if component.ID not in all_children_components_id
        ]

        removing_placed_workplace_component_set = set()
        for c in top_component_set:
            targeted_task_set = self.get_target_task_set(c.targeted_task_id_set)
            all_finished_flag = all(
                task.state == BaseTaskState.FINISHED for task in targeted_task_set
            )
            if all_finished_flag and c.placed_workplace_id is not None:
                removing_placed_workplace_component_set.add(c)

        for c in removing_placed_workplace_component_set:
            placed_workplace = self.workplace_dict.get(c.placed_workplace_id, None)
            self.remove_component_on_workplace(c, placed_workplace)
            self.set_component_on_workplace(c, None)

    def __is_allocated_worker(self, worker: BaseWorker, task: BaseTask):
        team = self.team_dict.get(worker.team_id, None)
        if team is None:
            return False
        targeted_task_set = self.get_target_task_set(team.targeted_task_id_set)
        return task in targeted_task_set

    def __iter_workplace_and_ancestors(self, workplace: BaseWorkplace):
        cur = workplace
        visited = set()
        while cur is not None and cur.ID not in visited:
            visited.add(cur.ID)
            yield cur
            if cur.parent_workplace_id is None:
                break
            cur = self.workplace_dict.get(cur.parent_workplace_id, None)

    def __allocate(
        self,
        task_priority_rule: TaskPriorityRuleMode = TaskPriorityRuleMode.TSLACK,
    ):

        # 1. Get ready task and free workers and facilities
        ready_and_working_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.READY
                or task.state == BaseTaskState.WORKING,
                self.task_set,
            )
        )

        worker_list = list(
            itertools.chain.from_iterable(
                list(map(lambda team: team.worker_set, self.team_set))
            )
        )

        free_worker_list = list(
            filter(lambda worker: worker.state == BaseWorkerState.FREE, worker_list)
        )

        # 2. Sort ready task using TaskPriorityRule
        ready_and_working_task_list = sort_task_list(
            ready_and_working_task_list, task_priority_rule
        )

        # 3. Allocate ready tasks to free workers and facilities
        target_workplace_id_set = {wp.ID for wp in self.workplace_set}

        for task in ready_and_working_task_list:
            if task.target_component_id is not None:
                # 3-1. Set target component of workplace if target component is ready
                component = self.component_dict.get(task.target_component_id, None)
                if self.is_ready_component(component):
                    candidate_workplace_set = [
                        workplace
                        for workplace in self.workplace_set
                        if workplace.ID in task.allocated_workplace_id_set
                    ]
                    candidate_workplace_set = sort_workplace_list(
                        candidate_workplace_set,
                        task.workplace_priority_rule,
                        name=task.name,
                    )
                    for workplace in candidate_workplace_set:
                        if workplace.ID in target_workplace_id_set:
                            conveyor_condition = True
                            if len(workplace.input_workplace_id_set) > 0:
                                if component.placed_workplace_id is None:
                                    conveyor_condition = True
                                elif not (
                                    component.placed_workplace_id
                                    in [
                                        workplace_id
                                        for workplace_id in workplace.input_workplace_id_set
                                    ]
                                ):
                                    conveyor_condition = False

                            skill_flag = (
                                workplace.get_total_workamount_skill(task.name) > 1e-10
                            )
                            if task.auto_task:
                                # Auto task can be performed even if there is no skill
                                skill_flag = True

                            if (
                                conveyor_condition
                                and self.can_put_component_to_workplace(
                                    workplace, component
                                )
                                and skill_flag
                            ):
                                # 3-1-1. move ready_component
                                pre_workplace = self.workplace_dict.get(
                                    component.placed_workplace_id, None
                                )

                                # 3-1-1-1. remove
                                if pre_workplace is None:
                                    for child_c_id in component.child_component_id_set:
                                        child_c = self.component_dict.get(
                                            child_c_id, None
                                        )
                                        wp = self.workplace_dict.get(
                                            child_c.placed_workplace_id, None
                                        )
                                        if wp is not None:
                                            for c_wp_id in wp.placed_component_id_set:
                                                c_wp = self.component_dict.get(
                                                    c_wp_id, None
                                                )
                                                if any(
                                                    child_id == task.target_component_id
                                                    for child_id in c_wp.child_component_id_set
                                                ):
                                                    self.remove_component_on_workplace(
                                                        c_wp, wp
                                                    )

                                elif pre_workplace is not None:
                                    self.remove_component_on_workplace(
                                        component, pre_workplace
                                    )

                                self.set_component_on_workplace(component, None)

                                # 3-1-1-2. register
                                self.set_component_on_workplace(component, workplace)
                                break

            if not task.auto_task:
                # 3-2. Allocate ready tasks to free workers and facilities

                if task.need_facility:
                    # Search candidate facilities from the list of placed_workplace
                    target_component = self.component_dict.get(
                        task.target_component_id, None
                    )
                    placed_workplace = self.workplace_dict.get(
                        target_component.placed_workplace_id, None
                    )

                    if placed_workplace is not None:
                        # Facility candidate set
                        candidate_facility_set = set()
                        for wp in self.__iter_workplace_and_ancestors(placed_workplace):
                            candidate_facility_set.update(wp.facility_set)
                        free_facility_list = [
                            f for f in candidate_facility_set if f.state == BaseFacilityState.FREE
                        ]

                        # Facility sorting
                        free_facility_list = sort_facility_list(
                            free_facility_list, task.facility_priority_rule
                        )

                        # Extract only candidate facilities
                        allocating_facilities = [
                            f for f in free_facility_list if f.has_workamount_skill(task.name)
                        ]

                        for facility in allocating_facilities:
                            # Extract only candidate workers
                            allocating_workers = list(
                                filter(
                                    lambda worker, task=task, facility=facility: (
                                        worker.has_workamount_skill(task.name)
                                        and self.__is_allocated_worker(worker, task)
                                        and self.can_add_resources_to_task(
                                            task, worker=worker, facility=facility
                                        )
                                    ),
                                    free_worker_list,
                                )
                            )

                            # Sort workers
                            allocating_workers = sort_worker_list(
                                allocating_workers,
                                task.worker_priority_rule,
                                name=task.name,
                                workplace_id=placed_workplace.ID,
                            )

                            # Allocate
                            for worker in allocating_workers:
                                task.add_alloc_pair((worker.ID, facility.ID))
                                worker.add_assigned_pair((task.ID, facility.ID))
                                facility.add_assigned_pair((task.ID, worker.ID))
                                allocating_workers.remove(worker)
                                free_worker_list = [
                                    w for w in free_worker_list if w.ID != worker.ID
                                ]
                                break

                else:
                    # Worker sorting
                    free_worker_list = sort_worker_list(
                        free_worker_list, task.worker_priority_rule, name=task.name
                    )

                    # Extract only candidate workers
                    allocating_workers = list(
                        filter(
                            lambda worker, task=task: worker.has_workamount_skill(
                                task.name
                            )
                            and self.__is_allocated_worker(worker, task),
                            free_worker_list,
                        )
                    )

                    # Allocate free workers to tasks
                    for worker in allocating_workers:
                        if self.can_add_resources_to_task(task, worker=worker):
                            task.add_alloc_pair((worker.ID, None))
                            worker.add_assigned_pair((task.ID, None))
                            free_worker_list = [
                                w for w in free_worker_list if w.ID != worker.ID
                            ]

    def check_state_workflow(
        self,
        workflow: BaseWorkflow,
        state: BaseTaskState,
        work_amount_limit_per_unit_time: float = 1e10,
        total_work_amount_in_working_tasks: float = None,
        count_auto_task_in_work_amount_limit: bool = False,
    ):
        """
        Check and update the state of all tasks in the given workflow for the specified state.

        Args:
            workflow (BaseWorkflow): The workflow whose tasks' states will be checked and updated.
            state (BaseTaskState): The target state to check (READY, WORKING, or FINISHED).
                Only tasks that can transition to this state will be updated.
            work_amount_limit_per_unit_time (float, optional):
                Maximum total work amount that can be newly started per simulation time unit
                across all workflows. This limit is applied only when transitioning tasks
                into the WORKING state via this method. If the sum of work amounts of
                eligible tasks that would start working exceeds this limit, only a subset
                up to the limit is allowed to transition to WORKING; the remaining eligible
                tasks stay in their current state and are reconsidered in subsequent calls.
                Defaults to 1e10 (effectively no limit).
            total_work_amount_in_working_tasks (float, optional):
                Current total work amount in WORKING tasks. Used when state is WORKING to
                enforce the limit across multiple workflows. If None, it will be calculated.
                Defaults to None.
            count_auto_task_in_work_amount_limit (bool, optional):
                Whether auto tasks should be counted toward the work amount limit.
                Defaults to False.
        
        Returns:
            float: Updated total work amount in WORKING tasks when state is WORKING, otherwise None.
        """
        if state == BaseTaskState.READY:
            self.__check_ready_workflow(workflow)
            return None
        elif state == BaseTaskState.WORKING:
            return self.__check_working_workflow(
                workflow,
                work_amount_limit_per_unit_time=work_amount_limit_per_unit_time,
                total_work_amount_in_working_tasks=total_work_amount_in_working_tasks,
                count_auto_task_in_work_amount_limit=count_auto_task_in_work_amount_limit,
            )
        elif state == BaseTaskState.FINISHED:
            self.__check_finished_workflow(workflow)
            return None

    def __check_ready_workflow(self, workflow: BaseWorkflow):
        NONE = BaseTaskState.NONE
        READY = BaseTaskState.READY
        WORKING = BaseTaskState.WORKING
        FINISHED = BaseTaskState.FINISHED

        task_dict = self.task_dict

        max_iter = len(workflow.task_set)
        for _ in range(max_iter):
            changed = False

            for task in workflow.task_set:
                if task.state is not NONE:
                    continue

                deps = task.input_task_id_dependency_set
                if not deps:
                    task.state = READY
                    changed = True
                    continue

                ready = True
                for input_task_id, dep in deps:
                    inp = task_dict.get(input_task_id)
                    if inp is None:
                        ready = False
                        break

                    if dep == BaseTaskDependency.FS:
                        if inp.state is not FINISHED:
                            ready = False
                            break

                    elif dep == BaseTaskDependency.SS:
                        # READY synchronization: predecessor must be READY or higher
                        if inp.state not in (READY, WORKING, FINISHED):
                            ready = False
                            break

                    elif dep == BaseTaskDependency.SF:
                        pass
                    elif dep == BaseTaskDependency.FF:
                        pass

                if ready:
                    task.state = READY
                    changed = True

            if not changed:
                break

    def __check_working_workflow(
        self,
        workflow: BaseWorkflow,
        work_amount_limit_per_unit_time: float = 1e10,
        total_work_amount_in_working_tasks: float = None,
        count_auto_task_in_work_amount_limit: bool = False,
    ):
        READY = BaseTaskState.READY
        WORKING = BaseTaskState.WORKING

        W_FREE = BaseWorkerState.FREE
        W_WORK = BaseWorkerState.WORKING
        W_ABS = BaseWorkerState.ABSENCE

        F_FREE = BaseFacilityState.FREE
        F_WORK = BaseFacilityState.WORKING
        F_ABS = BaseFacilityState.ABSENCE

        worker_dict = self.worker_dict
        facility_dict = self.facility_dict

        # Calculate total work amount in working tasks before allocation if not provided
        if total_work_amount_in_working_tasks is None:
            total_work_amount_in_working_tasks = sum(
                task.remaining_work_amount
                for task in self.task_set
                if task.state == BaseTaskState.WORKING
                and (
                    count_auto_task_in_work_amount_limit
                    or not task.auto_task
                )
            )

        for task in workflow.task_set:
            s = task.state

            if s is READY and (
                task.auto_task or task.allocated_worker_facility_id_tuple_set
            ):
                apply_limit = (
                    count_auto_task_in_work_amount_limit or not task.auto_task
                )
                if (not apply_limit) or (
                    total_work_amount_in_working_tasks + task.remaining_work_amount
                    <= work_amount_limit_per_unit_time
                ):
                    task.state = WORKING
                    if apply_limit:
                        total_work_amount_in_working_tasks += task.remaining_work_amount
                    for (
                        worker_id,
                        facility_id,
                    ) in task.allocated_worker_facility_id_tuple_set:
                        w = worker_dict.get(worker_id)
                        if w and w.state is not W_ABS and w.state is W_FREE:
                            w.state = W_WORK
                        if task.need_facility:
                            f = facility_dict.get(facility_id)
                            if f and f.state is not F_ABS and f.state is F_FREE:
                                f.state = F_WORK
                    continue

            if s is WORKING and task.allocated_worker_facility_id_tuple_set:
                for (
                    worker_id,
                    facility_id,
                ) in task.allocated_worker_facility_id_tuple_set:
                    w = worker_dict.get(worker_id)
                    if w and w.state is W_FREE:
                        w.state = W_WORK
                    if task.need_facility:
                        f = facility_dict.get(facility_id)
                        if f and f.state is F_FREE:
                            f.state = F_WORK
        
        # Return the updated total work amount
        return total_work_amount_in_working_tasks

    def __check_finished_workflow(
        self, workflow: BaseWorkflow, error_tol: float = 1e-10
    ):
        WORKING = BaseTaskState.WORKING
        FINISHED = BaseTaskState.FINISHED

        W_FREE = BaseWorkerState.FREE
        F_FREE = BaseFacilityState.FREE

        task_dict = self.task_dict
        worker_dict = self.worker_dict
        facility_dict = self.facility_dict

        for task in workflow.task_set:
            if not (
                task.state is WORKING and task.remaining_work_amount < 0.0 + error_tol
            ):
                continue

            finished_ok = True
            for input_task_id, dep in task.input_task_id_dependency_set:
                inp = task_dict.get(input_task_id)
                if inp is None:
                    finished_ok = False
                if dep == BaseTaskDependency.SF:
                    if inp.state not in (BaseTaskState.WORKING, BaseTaskState.FINISHED):
                        finished_ok = False
                        break
                elif dep == BaseTaskDependency.FF:
                    if inp.state is not BaseTaskState.FINISHED:
                        finished_ok = False
                        break

            if not finished_ok:
                continue

            task.state = FINISHED
            task.remaining_work_amount = 0.0

            for worker_id, facility_id in task.allocated_worker_facility_id_tuple_set:
                w = worker_dict.get(worker_id)
                if w:
                    if w.assigned_task_facility_id_tuple_set and all(
                        (task_dict.get(tid, None) is not None)
                        and (task_dict[tid].state is FINISHED)
                        for (tid, _fid) in w.assigned_task_facility_id_tuple_set
                    ):
                        w.state = W_FREE
                    w.remove_assigned_pair((task.ID, facility_id))

                if task.need_facility:
                    f = facility_dict.get(facility_id)
                    if f:
                        if f.assigned_task_worker_id_tuple_set and all(
                            (task_dict.get(tid, None) is not None)
                            and (task_dict[tid].state is FINISHED)
                            for (tid, _wid) in f.assigned_task_worker_id_tuple_set
                        ):
                            f.state = F_FREE
                        f.remove_assigned_pair((task.ID, worker_id))

            # Consistently use frozenset() here as well
            task.allocated_worker_facility_id_tuple_set = frozenset()

    def can_put_component_to_workplace(
        self,
        workplace: BaseWorkplace,
        component: BaseComponent,
        error_tol: float = 1e-8,
    ):
        """
        Check whether the target component can be put to this workplace in this time.

        Args:
            workplace (BaseWorkplace): Target workplace for checking.
            component (BaseComponent): Component to check for placement.
            error_tol (float, optional): Numerical error tolerance. Defaults to 1e-8.

        Returns:
            bool: Whether the target component can be put to this workplace in this time.
        """
        can_put = False
        if workplace.available_space_size > component.space_size - error_tol:
            can_put = True
        return can_put

    def can_add_resources_to_task(
        self,
        task: BaseTask,
        worker: Optional[BaseWorker] = None,
        facility: Optional[BaseFacility] = None,
    ):
        """
        Judge whether the target task can be assigned additional resources.

        Args:
            task (BaseTask): Target task for checking.
            worker (BaseWorker, optional): Target worker for allocating. Defaults to None.
            facility (BaseFacility, optional): Target facility for allocating. Defaults to None.

        Returns:
            bool: True if the target task can be assigned the specified resources, False otherwise.
        """
        if task.state == BaseTaskState.NONE:
            return False
        elif task.state == BaseTaskState.FINISHED:
            return False

        # True if none of the allocated resources have solo_working attribute True.
        for w_id, f_id in task.allocated_worker_facility_id_tuple_set:
            w = self.worker_dict.get(w_id, None)
            f = self.facility_dict.get(f_id, None)
            if w is not None:
                if w.solo_working:
                    return False
                if f is not None:
                    if f.solo_working:
                        return False

        # solo_working check
        if worker is not None:
            if worker.solo_working:
                if len(task.allocated_worker_facility_id_tuple_set) > 0:
                    return False
        if facility is not None:
            if facility.solo_working:
                if len(task.allocated_worker_facility_id_tuple_set) > 0:
                    return False

        # Fixing allocating worker/facility id list check
        if worker is not None:
            if task.fixing_allocating_worker_id_set is not None:
                if worker.ID not in task.fixing_allocating_worker_id_set:
                    return False
        if facility is not None:
            if task.fixing_allocating_facility_id_set is not None:
                if facility.ID not in task.fixing_allocating_facility_id_set:
                    return False

        # multi-task in one facility check
        if facility is not None:
            if len(facility.assigned_task_worker_id_tuple_set) > 0:
                return False

        # skill check
        if facility is not None:
            if facility.has_workamount_skill(task.name):
                if worker.has_facility_skill(
                    facility.name
                ) and worker.has_workamount_skill(task.name):
                    return True
                else:
                    return False
            else:
                return False
        elif worker is not None:
            if worker.has_workamount_skill(task.name):
                return True
            else:
                return False
        else:
            return False

    def is_ready_component(self, component: BaseComponent):
        """
        Check whether the given component is in the READY state.

        READY component is defined by satisfying the following conditions:
        - All tasks are not NONE.
        - There is no WORKING task in this component.
        - The states of targeted tasks include READY.

        Args:
            component (BaseComponent): The component to check.

        Returns:
            bool: True if this component is READY, False otherwise.
        """
        targeted_task_set = self.get_target_task_set(component.targeted_task_id_set)
        all_none_flag = all(
            [task.state == BaseTaskState.NONE for task in targeted_task_set]
        )

        any_working_flag = any(
            [task.state == BaseTaskState.WORKING for task in targeted_task_set]
        )

        any_ready_flag = any(
            [task.state == BaseTaskState.READY for task in targeted_task_set]
        )

        all_finished_flag = all(
            [task.state == BaseTaskState.FINISHED for task in targeted_task_set]
        )

        if all_finished_flag:
            return False

        if not all_none_flag and (not any_working_flag) and any_ready_flag:
            return True

        return False

    def remove_absence_time_list(self):
        """
        Remove record information on `absence_time_list`.

        This method removes all records related to absence times from products, workflows,
        teams, workplaces, and the project's cost record list. It also updates the simulation time
        and clears the absence_time_list.

        Returns:
            None
        """
        for product in self.product_set:
            product.remove_absence_time_list(self.absence_time_list)
        for workflow in self.workflow_set:
            workflow.remove_absence_time_list(self.absence_time_list)
        for team in self.team_set:
            team.remove_absence_time_list(self.absence_time_list)
        for workplace in self.workplace_set:
            workplace.remove_absence_time_list(self.absence_time_list)

        for step_time in sorted(self.absence_time_list, reverse=True):
            if step_time < len(self.cost_record_list):
                self.cost_record_list.pop(step_time)

        self.time = self.time - len(self.absence_time_list)
        self.absence_time_list = []

    def insert_absence_time_list(self, absence_time_list: list[int]):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step times in simulation.

        Returns:
            None
        """
        # duplication check
        new_absence_time_list = []
        for time in absence_time_list:
            if time not in self.absence_time_list:
                new_absence_time_list.append(time)
        for product in self.product_set:
            product.insert_absence_time_list(new_absence_time_list)
        for workflow in self.workflow_set:
            workflow.insert_absence_time_list(new_absence_time_list)
        for team in self.team_set:
            team.insert_absence_time_list(absence_time_list)
        for workplace in self.workplace_set:
            workplace.insert_absence_time_list(absence_time_list)

        for step_time in sorted(new_absence_time_list):
            self.cost_record_list.insert(step_time, 0.0)

        self.time = self.time + len(new_absence_time_list)
        self.absence_time_list.extend(new_absence_time_list)

    def set_last_datetime(
        self,
        last_datetime: datetime.datetime,
        unit_timedelta: Optional[datetime.timedelta] = None,
        set_init_datetime: bool = True,
    ):
        """
        Set the last datetime to project simulation result.

        This method calculates and optionally sets the initial datetime (`init_datetime`) of the project
        so that the simulation ends at the specified `last_datetime`.

        Args:
            last_datetime (datetime.datetime): Last datetime of the project.
            unit_timedelta (datetime.timedelta, optional): Unit time of simulation. If None, uses self.unit_timedelta.
            set_init_datetime (bool, optional): If True, sets the calculated init_datetime to this project. Defaults to True.

        Returns:
            datetime.datetime: Calculated init datetime of the project considering the `last_datetime`.
        """
        if unit_timedelta is None:
            unit_timedelta = self.unit_timedelta
        else:
            self.unit_timedelta = unit_timedelta

        init_datetime = last_datetime - unit_timedelta * (self.time - 1)
        if set_init_datetime:
            self.init_datetime = init_datetime

        return init_datetime

    def set_component_on_workplace(
        self,
        target_component: BaseComponent,
        placed_workplace: BaseWorkplace,
        set_to_all_children: bool = True,
    ):
        """
        Set the placed workplace for a component.

        Args:
            target_component (BaseComponent): Target component to set `placed_workplace`.
            placed_workplace (BaseWorkplace): Workplace to place this component in. If None, removes placement.
            set_to_all_children (bool, optional): If True, set placed_workplace to all child components recursively. Defaults to True.

        Returns:
            None
        """
        target_component.placed_workplace_id = (
            placed_workplace.ID if placed_workplace else None
        )
        if placed_workplace is not None:
            if target_component.ID not in placed_workplace.placed_component_id_set:
                placed_workplace.placed_component_id_set.add(target_component.ID)
                placed_workplace.available_space_size -= target_component.space_size

        if set_to_all_children:
            for child_c_id in target_component.child_component_id_set:
                child_c = self.component_dict.get(child_c_id, None)
                self.set_component_on_workplace(
                    child_c, placed_workplace, set_to_all_children=set_to_all_children
                )

    def remove_component_on_workplace(
        self,
        target_component: BaseComponent,
        placed_workplace: BaseWorkplace,
        set_to_all_children: bool = True,
    ):
        """
        Remove the placed workplace from a component.

        Args:
            target_component (BaseComponent): Component to remove from the workplace.
            placed_workplace (BaseWorkplace): Workplace from which the component will be removed.
            set_to_all_children (bool, optional): If True, remove placed_workplace from all child components recursively. Defaults to True.

        Returns:
            None
        """
        placed_workplace.placed_component_id_set.remove(target_component.ID)
        placed_workplace.available_space_size += target_component.space_size

        if set_to_all_children:
            for child_c_id in target_component.child_component_id_set:
                child_c = self.component_dict.get(child_c_id, None)
                self.remove_component_on_workplace(
                    child_c,
                    placed_workplace,
                    set_to_all_children=set_to_all_children,
                )

    def get_all_task_set(self):
        """
        Get all task set in this project.

        Returns:
            Set[BaseTask]: All task set in this project.
        """
        task_set = set()
        for workflow in self.workflow_set:
            task_set.update(workflow.task_set)
        return task_set

    def get_target_task_set(self, target_task_id_set: set[str]):
        """
        Get tasks by their IDs.

        Args:
            target_task_id_set (set[str]):
                set of task IDs to filter.
        Returns:
            set[BaseTask]: Set of tasks matching the provided IDs.
        """
        if not self.task_dict:
            self.__initialize_child_instance_set_id_instance_dict()
        return {
            self.task_dict[tid] for tid in target_task_id_set if tid in self.task_dict
        }

    def get_all_component_set(self):
        """
        Get all component set in this project.

        Returns:
            set[BaseComponent]: All component set in this project.
        """
        component_set = set()
        for product in self.product_set:
            component_set.update(product.component_set)
        return component_set

    def get_all_id_name_dict(self):
        """
        Get a flat dictionary of all id-name mappings in this project.

        Returns:
            dict: Flat dictionary containing all {id: name} mappings.
        """
        result = {}

        # BaseProduct
        for product in self.product_set:
            result[product.ID] = product.name

        # BaseComponent
        for component in self.component_set:
            result[component.ID] = component.name

        # BaseWorkflow
        for workflow in self.workflow_set:
            result[workflow.ID] = workflow.name

        # BaseTask
        for task in self.task_set:
            result[task.ID] = task.name

        # BaseTeam
        for team in self.team_set:
            result[team.ID] = team.name

        # BaseWorker
        for worker in self.worker_set:
            result[worker.ID] = worker.name

        # BaseWorkplace
        for workplace in self.workplace_set:
            result[workplace.ID] = workplace.name

        # BaseFacility
        for facility in self.facility_set:
            result[facility.ID] = facility.name

        return result

    def create_gantt_plotly(
        self,
        title: str = "Gantt Chart",
        target_product_id_order_list: list[str] = None,
        target_component_id_order_list: list[str] = None,
        target_workflow_id_order_list: list[str] = None,
        target_task_id_order_list: list[str] = None,
        target_team_id_order_list: list[str] = None,
        target_worker_id_order_list: list[str] = None,
        target_workplace_id_order_list: list[str] = None,
        target_facility_id_order_list: list[str] = None,
        colors: dict[str, str] = None,
        index_col: str = None,
        showgrid_x: bool = True,
        showgrid_y: bool = True,
        group_tasks: bool = False,
        show_colorbar: bool = True,
        finish_margin: float = 1.0,
        save_fig_path: str = None,
    ):
        """
        Create a Gantt chart using Plotly.

        This method should be used after simulation to visualize the schedule of components, tasks, workers, and facilities.

        Args:
            target_product_id_order_list (list[str], optional): List of target product IDs in the desired order. Defaults to None.
            target_component_id_order_list (list[str], optional): List of target component IDs in the desired order. Defaults to None.
            target_workflow_id_order_list (list[str], optional): List of target workflow IDs in the desired order. Defaults to None.
            target_task_id_order_list (list[str], optional): List of target task IDs in the desired order. Defaults to None.
            target_team_id_order_list (list[str], optional): List of target team IDs in the desired order. Defaults to None.
            target_worker_id_order_list (list[str], optional): List of target worker IDs in the desired order. Defaults to None.
            target_workplace_id_order_list (list[str], optional): List of target workplace IDs in the desired order. Defaults to None.
            target_facility_id_order_list (list[str], optional): List of target facility IDs in the desired order. Defaults to None.
            title (str, optional): Title of the Gantt chart. Defaults to "Gantt Chart".
            colors (dict[str, str], optional): Color settings for Plotly Gantt chart. Defaults to None.
            index_col (str, optional): Column name to group bars by color. Defaults to None ("Type").
            showgrid_x (bool, optional): Whether to show grid lines on the x-axis. Defaults to True.
            showgrid_y (bool, optional): Whether to show grid lines on the y-axis. Defaults to True.
            group_tasks (bool, optional): Whether to group tasks with the same name. Defaults to False.
            show_colorbar (bool, optional): Whether to show the color bar. Defaults to True.
            finish_margin (float, optional): Margin to add to the finish time in the Gantt chart. Defaults to 1.0.
            save_fig_path (str, optional): Path to save the figure. Supports "html", "json", or image formats. Defaults to None.

        Returns:
            plotly.graph_objs.Figure: Plotly figure object for the Gantt chart.
        """
        colors = (
            colors
            if colors is not None
            else {
                "Component": "rgb(246, 37, 105)",
                "Task": "rgb(146, 237, 5)",
                "Worker": "rgb(46, 137, 205)",
                "Facility": "rgb(46, 137, 205)",
            }
        )
        index_col = index_col if index_col is not None else "Type"
        df = []

        target_product_instance_list = self.product_set
        if target_product_id_order_list is not None:
            id_to_product_instance = {
                instance.ID: instance for instance in self.product_set
            }
            target_product_instance_list = [
                id_to_product_instance[tid]
                for tid in target_product_id_order_list
                if tid in id_to_product_instance
            ]
        for product in target_product_instance_list:
            df.extend(
                product.create_data_for_gantt_plotly(
                    self.init_datetime,
                    self.unit_timedelta,
                    target_id_order_list=target_component_id_order_list,
                    finish_margin=finish_margin,
                )
            )

        target_workflow_instance_list = self.workflow_set
        if target_workflow_id_order_list is not None:
            id_to_workflow_instance = {
                instance.ID: instance for instance in self.workflow_set
            }
            target_workflow_instance_list = [
                id_to_workflow_instance[tid]
                for tid in target_workflow_id_order_list
                if tid in id_to_workflow_instance
            ]
        for workflow in target_workflow_instance_list:
            df.extend(
                workflow.create_data_for_gantt_plotly(
                    self.init_datetime,
                    self.unit_timedelta,
                    target_id_order_list=target_task_id_order_list,
                    finish_margin=finish_margin,
                )
            )

        target_team_instance_list = self.team_set
        if target_team_id_order_list is not None:
            id_to_team_instance = {instance.ID: instance for instance in self.team_set}
            target_team_instance_list = [
                id_to_team_instance[tid]
                for tid in target_team_id_order_list
                if tid in id_to_team_instance
            ]
        for team in target_team_instance_list:
            df.extend(
                team.create_data_for_gantt_plotly(
                    self.init_datetime,
                    self.unit_timedelta,
                    target_id_order_list=target_worker_id_order_list,
                    finish_margin=finish_margin,
                    # view_ready=view_ready,
                    # view_absence=view_absence,
                )
            )

        target_workplace_instance_list = self.workplace_set
        if target_workplace_id_order_list is not None:
            id_to_workplace_instance = {
                instance.ID: instance for instance in self.workplace_set
            }
            target_workplace_instance_list = [
                id_to_workplace_instance[tid]
                for tid in target_workplace_id_order_list
                if tid in id_to_workplace_instance
            ]
        for workplace in target_workplace_instance_list:
            df.extend(
                workplace.create_data_for_gantt_plotly(
                    self.init_datetime,
                    self.unit_timedelta,
                    target_id_order_list=target_facility_id_order_list,
                    finish_margin=finish_margin,
                    # view_ready=view_ready,
                    # view_absence=view_absence,
                )
            )

        fig = ff.create_gantt(
            df,
            title=title,
            colors=colors,
            index_col=index_col,
            showgrid_x=showgrid_x,
            showgrid_y=showgrid_y,
            show_colorbar=show_colorbar,
            group_tasks=group_tasks,
        )

        if save_fig_path is not None:
            dot_point = save_fig_path.rfind(".")
            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            else:
                fig.write_image(save_fig_path)

        return fig

    def get_networkx_graph(
        self, view_workers: bool = False, view_facilities: bool = False
    ):
        """
        Get the information of the project as a NetworkX directed graph.

        Args:
            view_workers (bool, optional): If True, include workers in the graph. Defaults to False.
            view_facilities (bool, optional): If True, include facilities in the graph. Defaults to False.

        Returns:
            networkx.DiGraph: Directed graph representing the project structure.
        """
        g_product = nx.DiGraph()
        for product in self.product_set:
            g_product = nx.compose(g_product, product.get_networkx_graph())

        g_workflow = nx.DiGraph()
        for workflow in self.workflow_set:
            g_workflow = nx.compose(g_workflow, workflow.get_networkx_graph())

        g_team = nx.DiGraph()
        # 1. add all nodes
        for team in self.team_set:
            g_team.add_node(team)
        # 2. add all edges
        for team in self.team_set:
            if team.parent_team_id is not None:
                parent_team = self.team_dict.get(team.parent_team_id, None)
                g_team.add_edge(parent_team, team)
        if view_workers:
            for team in self.team_set:
                for w in team.worker_set:
                    g_team.add_node(w)
                    g_team.add_edge(team, w)

        g_workplace = nx.DiGraph()
        # 1. add all nodes
        for workplace in self.workplace_set:
            g_workplace.add_node(workplace)
        # 2. add all edges
        for workplace in self.workplace_set:
            if workplace.parent_workplace_id is not None:
                parent_workplace = self.workplace_dict.get(
                    workplace.parent_workplace_id, None
                )
                g_workplace.add_edge(parent_workplace, workplace)
        if view_facilities:
            for workplace in self.workplace_set:
                for w in workplace.facility_set:
                    g_workplace.add_node(w)
                    g_workplace.add_edge(workplace, w)

        g = nx.compose_all([g_product, g_workflow, g_team, g_workplace])

        # add edge between product and workflow
        for product in self.product_set:
            for c in product.component_set:
                targeted_task_set = self.get_target_task_set(c.targeted_task_id_set)
                for task in targeted_task_set:
                    g.add_edge(c, task)

        # add edge between workflow and team
        for team in self.team_set:
            targeted_task_set = self.get_target_task_set(team.targeted_task_id_set)
            for task in targeted_task_set:
                g.add_edge(team, task)

        if view_workers:
            for team in self.team_set:
                for w in team.worker_set:
                    # g.add_node(w)
                    g.add_edge(team, w)

        # add edge between workflow and workplace
        for workplace in self.workplace_set:
            targeted_task_set = self.get_target_task_set(workplace.targeted_task_id_set)
            for task in targeted_task_set:
                g.add_edge(workplace, task)

        if view_facilities:
            for workplace in self.workplace_set:
                for w in workplace.facility_set:
                    # g.add_node(w)
                    g.add_edge(workplace, w)

        return g

    def draw_networkx(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        arrows: bool = True,
        component_node_color: str = "#FF6600",
        task_node_color: str = "#00EE00",
        auto_task_node_color: str = "#005500",
        team_node_color: str = "#0099FF",
        worker_node_color: str = "#D9E5FF",
        view_workers: bool = False,
        view_facilities: bool = False,
        workplace_node_color: str = "#0099FF",
        facility_node_color: str = "#D9E5FF",
        figsize: tuple[float, float] = None,
        dpi: float = 100.0,
        save_fig_path: str = None,
        **kwargs,
    ):
        """
        Draw the project structure as a NetworkX graph using matplotlib.

        Args:
            g (networkx.DiGraph, optional): NetworkX graph to draw. Defaults to None (uses self.get_networkx_graph()).
            pos (dict, optional): Node positions for layout. Defaults to None (uses networkx.spring_layout).
            arrows (bool, optional): Whether to draw arrows for directed edges. Defaults to True.
            component_node_color (str, optional): Color for component nodes. Defaults to "#FF6600".
            task_node_color (str, optional): Color for task nodes. Defaults to "#00EE00".
            auto_task_node_color (str, optional): Color for auto task nodes. Defaults to "#005500".
            team_node_color (str, optional): Color for team nodes. Defaults to "#0099FF".
            worker_node_color (str, optional): Color for worker nodes. Defaults to "#D9E5FF".
            view_workers (bool, optional): Whether to include workers in the graph. Defaults to False.
            view_facilities (bool, optional): Whether to include facilities in the graph. Defaults to False.
            workplace_node_color (str, optional): Color for workplace nodes. Defaults to "#0099FF".
            facility_node_color (str, optional): Color for facility nodes. Defaults to "#D9E5FF".
            figsize (tuple[float, float], optional): Figure size in inches. Defaults to None ([6.4, 4.8]).
            dpi (float, optional): Figure resolution in dots-per-inch. Defaults to 100.0.
            save_fig_path (str, optional): Path to save the figure. Defaults to None.
            **kwargs: Additional keyword arguments for networkx drawing functions.

        Returns:
            matplotlib.figure.Figure: Matplotlib figure object for the network graph.
        """

        if figsize is None:
            figsize = [6.4, 4.8]
        fig = plt.figure(figsize=figsize, dpi=dpi)
        g = (
            g
            if g is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(g)

        # Product
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=self.component_set,
            node_color=component_node_color,
            **kwargs,
        )
        # Workflow
        normal_task_set = [task for task in self.task_set if not task.auto_task]
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=normal_task_set,
            node_color=task_node_color,
            **kwargs,
        )
        auto_task_set = {task for task in self.task_set if task.auto_task}
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=auto_task_set,
            node_color=auto_task_node_color,
        )
        # Team
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=self.team_set,
            node_color=team_node_color,
            **kwargs,
        )
        if view_workers:
            worker_set = set()
            for team in self.team_set:
                worker_set.update(team.worker_set)

            nx.draw_networkx_nodes(
                g,
                pos,
                nodelist=worker_set,
                node_color=worker_node_color,
                **kwargs,
            )

        # Workplace
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=self.workplace_set,
            node_color=workplace_node_color,
            **kwargs,
        )
        if view_facilities:
            facility_set = set()
            for workplace in self.workplace_set:
                facility_set.update(workplace.facility_set)

            nx.draw_networkx_nodes(
                g,
                pos,
                nodelist=facility_set,
                node_color=facility_node_color,
                **kwargs,
            )

        nx.draw_networkx_labels(g, pos)
        nx.draw_networkx_edges(g, pos, arrows=arrows, **kwargs)
        plt.axis("off")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig

    def get_node_and_edge_trace_for_plotly_network(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        node_size: int = 20,
        component_node_color: str = "#FF6600",
        task_node_color: str = "#00EE00",
        auto_task_node_color: str = "#005500",
        team_node_color: str = "#0099FF",
        worker_node_color: str = "#D9E5FF",
        view_workers: bool = False,
        workplace_node_color: str = "#0099FF",
        facility_node_color: str = "#D9E5FF",
        view_facilities: bool = False,
    ):
        """
        Get nodes and edges information for a Plotly network visualization.

        Args:
            g (networkx.DiGraph, optional): NetworkX graph to visualize. Defaults to None (uses self.get_networkx_graph()).
            pos (dict, optional): Node positions for layout. Defaults to None (uses networkx.spring_layout).
            node_size (int, optional): Size of nodes in the plot. Defaults to 20.
            component_node_color (str, optional): Color for component nodes. Defaults to "#FF6600".
            task_node_color (str, optional): Color for task nodes. Defaults to "#00EE00".
            auto_task_node_color (str, optional): Color for auto task nodes. Defaults to "#005500".
            team_node_color (str, optional): Color for team nodes. Defaults to "#0099FF".
            worker_node_color (str, optional): Color for worker nodes. Defaults to "#D9E5FF".
            view_workers (bool, optional): Whether to include workers in the graph. Defaults to False.
            workplace_node_color (str, optional): Color for workplace nodes. Defaults to "#0099FF".
            facility_node_color (str, optional): Color for facility nodes. Defaults to "#D9E5FF".
            view_facilities (bool, optional): Whether to include facilities in the graph. Defaults to False.

        Returns:
            component_node_trace: Plotly Scatter trace for component nodes.
            task_node_trace: Plotly Scatter trace for task nodes.
            auto_task_node_trace: Plotly Scatter trace for auto task nodes.
            team_node_trace: Plotly Scatter trace for team nodes.
            worker_node_trace: Plotly Scatter trace for worker nodes.
            workplace_node_trace: Plotly Scatter trace for workplace nodes.
            facility_node_trace: Plotly Scatter trace for facility nodes.
            edge_trace: Plotly Scatter trace for edges.
        """
        g = (
            g
            if g is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(g)

        component_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={
                "color": component_node_color,
                "size": node_size,
            },
        )

        task_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={
                "color": task_node_color,
                "size": node_size,
            },
        )

        auto_task_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={
                "color": auto_task_node_color,
                "size": node_size,
            },
        )

        team_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={
                "color": team_node_color,
                "size": node_size,
            },
        )

        worker_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={
                "color": worker_node_color,
                "size": node_size,
            },
        )

        workplace_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={
                "color": workplace_node_color,
                "size": node_size,
            },
        )

        facility_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={
                "color": facility_node_color,
                "size": node_size,
            },
        )

        edge_trace = go.Scatter(
            x=[],
            y=[],
            line={"width": 0, "color": "#888"},
            mode="lines",
        )

        for node in g.nodes:
            x, y = pos[node]
            if isinstance(node, BaseComponent):
                component_node_trace["x"] = component_node_trace["x"] + (x,)
                component_node_trace["y"] = component_node_trace["y"] + (y,)
                component_node_trace["text"] = component_node_trace["text"] + (node,)
            elif isinstance(node, BaseTask):
                if not node.auto_task:
                    task_node_trace["x"] = task_node_trace["x"] + (x,)
                    task_node_trace["y"] = task_node_trace["y"] + (y,)
                    task_node_trace["text"] = task_node_trace["text"] + (node,)
                elif node.auto_task:
                    auto_task_node_trace["x"] = auto_task_node_trace["x"] + (x,)
                    auto_task_node_trace["y"] = auto_task_node_trace["y"] + (y,)
                    auto_task_node_trace["text"] = auto_task_node_trace["text"] + (
                        node,
                    )
            elif isinstance(node, BaseWorkplace):
                workplace_node_trace["x"] = workplace_node_trace["x"] + (x,)
                workplace_node_trace["y"] = workplace_node_trace["y"] + (y,)
                workplace_node_trace["text"] = workplace_node_trace["text"] + (node,)
            elif isinstance(node, BaseFacility):
                facility_node_trace["x"] = facility_node_trace["x"] + (x,)
                facility_node_trace["y"] = facility_node_trace["y"] + (y,)
                facility_node_trace["text"] = facility_node_trace["text"] + (node,)
            elif isinstance(node, BaseTeam):
                team_node_trace["x"] = team_node_trace["x"] + (x,)
                team_node_trace["y"] = team_node_trace["y"] + (y,)
                team_node_trace["text"] = team_node_trace["text"] + (node,)
            elif isinstance(node, BaseWorker):
                worker_node_trace["x"] = worker_node_trace["x"] + (x,)
                worker_node_trace["y"] = worker_node_trace["y"] + (y,)
                worker_node_trace["text"] = worker_node_trace["text"] + (node,)

        for edge in g.edges:
            x = edge[0]
            y = edge[1]
            x_pos_x, x_pos_y = pos[x]
            y_pos_x, y_pos_y = pos[y]
            edge_trace["x"] += (x_pos_x, y_pos_x)
            edge_trace["y"] += (x_pos_y, y_pos_y)

        return (
            component_node_trace,
            task_node_trace,
            auto_task_node_trace,
            team_node_trace,
            worker_node_trace,
            workplace_node_trace,
            facility_node_trace,
            edge_trace,
        )

    def draw_plotly_network(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        title: str = "Project",
        node_size: int = 20,
        component_node_color: str = "#FF6600",
        task_node_color: str = "#00EE00",
        auto_task_node_color: str = "#005500",
        team_node_color: str = "#0099FF",
        worker_node_color: str = "#D9E5FF",
        view_workers: bool = False,
        workplace_node_color: str = "#0099FF",
        facility_node_color: str = "#D9E5FF",
        view_facilities: bool = False,
        save_fig_path: str = None,
    ):
        """
        Draw the project structure as a Plotly network graph.

        Args:
            g (networkx.DiGraph, optional): NetworkX graph to visualize. Defaults to None (uses self.get_networkx_graph()).
            pos (dict, optional): Node positions for layout. Defaults to None (uses networkx.spring_layout).
            title (str, optional): Title of the Plotly figure. Defaults to "Project".
            node_size (int, optional): Size of nodes in the plot. Defaults to 20.
            component_node_color (str, optional): Color for component nodes. Defaults to "#FF6600".
            task_node_color (str, optional): Color for task nodes. Defaults to "#00EE00".
            auto_task_node_color (str, optional): Color for auto task nodes. Defaults to "#005500".
            team_node_color (str, optional): Color for team nodes. Defaults to "#0099FF".
            worker_node_color (str, optional): Color for worker nodes. Defaults to "#D9E5FF".
            view_workers (bool, optional): Whether to include workers in the graph. Defaults to False.
            workplace_node_color (str, optional): Color for workplace nodes. Defaults to "#0099FF".
            facility_node_color (str, optional): Color for facility nodes. Defaults to "#D9E5FF".
            view_facilities (bool, optional): Whether to include facilities in the graph. Defaults to False.
            save_fig_path (str, optional): Path to save the figure. Supports "html", "json", or image formats. Defaults to None.

        Returns:
            plotly.graph_objs.Figure: Plotly figure object for the network graph.
        """
        g = (
            g
            if g is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(g)
        (
            component_node_trace,
            task_node_trace,
            auto_task_node_trace,
            team_node_trace,
            worker_node_trace,
            workplace_node_trace,
            facility_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(g, pos, node_size=node_size)
        fig = go.Figure(
            data=[
                edge_trace,
                component_node_trace,
                task_node_trace,
                auto_task_node_trace,
                team_node_trace,
                worker_node_trace,
                workplace_node_trace,
                facility_node_trace,
            ],
            layout=go.Layout(
                title=title,
                showlegend=False,
                #         hovermode='closest',
                #         margin=dict(b=20,l=5,r=5,t=40),
                annotations=[
                    {
                        "ax": edge_trace["x"][index * 2],
                        "ay": edge_trace["y"][index * 2],
                        "axref": "x",
                        "ayref": "y",
                        "x": edge_trace["x"][index * 2 + 1],
                        "y": edge_trace["y"][index * 2 + 1],
                        "xref": "x",
                        "yref": "y",
                        "showarrow": True,
                        "arrowhead": 5,
                    }
                    for index in range(0, int(len(edge_trace["x"]) / 2))
                ],
                xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            ),
        )
        if save_fig_path is not None:
            dot_point = save_fig_path.rfind(".")
            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            else:
                fig.write_image(save_fig_path)

        return fig

    def print_log(self, target_step_time: int):
        """
        Print log in the specified step time.

        Args:
            target_step_time (int): Target step time for printing the log.
        """
        for product in self.product_set:
            product.print_log(target_step_time)
        for workflow in self.workflow_set:
            workflow.print_log(target_step_time)
        for team in self.team_set:
            team.print_log(target_step_time)
        for workplace in self.workplace_set:
            workplace.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """
        Print all logs in chronological order.

        Args:
            backward (bool, optional): If True, print logs in reverse (backward) order. Defaults to False.
        """
        if self.simulation_mode == SimulationMode.BACKWARD:
            backward = True
        elif self.simulation_mode == SimulationMode.FORWARD:
            backward = False

        for workflow in self.workflow_set:
            if len(workflow.task_set) > 0:
                sample_task = next(iter(workflow.task_set))
                n = len(sample_task.state_record_list)
                for i in range(n):
                    t = n - 1 - i if backward else i
                    print("TIME: ", t)
                    self.print_log(t)

    def write_simple_json(
        self, file_path: str, encoding: str = "utf-8", indent: int = 4
    ):
        """
        Create a JSON file of this project.

        Args:
            file_path (str): File path for saving this project data.
            encoding (str, optional): Encoding for the JSON file. Defaults to "utf-8".
            indent (int, optional): Indentation level for JSON formatting. Defaults to 4.

        Returns:
            None
        """
        dict_data = {"pDESy": []}
        dict_data["pDESy"].append(
            {
                "type": self.__class__.__name__,
                "name": self.name,
                "ID": self.ID,
                "init_datetime": self.init_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "unit_timedelta": str(self.unit_timedelta.total_seconds()),
                "absence_time_list": self.absence_time_list,
                "perform_auto_task_while_absence_time": self.perform_auto_task_while_absence_time,
                "time": self.time,
                "cost_record_list": self.cost_record_list,
                "simulation_mode": int(self.simulation_mode),
                "status": int(self.status),
            }
        )
        for product in self.product_set:
            dict_data["pDESy"].append(product.export_dict_json_data())
        for workflow in self.workflow_set:
            dict_data["pDESy"].append(workflow.export_dict_json_data())
        for team in self.team_set:
            dict_data["pDESy"].append(team.export_dict_json_data())
        for workplace in self.workplace_set:
            dict_data["pDESy"].append(workplace.export_dict_json_data())
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(dict_data, f, indent=indent)

    def read_simple_json(self, file_path: str, encoding: str = "utf-8"):
        """
        Read a JSON file created by BaseProject.write_simple_json() and load project data.

        Args:
            file_path (str): File path for reading this project data.
            encoding (str, optional): Encoding for the JSON file. Defaults to "utf-8".

        Returns:
            None
        """
        pdes_json = open(file_path, "r", encoding=encoding)
        json_data = json.load(pdes_json)
        data = json_data["pDESy"]
        project_json = list(filter(lambda node: node["type"] == "BaseProject", data))[0]
        self.name = project_json["name"]
        self.ID = project_json["ID"]
        self.init_datetime = datetime.datetime.strptime(
            project_json["init_datetime"], "%Y-%m-%d %H:%M:%S"
        )
        self.unit_timedelta = datetime.timedelta(
            seconds=float(project_json["unit_timedelta"])
        )
        self.absence_time_list = project_json["absence_time_list"]
        self.perform_auto_task_while_absence_time = project_json[
            "perform_auto_task_while_absence_time"
        ]
        self.time = project_json["time"]
        self.cost_record_list = project_json["cost_record_list"]
        self.simulation_mode = SimulationMode(project_json["simulation_mode"])
        self.status = BaseProjectStatus(project_json["status"])
        # 1. read all node and attr only considering ID info
        # product
        product_json_list = list(
            filter(lambda node: node["type"] == "BaseProduct", data)
        )
        for product_json in product_json_list:
            product = BaseProduct(component_set=set())
            product.read_json_data(product_json)
            self.product_set.add(product)
        # workflow
        workflow_json_list = list(
            filter(lambda node: node["type"] == "BaseWorkflow", data)
        )
        for workflow_json in workflow_json_list:
            workflow = BaseWorkflow(task_set=set())
            workflow.read_json_data(workflow_json)
            self.workflow_set.add(workflow)

        # team
        team_json_list = list(filter(lambda node: node["type"] == "BaseTeam", data))
        for team_json in team_json_list:
            team = BaseTeam(worker_set=set())
            team.read_json_data(team_json)
            self.team_set.add(team)

        # workplace
        workplace_json_list = list(
            filter(lambda node: node["type"] == "BaseWorkplace", data)
        )
        for workplace_json in workplace_json_list:
            workplace = BaseWorkplace(facility_set=set())
            workplace.read_json_data(workplace_json)
            self.workplace_set.add(workplace)

        all_component_set = self.get_all_component_set()
        all_task_set = self.get_all_task_set()
        # 2. update ID info to instance info
        # 2-1. component
        all_component_id_set = {component.ID for component in all_component_set}
        all_task_id_set = {task.ID for task in all_task_set}
        all_team_id_set = {team.ID for team in self.team_set}
        all_workplace_id_set = {workplace.ID for workplace in self.workplace_set}
        for c in all_component_set:
            c.child_component_id_set &= all_component_id_set
            c.targeted_task_id_set &= all_task_id_set
            c.placed_workplace_id = (
                [
                    workplace.ID
                    for workplace in self.workplace_set
                    if workplace.ID == c.placed_workplace_id
                ]
                if c.placed_workplace_id is not None
                else None
            )
        # 2-2. task
        for t in all_task_set:
            t.input_task_id_dependency_set = {
                (
                    [task for task in all_task_set if task.ID == ID][0].ID,
                    BaseTaskDependency(dependency_number),
                )
                for (ID, dependency_number) in t.input_task_id_dependency_set
            }
            t.allocated_team_id_set &= all_team_id_set
            t.allocated_workplace_id_set &= all_workplace_id_set
            t.target_component_id = (
                [
                    component.ID
                    for component in all_component_set
                    if component.ID == t.target_component_id
                ][0]
                if t.target_component_id is not None
                else None
            )

            t.allocated_worker_facility_id_tuple_set = {
                (w_id, f_id)
                for (w_id, f_id) in t.allocated_worker_facility_id_tuple_set
                if (w_id, f_id) in t.allocated_worker_facility_id_tuple_set
            }

        # 2-3. team
        for x in self.team_set:
            x.targeted_task_id_set &= all_task_id_set
            x.parent_team_id = (
                [team.ID for team in self.team_set if team.ID == x.parent_team_id][0]
                if x.parent_team_id is not None
                else None
            )
            for w in x.worker_set:
                w.assigned_task_facility_id_tuple_set = {
                    task.ID
                    for task in all_task_set
                    if task.ID in w.assigned_task_facility_id_tuple_set
                }

        # 2-4. workplace
        for x in self.workplace_set:
            x.targeted_task_id_set &= all_task_id_set
            x.parent_workplace_id = (
                [
                    workplace.ID
                    for workplace in self.workplace_set
                    if workplace.ID == x.parent_workplace_id
                ][0]
                if x.parent_workplace_id is not None
                else None
            )
            x.placed_component_id_set = {
                component.ID
                for component in all_component_set
                if component.ID in x.placed_component_id_set
            }
            for f in x.facility_set:
                f.assigned_task_worker_id_tuple_set = {
                    task.ID
                    for task in all_task_set
                    if task.ID in f.assigned_task_worker_id_tuple_set
                }

        self.__initialize_child_instance_set_id_instance_dict()

    def get_all_worker_set(self):
        """
        Get all worker set of this project.

        Returns:
            set[BaseWorker]: All worker set of this project.
        """
        all_worker_set = set()
        for team in self.team_set:
            all_worker_set.update(team.worker_set)
        return all_worker_set

    def get_all_facility_set(self):
        """
        Get all facility set of this project.

        Returns:
            set[BaseFacility]: All facility set of this project.
        """
        all_facility_set = set()
        for workplace in self.workplace_set:
            all_facility_set.update(workplace.facility_set)
        return all_facility_set

    def append_project_log_from_simple_json(
        self, file_path: str, encoding: str = "utf-8"
    ):
        """
        Append project log information from a JSON file created by BaseProject.write_simple_json().

        Note:
            This function is not yet verified sufficiently.

        Args:
            file_path (str): File path for reading the extended project data.
            encoding (str, optional): Encoding for the JSON file. Defaults to "utf-8".

        Returns:
            None
        """
        warnings.warn(
            "This function is not yet verified sufficiently.",
            UserWarning,
        )
        with open(file_path, "r", encoding=encoding) as pdes_json:
            json_data = json.load(pdes_json)
            data = json_data["pDESy"]
            project_json = list(
                filter(lambda node: node["type"] == "BaseProject", data)
            )[0]

            target_absence_time_list = [
                self.time + t for t in project_json["absence_time_list"]
            ]
            self.absence_time_list.extend(target_absence_time_list)

            self.time = self.time + int(project_json["time"])
            self.cost_record_list.extend(project_json["cost_record_list"])

            # product
            all_component_set = self.get_all_component_set()
            product_json = list(
                filter(lambda node: node["type"] == "BaseProduct", data)
            )[0]
            for c_json in product_json["component_set"]:
                c = list(
                    filter(
                        lambda component, c_json=c_json: component.ID == c_json["ID"],
                        all_component_set,
                    )
                )[0]
                c.state = BaseComponentState(c_json["state"])
                c.state_record_list.extend(
                    [BaseComponentState(num) for num in c_json["state_record_list"]]
                )
                c.placed_workplace_id = c_json["placed_workplace_id"]
                c.placed_workplace_id_record_list_list.extend(
                    c_json["placed_workplace_id_record_list_list"]
                )

            # workflow
            workflow_j = list(
                filter(lambda node: node["type"] == "BaseWorkflow", data)
            )[0]
            for j in workflow_j["task_set"]:
                task = list(
                    filter(
                        lambda task, j=j: task.ID == j["ID"],
                        self.get_all_task_set(),
                    )
                )[0]
                task.est = j["est"]
                task.eft = j["eft"]
                task.lst = j["lst"]
                task.lft = j["lft"]
                task.remaining_work_amount = j["remaining_work_amount"]
                task.state = BaseTaskState(j["state"])
                task.state_record_list.extend(
                    [BaseTaskState(num) for num in j["state_record_list"]],
                )
                task.allocated_worker_facility_id_tuple_set = j[
                    "allocated_worker_facility_id_tuple_set"
                ]
                task.allocated_worker_facility_id_tuple_set_record_list.extend(
                    j["allocated_worker_facility_id_tuple_set_record_list"]
                )

            # organization
            o_json = list(
                filter(lambda node: node["type"] == "BaseOrganization", data)
            )[0]
            # team
            team_set_j = o_json["team_set"]
            for team_j in team_set_j:
                team = list(
                    filter(
                        lambda team, team_j=team_j: team.ID == team_j["ID"],
                        self.team_set,
                    )
                )[0]
                team.cost_record_list.extend(team_j["cost_record_list"])
                for j in team_j["worker_set"]:
                    worker = list(
                        filter(
                            lambda worker, j=j: worker.ID == j["ID"],
                            team.worker_set,
                        )
                    )[0]
                    worker.state = BaseWorkerState(j["state"])
                    worker.state_record_list.extend(
                        [BaseWorkerState(num) for num in j["state_record_list"]],
                    )
                    worker.cost_record_list.extend(j["cost_record_list"])
                    worker.assigned_task_facility_id_tuple_set = set(
                        j["assigned_task_facility_id_tuple_set"]
                    )
                    worker.assigned_task_facility_id_tuple_set_record_list.extend(
                        j["assigned_task_facility_id_tuple_set_record_list"]
                    )

            # workplace
            workplace_set_j = o_json["workplace_set"]
            for workplace_j in workplace_set_j:
                workplace = list(
                    filter(
                        lambda workplace, workplace_j=workplace_j: workplace.ID
                        == workplace_j["ID"],
                        self.workplace_set,
                    )
                )[0]
                workplace.cost_record_list.extend(workplace_j["cost_record_list"])
                workplace.placed_component_id_set = workplace_j[
                    "placed_component_id_set"
                ]
                workplace.placed_component_id_set_record_list.extend(
                    workplace_j["placed_component_id_set_record_list"]
                )
                for j in workplace_j["facility_set"]:
                    facility = list(
                        filter(
                            lambda worker, j=j: worker.ID == j["ID"],
                            workplace.facility_set,
                        )
                    )[0]
                    facility.state = BaseWorkerState(j["state"])
                    facility.state_record_list.extend(
                        [BaseWorkerState(num) for num in j["state_record_list"]],
                    )
                    facility.cost_record_list.extend(j["cost_record_list"])
                    facility.assigned_task_worker_id_tuple_set = set(
                        j["assigned_task_worker_id_tuple_set"]
                    )
                    facility.assigned_task_worker_id_tuple_set_record_list.extend(
                        j["assigned_task_worker_id_tuple_set_record_list"]
                    )

    def get_target_mermaid_diagram(
        self,
        target_product_set: set[BaseProduct] = None,
        target_workflow_set: set[BaseWorkflow] = None,
        target_team_set: set[BaseTeam] = None,
        target_workplace_set: set[BaseWorkplace] = None,
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        link_type_str_workplace_workplace: str = "-->",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of target information.

        Args:
            target_product_set (set[BaseProduct], optional): Target product set. Defaults to None.
            target_workflow_set (set[BaseWorkflow], optional): Target workflow set. Defaults to None.
            target_team_set (set[BaseTeam], optional): Target team set. Defaults to None.
            target_workplace_set (set[BaseWorkplace], optional): Target workplace set. Defaults to None.
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            link_type_str_workplace_workplace (str, optional): Link type string of each workplace and workplace. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        # product, workflow, organization
        for product in target_product_set:
            list_of_lines.extend(
                product.get_mermaid_diagram(
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )
        for workflow in target_workflow_set:
            list_of_lines.extend(
                workflow.get_mermaid_diagram(
                    shape_task=shape_task,
                    print_work_amount_info=print_work_amount_info,
                    print_dependency_type=print_dependency_type,
                    link_type_str=link_type_str_task,
                    subgraph=subgraph_workflow,
                    subgraph_direction=subgraph_direction_workflow,
                )
            )
        for team in target_team_set:
            list_of_lines.extend(
                team.get_mermaid_diagram(
                    print_worker=print_worker,
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_worker,
                    subgraph=subgraph_team,
                    subgraph_direction=subgraph_direction_team,
                )
            )
        for workplace in target_workplace_set:
            list_of_lines.extend(
                workplace.get_mermaid_diagram(
                    print_facility=print_facility,
                    shape_facility=shape_facility,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph_workplace,
                    subgraph_direction=subgraph_direction_workplace,
                )
            )

        # product -> workflow
        for product in target_product_set:
            for c in product.component_set:
                targeted_task_set = self.get_target_task_set(c.targeted_task_id_set)
                for t in targeted_task_set:
                    if t.parent_workflow_id in [w.ID for w in target_workflow_set]:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_set:
                for team_id in t.allocated_team_id_set:
                    if team_id in [team.ID for team in target_team_set]:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_set:
                    if workplace_id in [w.ID for w in target_workplace_set]:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )
        
        # Output the dependencies between workflows                    
        for workflow in target_workflow_set:
            for t in workflow.task_set:
                for input_task_id, dep in t.input_task_id_dependency_set:
                    inp = self.task_dict.get(input_task_id, None)
                    if inp is not None and t.parent_workflow_id != inp.parent_workflow_id:
                        if dep == BaseTaskDependency.FS:
                            dependency_type_mark = "|FS|"
                        elif dep == BaseTaskDependency.SS:
                            dependency_type_mark = "|SS|"
                        elif dep == BaseTaskDependency.FF:
                            dependency_type_mark = "|FF|"
                        elif dep == BaseTaskDependency.SF:
                            dependency_type_mark = "|SF|"
                        if not print_dependency_type:
                            dependency_type_mark = ""
                        list_of_lines.append(f"{inp.ID}{link_type_str_task}{dependency_type_mark}{t.ID}")


        # workplace -> workplace
        for workplace in target_workplace_set:
            for input_workplace_id in workplace.input_workplace_id_set:
                list_of_lines.append(
                    f"{input_workplace_id}{link_type_str_workplace_workplace}{workplace.ID}"
                )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def get_mermaid_diagram(
        self,
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this project.

        Args:
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        return self.get_target_mermaid_diagram(
            target_product_set=self.product_set,
            target_workflow_set=self.workflow_set,
            target_team_set=self.team_set,
            target_workplace_set=self.workplace_set,
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph_product=subgraph_product,
            subgraph_direction_product=subgraph_direction_product,
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph_workflow=subgraph_workflow,
            subgraph_direction_workflow=subgraph_direction_workflow,
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph_team=subgraph_team,
            subgraph_direction_team=subgraph_direction_team,
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph_workplace=subgraph_workplace,
            subgraph_direction_workplace=subgraph_direction_workplace,
            # project
            link_type_str_component_task=link_type_str_component_task,
            link_type_str_worker_task=link_type_str_worker_task,
            link_type_str_facility_task=link_type_str_facility_task,
            link_type_str_worker_facility=link_type_str_worker_facility,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def print_target_mermaid_diagram(
        self,
        target_product_set: set[BaseProduct] = None,
        target_workflow_set: set[BaseWorkflow] = None,
        target_team_set: set[BaseTeam] = None,
        target_workplace_set: set[BaseWorkplace] = None,
        orientations: str = "LR",
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of target information.

        Args:
            target_product_set (set[BaseProduct], optional): Target product set. Defaults to None.
            target_workflow_set (set[BaseWorkflow], optional): Target workflow set. Defaults to None.
            target_team_set (set[BaseTeam], optional): Target team set. Defaults to None.
            target_workplace_set (set[BaseWorkplace], optional): Target workplace set. Defaults to None.
            orientations (str, optional): Orientation of the flowchart. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            None
        """
        if target_product_set is None:
            target_product_set = set()
        if target_workflow_set is None:
            target_workflow_set = set()
        if target_team_set is None:
            target_team_set = set()
        if target_workplace_set is None:
            target_workplace_set = set()
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_mermaid_diagram(
            target_product_set=target_product_set,
            target_workflow_set=target_workflow_set,
            target_team_set=target_team_set,
            target_workplace_set=target_workplace_set,
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph_product=subgraph_product,
            subgraph_direction_product=subgraph_direction_product,
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph_workflow=subgraph_workflow,
            subgraph_direction_workflow=subgraph_direction_workflow,
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph_team=subgraph_team,
            subgraph_direction_team=subgraph_direction_team,
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph_workplace=subgraph_workplace,
            subgraph_direction_workplace=subgraph_direction_workplace,
            # project
            link_type_str_component_task=link_type_str_component_task,
            link_type_str_worker_task=link_type_str_worker_task,
            link_type_str_facility_task=link_type_str_facility_task,
            link_type_str_worker_facility=link_type_str_worker_facility,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this project.

        Args:
            orientations (str, optional): Orientation of the flowchart. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            None
        """
        self.print_target_mermaid_diagram(
            target_product_set=self.product_set,
            target_workflow_set=self.workflow_set,
            target_team_set=self.team_set,
            target_workplace_set=self.workplace_set,
            orientations=orientations,
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph_product=subgraph_product,
            subgraph_direction_product=subgraph_direction_product,
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph_workflow=subgraph_workflow,
            subgraph_direction_workflow=subgraph_direction_workflow,
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph_team=subgraph_team,
            subgraph_direction_team=subgraph_direction_team,
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph_workplace=subgraph_workplace,
            subgraph_direction_workplace=subgraph_direction_workplace,
            # project
            link_type_str_component_task=link_type_str_component_task,
            link_type_str_worker_task=link_type_str_worker_task,
            link_type_str_facility_task=link_type_str_facility_task,
            link_type_str_worker_facility=link_type_str_worker_facility,
        )

    def get_target_product_related_mermaid_diagram(
        self,
        target_product_set: set[BaseProduct],
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of product-related information for the specified products.

        Args:
            target_product_set (set[BaseProduct]): Target product set.
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for product in target_product_set:
            list_of_lines.extend(
                product.get_mermaid_diagram(
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )

        target_workflow_set = set()
        target_task_set = set()
        for product in target_product_set:
            for component in product.component_set:
                targeted_task_set = self.get_target_task_set(
                    component.targeted_task_id_set
                )
                for task in targeted_task_set:
                    target_task_set.add(task)
                    target_workflow = self.workflow_dict.get(
                        task.parent_workflow_id, None
                    )
                    target_workflow_set.add(target_workflow)

        for workflow in target_workflow_set:
            list_of_lines.extend(
                workflow.get_target_task_mermaid_diagram(
                    target_task_set,
                    shape_task=shape_task,
                    print_work_amount_info=print_work_amount_info,
                    print_dependency_type=print_dependency_type,
                    link_type_str=link_type_str_task,
                    subgraph=subgraph_workflow,
                    subgraph_direction=subgraph_direction_workflow,
                )
            )

        target_team_set = set()
        target_worker_set = set()
        target_workplace_set = set()
        target_facility_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                for team_id in task.allocated_team_id_set:
                    target_team = self.team_dict.get(team_id, None)
                    target_team_set.add(target_team)
                    for worker in target_team.worker_set:
                        target_worker_set.add(worker)
                for workplace_id in task.allocated_workplace_id_set:
                    target_workplace = self.workplace_dict.get(workplace_id, None)
                    target_workplace_set.add(target_workplace)
                    for facility in target_workplace.facility_set:
                        target_facility_set.add(facility)

        for team in target_team_set:
            list_of_lines.extend(
                team.get_target_worker_mermaid_diagram(
                    target_worker_set,
                    print_worker=print_worker,
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_worker,
                    subgraph=subgraph_team,
                    subgraph_direction=subgraph_direction_team,
                )
            )
        for workplace in target_workplace_set:
            list_of_lines.extend(
                workplace.get_target_facility_mermaid_diagram(
                    target_facility_set,
                    print_facility=print_facility,
                    shape_facility=shape_facility,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph_workplace,
                    subgraph_direction=subgraph_direction_workplace,
                )
            )

        # product -> workflow
        target_workflow_id_set = {wf.ID for wf in target_workflow_set}
        for product in target_product_set:
            for c in product.component_set:
                targeted_task_set = self.get_target_task_set(c.targeted_task_id_set)
                for t in targeted_task_set:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_set:
                for team_id in t.allocated_team_id_set:
                    if team_id in {team.ID for team in target_team_set}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_set:
                    if workplace_id in {w.ID for w in target_workplace_set}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_product_related_mermaid_diagram(
        self,
        target_product_set: set[BaseProduct],
        orientations: str = "LR",
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of product-related information for the specified products.

        Args:
            target_product_set (set[BaseProduct]): Target product set.
            orientations (str, optional): Orientation of the flowchart. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_product_related_mermaid_diagram(
            target_product_set=target_product_set,
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph_product=subgraph_product,
            subgraph_direction_product=subgraph_direction_product,
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph_workflow=subgraph_workflow,
            subgraph_direction_workflow=subgraph_direction_workflow,
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph_team=subgraph_team,
            subgraph_direction_team=subgraph_direction_team,
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph_workplace=subgraph_workplace,
            subgraph_direction_workplace=subgraph_direction_workplace,
            # project
            link_type_str_component_task=link_type_str_component_task,
            link_type_str_worker_task=link_type_str_worker_task,
            link_type_str_facility_task=link_type_str_facility_task,
            link_type_str_worker_facility=link_type_str_worker_facility,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_target_team_related_mermaid_diagram(
        self,
        target_team_set: set[BaseTeam],
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of team-related information for the specified teams.

        Args:
            target_team_set (set[BaseTeam]): Target team set.
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for team in target_team_set:
            list_of_lines.extend(
                team.get_mermaid_diagram(
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_worker,
                    subgraph=subgraph_team,
                    subgraph_direction=subgraph_direction_team,
                )
            )

        target_workflow_set = set()
        target_task_set = set()
        for team in target_team_set:
            targeted_task_set = self.get_target_task_set(team.targeted_task_id_set)
            for task in targeted_task_set:
                target_task_set.add(task)
                target_workflow = self.workflow_dict.get(task.parent_workflow_id, None)
                target_workflow_set.add(target_workflow)

        for workflow in target_workflow_set:
            list_of_lines.extend(
                workflow.get_target_task_mermaid_diagram(
                    target_task_set,
                    shape_task=shape_task,
                    print_work_amount_info=print_work_amount_info,
                    print_dependency_type=print_dependency_type,
                    link_type_str=link_type_str_task,
                    subgraph=subgraph_workflow,
                    subgraph_direction=subgraph_direction_workflow,
                )
            )

        target_workplace_set = set()
        target_facility_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                for workplace_id in task.allocated_workplace_id_set:
                    target_workplace = self.workplace_dict.get(workplace_id, None)
                    target_workplace_set.add(target_workplace)
                    for facility in target_workplace.facility_set:
                        target_facility_set.add(facility)

        for workplace in target_workplace_set:
            list_of_lines.extend(
                workplace.get_target_facility_mermaid_diagram(
                    target_facility_set,
                    print_facility=print_facility,
                    shape_facility=shape_facility,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph_workplace,
                    subgraph_direction=subgraph_direction_workplace,
                )
            )

        target_product_set = set()
        target_component_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                if task.target_component_id is not None:
                    target_component = self.component_dict.get(
                        task.target_component_id, None
                    )
                    target_component_set.add(target_component)
                    target_product = self.product_dict.get(
                        target_component.parent_product_id, None
                    )
                    target_product_set.add(target_product)

        for product in target_product_set:
            list_of_lines.extend(
                product.get_target_component_mermaid_diagram(
                    target_component_set=target_component_set,
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )

        # product -> workflow
        target_workflow_id_set = {wf.ID for wf in target_workflow_set}
        for product in target_product_set:
            for c in product.component_set:
                targeted_task_set = self.get_target_task_set(c.targeted_task_id_set)
                for t in targeted_task_set:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_set:
                for team_id in t.allocated_team_id_set:
                    if team_id in {team.ID for team in target_team_set}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_set:
                    if workplace_id in {w.ID for w in target_workplace_set}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_team_related_mermaid_diagram(
        self,
        target_team_set: set[BaseTeam],
        orientations: str = "LR",
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of team-related information for the specified teams.

        Args:
            target_team_set (set[BaseTeam]): Target team set.
            orientations (str, optional): Orientation of the flowchart. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_team_related_mermaid_diagram(
            target_team_set=target_team_set,
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph_product=subgraph_product,
            subgraph_direction_product=subgraph_direction_product,
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph_workflow=subgraph_workflow,
            subgraph_direction_workflow=subgraph_direction_workflow,
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph_team=subgraph_team,
            subgraph_direction_team=subgraph_direction_team,
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph_workplace=subgraph_workplace,
            subgraph_direction_workplace=subgraph_direction_workplace,
            # project
            link_type_str_component_task=link_type_str_component_task,
            link_type_str_worker_task=link_type_str_worker_task,
            link_type_str_facility_task=link_type_str_facility_task,
            link_type_str_worker_facility=link_type_str_worker_facility,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_target_workplace_related_mermaid_diagram(
        self,
        target_workplace_set: set[BaseWorkplace],
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of workplace-related information for the specified workplaces.

        Args:
            target_workplace_set (set[BaseWorkplace]): Target workplace set.
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for workplace in target_workplace_set:
            list_of_lines.extend(
                workplace.get_mermaid_diagram(
                    print_facility=print_facility,
                    shape_facility=shape_facility,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph_workplace,
                    subgraph_direction=subgraph_direction_workplace,
                )
            )

        target_workflow_set = set()
        target_task_set = set()
        for workplace in target_workplace_set:
            targeted_task_set = self.get_target_task_set(workplace.targeted_task_id_set)
            for task in targeted_task_set:
                target_task_set.add(task)
                target_workflow = self.workflow_dict.get(task.parent_workflow_id, None)
                target_workflow_set.add(target_workflow)

        for workflow in target_workflow_set:
            list_of_lines.extend(
                workflow.get_target_task_mermaid_diagram(
                    target_task_set,
                    shape_task=shape_task,
                    print_work_amount_info=print_work_amount_info,
                    print_dependency_type=print_dependency_type,
                    link_type_str=link_type_str_task,
                    subgraph=subgraph_workflow,
                    subgraph_direction=subgraph_direction_workflow,
                )
            )

        target_team_set = set()
        target_worker_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                for team_id in task.allocated_team_id_set:
                    target_team = self.team_dict.get(team_id, None)
                    if target_team is not None:
                        target_team_set.add(target_team)
                        for worker in target_team.worker_set:
                            target_worker_set.add(worker)

        for team in target_team_set:
            list_of_lines.extend(
                team.get_target_worker_mermaid_diagram(
                    target_worker_set,
                    print_worker=print_worker,
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph_workplace,
                    subgraph_direction=subgraph_direction_workplace,
                )
            )

        target_product_set = set()
        target_component_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                if task.target_component_id is not None:
                    target_component = self.component_dict.get(
                        task.target_component_id, None
                    )
                    target_component_set.add(target_component)
                    target_product = self.product_dict.get(
                        target_component.parent_product_id, None
                    )
                    target_product_set.add(target_product)

        for product in target_product_set:
            list_of_lines.extend(
                product.get_target_component_mermaid_diagram(
                    target_component_set=target_component_set,
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )

        # product -> workflow
        target_workflow_id_set = {wf.ID for wf in target_workflow_set}
        for product in target_product_set:
            for c in product.component_set:
                targeted_task_set = self.get_target_task_set(c.targeted_task_id_set)
                for t in targeted_task_set:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_set:
                for team_id in t.allocated_team_id_set:
                    if team_id in {team.ID for team in target_team_set}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_set:
                    if workplace_id in {w.ID for w in target_workplace_set}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_workplace_related_mermaid_diagram(
        self,
        target_workplace_set: set[BaseWorkplace],
        orientations: str = "LR",
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of workplace-related information for the specified workplaces.

        Args:
            target_workplace_set (set[BaseWorkplace]): Target workplace set.
            orientations (str, optional): Orientation of the flowchart. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_workplace_related_mermaid_diagram(
            target_workplace_set=target_workplace_set,
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph_product=subgraph_product,
            subgraph_direction_product=subgraph_direction_product,
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph_workflow=subgraph_workflow,
            subgraph_direction_workflow=subgraph_direction_workflow,
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph_team=subgraph_team,
            subgraph_direction_team=subgraph_direction_team,
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph_workplace=subgraph_workplace,
            subgraph_direction_workplace=subgraph_direction_workplace,
            # project
            link_type_str_component_task=link_type_str_component_task,
            link_type_str_worker_task=link_type_str_worker_task,
            link_type_str_facility_task=link_type_str_facility_task,
            link_type_str_worker_facility=link_type_str_worker_facility,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_target_workflow_related_mermaid_diagram(
        self,
        target_workflow_set: set[BaseWorkflow],
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of workflow-related information for the specified workflows.

        Args:
            target_workflow_set (set[BaseWorkflow]): Target workflow set.
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for workflow in target_workflow_set:
            list_of_lines.extend(
                workflow.get_mermaid_diagram(
                    shape_task=shape_task,
                    print_work_amount_info=print_work_amount_info,
                    print_dependency_type=print_dependency_type,
                    link_type_str=link_type_str_task,
                    subgraph=subgraph_workflow,
                    subgraph_direction=subgraph_direction_workflow,
                )
            )

        target_team_set = set()
        target_worker_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                for team_id in task.allocated_team_id_set:
                    target_team = self.team_dict.get(team_id, None)
                    if target_team is not None:
                        target_team_set.add(target_team)
                        for worker in target_team.worker_set:
                            target_worker_set.add(worker)

        for team in target_team_set:
            list_of_lines.extend(
                team.get_target_worker_mermaid_diagram(
                    target_worker_set,
                    print_worker=print_worker,
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph_workplace,
                    subgraph_direction=subgraph_direction_workplace,
                )
            )

        target_workplace_set = set()
        target_facility_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                for workplace_id in task.allocated_workplace_id_set:
                    target_workplace = self.workplace_dict.get(workplace_id, None)
                    target_workplace_set.add(target_workplace)
                    for facility in target_workplace.facility_set:
                        target_facility_set.add(facility)

        for workplace in target_workplace_set:
            list_of_lines.extend(
                workplace.get_target_facility_mermaid_diagram(
                    target_facility_set,
                    print_facility=print_facility,
                    shape_facility=shape_facility,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph_workplace,
                    subgraph_direction=subgraph_direction_workplace,
                )
            )

        target_product_set = set()
        target_component_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_set:
                if task.target_component_id is not None:
                    target_component = self.component_dict.get(
                        task.target_component_id, None
                    )
                    target_component_set.add(target_component)
                    target_product = self.product_dict.get(
                        target_component.parent_product_id, None
                    )
                    target_product_set.add(target_product)

        for product in target_product_set:
            list_of_lines.extend(
                product.get_target_component_mermaid_diagram(
                    target_component_set=target_component_set,
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )

        # product -> workflow
        target_workflow_id_set = {wf.ID for wf in target_workflow_set}
        for product in target_product_set:
            for c in product.component_set:
                targeted_task_set = self.get_target_task_set(c.targeted_task_id_set)
                for t in targeted_task_set:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_set:
                for team_id in t.allocated_team_id_set:
                    if team_id in {team.ID for team in target_team_set}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_set:
                    if workplace_id in {w.ID for w in target_workplace_set}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_workflow_related_mermaid_diagram(
        self,
        target_workflow_set: set[BaseWorkflow],
        orientations: str = "LR",
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph_product: bool = True,
        subgraph_direction_product: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph_workflow: bool = True,
        subgraph_direction_workflow: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph_team: bool = True,
        subgraph_direction_team: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph_workplace: bool = True,
        subgraph_direction_workplace: str = "LR",
        # project
        link_type_str_component_task: str = "-.-",
        link_type_str_worker_task: str = "-.-",
        link_type_str_facility_task: str = "-.-",
        link_type_str_worker_facility: str = "-.-",
        subgraph: bool = False,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of workflow-related information for the specified workflows.

        Args:
            target_workflow_set (set[BaseWorkflow]): Target workflow set.
            orientations (str, optional): Orientation of the flowchart. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph_product (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction_product (str, optional): Direction of product subgraph. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph_workflow (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction_workflow (str, optional): Direction of workflow subgraph. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph_team (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction_team (str, optional): Direction of team subgraph. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph_workplace (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction_workplace (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_component_task (str, optional): Link type string of each component and task. Defaults to "-.-".
            link_type_str_worker_task (str, optional): Link type string of each worker and task. Defaults to "-.-".
            link_type_str_facility_task (str, optional): Link type string of each facility and task. Defaults to "-.-".
            link_type_str_worker_facility (str, optional): Link type string of each worker and facility. Defaults to "-.-".
            subgraph (bool, optional): Whether to use subgraph for the whole diagram. Defaults to False.
            subgraph_direction (str, optional): Direction of the main subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_workflow_related_mermaid_diagram(
            target_workflow_set=target_workflow_set,
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph_product=subgraph_product,
            subgraph_direction_product=subgraph_direction_product,
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph_workflow=subgraph_workflow,
            subgraph_direction_workflow=subgraph_direction_workflow,
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph_team=subgraph_team,
            subgraph_direction_team=subgraph_direction_team,
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph_workplace=subgraph_workplace,
            subgraph_direction_workplace=subgraph_direction_workplace,
            # project
            link_type_str_component_task=link_type_str_component_task,
            link_type_str_worker_task=link_type_str_worker_task,
            link_type_str_facility_task=link_type_str_facility_task,
            link_type_str_worker_facility=link_type_str_worker_facility,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_all_product_mermaid_diagram(
        self,
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of all products.

        Args:
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction (str, optional): Direction of product subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        for product in self.product_set:
            list_of_lines.extend(
                product.get_mermaid_diagram(
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph,
                    subgraph_direction=subgraph_direction,
                )
            )
        return list_of_lines

    def print_all_product_mermaid_diagram(
        self,
        orientations: str = "LR",
        # product
        shape_component: str = "odd",
        link_type_str_component: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of all products.

        Args:
            orientations (str): Orientation of the flowchart. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram for components. Defaults to "odd".
            link_type_str_component (str, optional): Link type string of each component. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for products. Defaults to True.
            subgraph_direction (str, optional): Direction of product subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_all_product_mermaid_diagram(
            # product
            shape_component=shape_component,
            link_type_str_component=link_type_str_component,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_all_workflow_mermaid_diagram(
        self,
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of all workflows.

        Args:
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction (str, optional): Direction of workflow subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        for workflow in self.workflow_set:
            list_of_lines.extend(
                workflow.get_mermaid_diagram(
                    shape_task=shape_task,
                    print_work_amount_info=print_work_amount_info,
                    print_dependency_type=print_dependency_type,
                    link_type_str=link_type_str_task,
                    subgraph=subgraph,
                    subgraph_direction=subgraph_direction,
                )
            )
        return list_of_lines

    def print_all_workflow_mermaid_diagram(
        self,
        orientations: str = "LR",
        # workflow
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        print_dependency_type: bool = False,
        link_type_str_task: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of all workflows.

        Args:
            orientations (str): Orientation of the flowchart. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram for tasks. Defaults to "rect".
            print_work_amount_info (bool, optional): Whether to print work amount info. Defaults to True.
            print_dependency_type (bool, optional): Whether to print dependency type info. Defaults to False.
            link_type_str_task (str, optional): Link type string of each task. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for workflows. Defaults to True.
            subgraph_direction (str, optional): Direction of workflow subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_all_workflow_mermaid_diagram(
            # workflow
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            print_dependency_type=print_dependency_type,
            link_type_str_task=link_type_str_task,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_all_team_mermaid_diagram(
        self,
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of all teams.

        Args:
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction (str, optional): Direction of team subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        for team in self.team_set:
            list_of_lines.extend(
                team.get_mermaid_diagram(
                    print_worker=print_worker,
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_worker,
                    subgraph=subgraph,
                    subgraph_direction=subgraph_direction,
                )
            )
        return list_of_lines

    def print_all_team_mermaid_diagram(
        self,
        orientations: str = "LR",
        # team
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str_worker: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of all teams.

        Args:
            orientations (str): Orientation of the flowchart. Defaults to "LR".
            print_worker (bool, optional): Whether to print workers. Defaults to True.
            shape_worker (str, optional): Shape of mermaid diagram for workers. Defaults to "stadium".
            link_type_str_worker (str, optional): Link type string of each worker. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for teams. Defaults to True.
            subgraph_direction (str, optional): Direction of team subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_all_team_mermaid_diagram(
            # team
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str_worker=link_type_str_worker,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_all_workplace_mermaid_diagram(
        self,
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
        link_type_str_workplace_workplace: str = "-->",
    ):
        """
        Get mermaid diagram of all workplaces.

        Args:
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction (str, optional): Direction of workplace subgraph. Defaults to "LR".
            link_type_str_workplace_workplace (str, optional): Link type string of each workplace. Defaults to "-->".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        for workplace in self.workplace_set:
            list_of_lines.extend(
                workplace.get_mermaid_diagram(
                    print_facility=print_facility,
                    shape_facility=shape_facility,
                    link_type_str=link_type_str_facility,
                    subgraph=subgraph,
                    subgraph_direction=subgraph_direction,
                )
            )
        # workplace -> workplace
        for workplace in self.workplace_set:
            for input_workplace_id in workplace.input_workplace_id_set:
                list_of_lines.append(
                    f"{input_workplace_id}{link_type_str_workplace_workplace}{workplace.ID}"
                )

        return list_of_lines

    def print_all_workplace_mermaid_diagram(
        self,
        orientations: str = "LR",
        # workplace
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str_facility: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of all workplaces.

        Args:
            orientations (str): Orientation of the flowchart. Defaults to "LR".
            print_facility (bool, optional): Whether to print facilities. Defaults to True.
            shape_facility (str, optional): Shape of mermaid diagram for facilities. Defaults to "stadium".
            link_type_str_facility (str, optional): Link type string of each facility. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph for workplaces. Defaults to True.
            subgraph_direction (str, optional): Direction of workplace subgraph. Defaults to "LR".

        Returns:
            None
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_all_workplace_mermaid_diagram(
            # workplace
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str_facility=link_type_str_facility,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_all_product_gantt_mermaid(
        self,
        target_product_id_order_list: list[str] = None,
        target_component_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
    ):
        """
        Get mermaid Gantt diagram lines for all products.

        Args:
            target_product_id_order_list (list[str], optional): List of target product IDs in the desired order. Defaults to None.
            target_component_id_order_list (list[str], optional): List of target component IDs in the desired order. Defaults to None.
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.

        Returns:
            list[str]: List of lines for mermaid Gantt diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        target_instance_list = self.product_set
        if target_product_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.product_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_product_id_order_list
                if tid in id_to_instance
            ]

        list_of_lines = []
        for product in target_instance_list:
            list_of_lines.extend(
                product.get_gantt_mermaid(
                    target_id_order_list=target_component_id_order_list,
                    section=section,
                    range_time=range_time,
                    view_ready=view_ready,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_all_product_gantt_mermaid(
        self,
        target_product_id_order_list: list[str] = None,
        target_component_id_order_list: list[str] = None,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        view_ready: bool = False,
    ):
        """
        Print mermaid Gantt diagram for all products.

        Args:
            target_product_id_order_list (list[str], optional): List of target product IDs in the desired order. Defaults to None.
            target_component_id_order_list (list[str], optional): List of target component IDs in the desired order. Defaults to None.
            date_format (str, optional): Date format for the diagram. Defaults to "X".
            axis_format (str, optional): Axis format for the diagram. Defaults to "%s".
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.

        Returns:
            None
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_product_gantt_mermaid(
            target_product_id_order_list=target_product_id_order_list,
            target_component_id_order_list=target_component_id_order_list,
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
            view_ready=view_ready,
        )
        print(*list_of_lines, sep="\n")

    def get_all_workflow_gantt_mermaid(
        self,
        target_workflow_id_order_list: list[str] = None,
        target_task_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        view_ready: bool = False,
    ):
        """
        Get mermaid Gantt diagram lines for all workflows.

        Args:
            target_workflow_id_order_list (list[str], optional): List of target workflow IDs in the desired order. Defaults to None.
            target_task_id_order_list (list[str], optional): List of target task IDs in the desired order. Defaults to None.
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.

        Returns:
            list[str]: List of lines for mermaid Gantt diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        target_instance_list = self.workflow_set
        if target_workflow_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.workflow_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_workflow_id_order_list
                if tid in id_to_instance
            ]

        list_of_lines = []
        for workflow in target_instance_list:
            list_of_lines.extend(
                workflow.get_gantt_mermaid(
                    target_id_order_list=target_task_id_order_list,
                    section=section,
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                    view_ready=view_ready,
                )
            )
        return list_of_lines

    def print_all_workflow_gantt_mermaid(
        self,
        target_workflow_id_order_list: list[str] = None,
        target_task_id_order_list: list[str] = None,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        view_ready: bool = False,
    ):
        """
        Print mermaid Gantt diagram for all workflows.

        Args:
            target_workflow_id_order_list (list[str], optional): List of target workflow IDs in the desired order. Defaults to None.
            target_task_id_order_list (list[str], optional): List of target task IDs in the desired order. Defaults to None.
            date_format (str, optional): Date format for the diagram. Defaults to "X".
            axis_format (str, optional): Axis format for the diagram. Defaults to "%s".
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.

        Returns:
            None
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_workflow_gantt_mermaid(
            target_workflow_id_order_list=target_workflow_id_order_list,
            target_task_id_order_list=target_task_id_order_list,
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
            view_ready=view_ready,
        )
        print(*list_of_lines, sep="\n")

    def get_all_team_gantt_mermaid(
        self,
        target_team_id_order_list: list[str] = None,
        target_worker_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        view_ready: bool = False,
    ):
        """
        Get mermaid Gantt diagram lines for all teams.

        Args:
            target_team_id_order_list (list[str], optional): List of target team IDs in the desired order. Defaults to None.
            target_worker_id_order_list (list[str], optional): List of target worker IDs in the desired order. Defaults to None.
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.

        Returns:
            list[str]: List of lines for mermaid Gantt diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        target_instance_list = self.team_set
        if target_team_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.team_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_team_id_order_list
                if tid in id_to_instance
            ]

        list_of_lines = []
        for team in target_instance_list:
            list_of_lines.extend(
                team.get_gantt_mermaid(
                    target_id_order_list=target_worker_id_order_list,
                    section=section,
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                    view_ready=view_ready,
                )
            )
        return list_of_lines

    def print_all_team_gantt_mermaid(
        self,
        target_team_id_order_list: list[str] = None,
        target_worker_id_order_list: list[str] = None,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        view_ready: bool = False,
    ):
        """
        Print mermaid Gantt diagram for all teams.

        Args:
            target_team_id_order_list (list[str], optional): List of target team IDs in the desired order. Defaults to None.
            target_worker_id_order_list (list[str], optional): List of target worker IDs in the desired order. Defaults to None.
            date_format (str, optional): Date format for the diagram. Defaults to "X".
            axis_format (str, optional): Axis format for the diagram. Defaults to "%s".
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.

        Returns:
            None
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_team_gantt_mermaid(
            target_team_id_order_list=target_team_id_order_list,
            target_worker_id_order_list=target_worker_id_order_list,
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
            view_ready=view_ready,
        )
        print(*list_of_lines, sep="\n")

    def get_all_workplace_gantt_mermaid(
        self,
        target_workplace_id_order_list: list[str] = None,
        target_facility_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        view_ready: bool = False,
    ):
        """
        Get mermaid Gantt diagram lines for all workplaces.

        Args:
            target_workplace_id_order_list (list[str], optional): List of target workplace IDs in the desired order. Defaults to None.
            target_facility_id_order_list (list[str], optional): List of target facility IDs in the desired order. Defaults to None.
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.

        Returns:
            list[str]: List of lines for mermaid Gantt diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        target_instance_list = self.workplace_set
        if target_workplace_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.workplace_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_workplace_id_order_list
                if tid in id_to_instance
            ]

        list_of_lines = []
        for workplace in target_instance_list:
            list_of_lines.extend(
                workplace.get_gantt_mermaid(
                    target_id_order_list=target_facility_id_order_list,
                    section=section,
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                    view_ready=view_ready,
                )
            )
        return list_of_lines

    def print_all_workplace_gantt_mermaid(
        self,
        target_workplace_id_order_list: list[str] = None,
        target_facility_id_order_list: list[str] = None,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        view_ready: bool = False,
    ):
        """
        Print mermaid Gantt diagram for all workplaces.

        Args:
            target_workplace_id_order_list (list[str], optional): List of target workplace IDs in the desired order. Defaults to None.
            target_facility_id_order_list (list[str], optional): List of target facility IDs in the desired order. Defaults to None.
            date_format (str, optional): Date format for the diagram. Defaults to "X".
            axis_format (str, optional): Axis format for the diagram. Defaults to "%s".
            section (bool, optional): Whether to use sections in the diagram. Defaults to True.
            range_time (tuple[int, int], optional): Time range for the diagram. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): Whether to include detailed information. Defaults to False.
            view_ready (bool, optional): Whether to include ready tasks. Defaults to False.

        Returns:
            None
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_workplace_gantt_mermaid(
            target_workplace_id_order_list=target_workplace_id_order_list,
            target_facility_id_order_list=target_facility_id_order_list,
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
            view_ready=view_ready,
        )
        print(*list_of_lines, sep="\n")
