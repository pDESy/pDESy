#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_project."""

import datetime
import itertools
import json
import sys
import uuid
import warnings
from abc import ABCMeta
from enum import IntEnum

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
    including product, workflow, team_list and workplace_list.
    This class will be used as template.

    Args:
        name (str, optional):
            Basic parameter.
            Name of this project.
            Defaults to None -> "Project".
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None -> str(uuid.uuid4()).
        init_datetime (datetime.datetime, optional):
            Start datetime of project.
            Defaults to None -> datetime.datetime.now().
        unit_timedelta (datetime.timedelta, optional):
            Unit time of simulation.
            Defaults to None -> datetime.timedelta(minutes=1).
        absence_time_list (List[int], optional):
            List of absence time of simulation.
            Defaults to None -> [].
        perform_auto_task_while_absence_time (bool, optional):
            Perform auto_task while absence time or not.
            Defaults to None -> False.
            This means that auto_task does not be performed while absence time.
        product_list (List[BaseProduct], optional):
            List of BaseProduct in this project.
            Defaults to None -> [].
        workflow_list (List[BaseWorkflow], optional):
            List of BaseWorkflow in this project.
            Defaults to None -> [].
        team_list (List[BaseTeam], optional):
            List of BaseTeam in this project.
            Defaults to None -> [].
        workplace_list (List[BaseWorkplace], optional):
            List of BaseWorkplace in this project.
            Defaults to None -> [].
        time (int, optional):
            Simulation time executing this method.
            Defaults to 0.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this project's cost in simulation.
            Defaults to None -> [].
        simulation_mode (SimulationMode, optional):
            Basic variable.
            Simulation mode.
            Defaults to None -> SimulationMode.NONE
        status (BaseProjectStatus, optional):
            Basic variable.
            Project status.
            Defaults to None -> BaseProjectStatus.NONE
    """

    def __init__(
        self,
        # Basic parameters
        name=None,
        ID=None,
        init_datetime=None,
        unit_timedelta=None,
        absence_time_list=None,
        perform_auto_task_while_absence_time=None,
        # Basic variables
        product_list=None,
        workflow_list=None,
        team_list=None,
        workplace_list=None,
        time=0,
        cost_list=None,
        simulation_mode=None,
        status=None,
    ):
        """init."""
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
        self.product_list = product_list if product_list is not None else []
        self.workflow_list = workflow_list if workflow_list is not None else []
        self.team_list = team_list if team_list is not None else []
        self.workplace_list = workplace_list if workplace_list is not None else []

        if time != int(0):
            self.time = time
        else:
            self.time = int(0)

        if cost_list is not None:
            self.cost_list = cost_list
        else:
            self.cost_list = []

        if simulation_mode is not None:
            self.simulation_mode = simulation_mode
        else:
            self.simulation_mode = SimulationMode.NONE

        if status is not None:
            self.status = status
        else:
            self.status = BaseProjectStatus.NONE

    def __str__(self):
        """str.

        Returns:
            str: time and name lists of product, workflow.
        """
        return (
            f"TIME: {self.time}\n"
            f"PRODUCT\n{self.product_list}\n\n"
            f"Workflow\n{self.workflow_list}\n\n"
            f"TEAM\n{self.team_list}\n\n"
            f"WORKPLACE\n{self.workplace_list}"
        )

    def append_product(self, product):
        """
        Append product to this project.

        Args:
            product (BaseProduct): Product to append.
        """
        if not isinstance(product, BaseProduct):
            raise TypeError("product should be BaseProduct")
        self.product_list.append(product)

    def extend_product_list(self, product_list):
        """
        Extend product list to this project.

        Args:
            product_list (List[BaseProduct]): List of products to extend.
        """
        if not all(isinstance(product, BaseProduct) for product in product_list):
            raise TypeError("All items in product_list should be BaseProduct")
        self.product_list.extend(product_list)

    def append_workflow(self, workflow):
        """
        Append workflow to this project.

        Args:
            workflow (BaseWorkflow): Workflow to append.
        """
        if not isinstance(workflow, BaseWorkflow):
            raise TypeError("workflow should be BaseWorkflow")
        self.workflow_list.append(workflow)

    def extend_workflow_list(self, workflow_list):
        """
        Extend workflow list to this project.

        Args:
            workflow_list (List[BaseWorkflow]): List of workflows to extend.
        """
        if not all(isinstance(workflow, BaseWorkflow) for workflow in workflow_list):
            raise TypeError("All items in workflow_list should be BaseWorkflow")
        self.workflow_list.extend(workflow_list)

    def append_team(self, team):
        """
        Append team to this project.

        Args:
            team (BaseTeam): Team to append.
        """
        if not isinstance(team, BaseTeam):
            raise TypeError("team should be BaseTeam")
        self.team_list.append(team)

    def extend_team_list(self, team_list):
        """
        Extend team list to this project.

        Args:
            team_list (List[BaseTeam]): List of teams to extend.
        """
        if not all(isinstance(team, BaseTeam) for team in team_list):
            raise TypeError("All items in team_list should be BaseTeam")
        self.team_list.extend(team_list)

    def append_workplace(self, workplace):
        """
        Append workplace to this project.

        Args:
            workplace (BaseWorkplace): Workplace to append.
        """
        if not isinstance(workplace, BaseWorkplace):
            raise TypeError("workplace should be BaseWorkplace")
        self.workplace_list.append(workplace)

    def extend_workplace_list(self, workplace_list):
        """
        Extend workplace list to this project.

        Args:
            workplace_list (List[BaseWorkplace]): List of workplaces to extend.
        """
        if not all(
            isinstance(workplace, BaseWorkplace) for workplace in workplace_list
        ):
            raise TypeError("All items in workplace_list should be BaseWorkplace")
        self.workplace_list.extend(workplace_list)

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseProject.

        If `state_info` is True, the attributes of this class are not initialized.

        If `log_info` is True, the following attributes are initialized.

          - `time`
          - `cost_list`
          - `simulation_mode`
          - `status`

        BaseProduct in `product`, BaseWorkflow in `workflow`, BaseTeam in `team_list`,
        and BaseWorkplace in `workplace_list` are initialized.

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaults to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """

        if log_info:
            self.time = 0
            self.cost_list = []
            self.simulation_mode = SimulationMode.NONE
            self.status = BaseProjectStatus.NONE

        # product should be initialized after initializing workflow
        for workflow in self.workflow_list:
            workflow.initialize(state_info=state_info, log_info=log_info)
            self.check_state_workflow(workflow, BaseTaskState.READY)
        for product in self.product_list:
            product.initialize(state_info=state_info, log_info=log_info)
            for component in product.component_list:
                self.check_state_component(component)
        for team in self.team_list:
            team.initialize(state_info=state_info, log_info=log_info)
        for workplace in self.workplace_list:
            workplace.initialize(state_info=state_info, log_info=log_info)

    def check_state_component(self, component: BaseComponent):
        """
        Check the state of a component from its task state.

        Args:
            component (BaseComponent): The component to check.
        """
        targeted_task_list = self.get_target_task_list(component.targeted_task_id_list)
        self.__check_ready_component(component, targeted_task_list)
        self.__check_working_component(component, targeted_task_list)
        self.__check_finished_component(component, targeted_task_list)

    def __check_ready_component(self, component: BaseComponent, targeted_task_list):
        if not all(map(lambda t: t.state == BaseTaskState.WORKING, targeted_task_list)):
            if not all(
                map(
                    lambda t: t.state == BaseTaskState.FINISHED,
                    targeted_task_list,
                )
            ):
                if any(
                    map(
                        lambda t: t.state == BaseTaskState.READY,
                        targeted_task_list,
                    )
                ):
                    component.state = BaseComponentState.READY

    def __check_working_component(self, component: BaseComponent, targeted_task_list):
        if any(map(lambda t: t.state == BaseTaskState.WORKING, targeted_task_list)):
            component.state = BaseComponentState.WORKING

    def __check_finished_component(self, component: BaseComponent, targeted_task_list):
        if all(
            map(
                lambda t: t.state == BaseTaskState.FINISHED,
                targeted_task_list,
            )
        ):
            component.state = BaseComponentState.FINISHED

    def simulate(
        self,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        error_tol=1e-10,
        absence_time_list=None,
        perform_auto_task_while_absence_time=False,
        initialize_state_info=True,
        initialize_log_info=True,
        max_time=10000,
        unit_time=1,
    ):
        """
        Simulate this BaseProject.

        Args:
            task_priority_rule (TaskPriorityRule, optional):
                Task priority rule for simulation.
                Defaults to TaskPriorityRule.TSLACK.
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            absence_time_list (List[int], optional):
                List of absence time in simulation.
                Defaults to None -> []. This means workers work every time.
            perform_auto_task_while_absence_time (bool, optional):
                Perform auto_task while absence time or not.
                Defaults to False.
                This means that auto_task does not be performed while absence time.
            initialize_state_info (bool, optional):
                Whether initializing state info of this project or not.
                Defaults to True.
            initialize_log_info (bool, optional):
                Whether initializing log info of this project or not.
                Defaults to True.
            max_time (int, optional):
                Max time of simulation.
                Defaults to 10000.
            unit_time (int, optional):
                Unit time of simulation.
                Defaults to 1.
        """
        if absence_time_list is None:
            absence_time_list = []

        self.initialize(state_info=initialize_state_info, log_info=initialize_log_info)

        self.simulation_mode = SimulationMode.FORWARD

        self.absence_time_list = absence_time_list

        self.perform_auto_task_while_absence_time = perform_auto_task_while_absence_time

        while True:
            # 0. Update status
            self.__update()

            # 1. Check finished or not
            all_task_list = self.get_all_task_list()
            state_list = list(map(lambda task: task.state, all_task_list))
            if all(state == BaseTaskState.FINISHED for state in state_list):
                self.status = BaseProjectStatus.FINISHED_SUCCESS
                return

            # Time over check
            if self.time >= max_time:
                self.status = BaseProjectStatus.FINISHED_FAILURE
                warnings.warn(
                    "Time Over! Please check your simulation model or increase max_time value"
                )
                return

            # check now is business time or not
            working = True

            if self.time in absence_time_list:
                working = False

            # check and update state of each worker and facility
            if working:
                for team in self.team_list:
                    team.check_update_state_from_absence_time_list(self.time)
                for workplace in self.workplace_list:
                    workplace.check_update_state_from_absence_time_list(self.time)
            else:
                for team in self.team_list:
                    team.set_absence_state_to_all_workers()
                for workplace in self.workplace_list:
                    workplace.set_absence_state_to_all_facilities()

            # 2. Allocate free workers to READY tasks
            if working:
                self.__allocate(
                    task_priority_rule=task_priority_rule,
                )

            # Update state of task newly allocated workers and facilities (READY -> WORKING)
            for workflow in self.workflow_list:
                self.check_state_workflow(workflow, BaseTaskState.WORKING)
            for product in self.product_list:
                # product should be checked after checking workflow state
                for component in product.component_list:
                    self.check_state_component(component)

            # 3. Pay cost to all workers and facilities in this time
            cost_this_time = 0.0

            add_zero_to_all_workers = False
            add_zero_to_all_facilities = False
            if not working:
                add_zero_to_all_workers = True
                add_zero_to_all_facilities = True

            for team in self.team_list:
                cost_this_time += team.add_labor_cost(
                    only_working=True,
                    add_zero_to_all_workers=add_zero_to_all_workers,
                )
            for workplace in self.workplace_list:
                cost_this_time += workplace.add_labor_cost(
                    only_working=True,
                    add_zero_to_all_facilities=add_zero_to_all_facilities,
                )
            self.cost_list.append(cost_this_time)

            # 4, Perform
            if working:
                self.__perform(only_auto_task=False)
            elif perform_auto_task_while_absence_time:
                self.__perform(only_auto_task=True)

            # 5. Record
            self.__record(working=working)

            # 6. Update time
            self.time = self.time + unit_time

    def backward_simulate(
        self,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        error_tol=1e-10,
        absence_time_list=None,
        perform_auto_task_while_absence_time=False,
        initialize_state_info=True,
        initialize_log_info=True,
        max_time=10000,
        unit_time=1,
        considering_due_time_of_tail_tasks=False,
        reverse_log_information=True,
    ):
        """
        Simulate this BaseProject by using backward simulation.

        Args:
            task_performed_mode (str, optional):
                Mode of performed task in simulation.
                pDESy has the following options of this mode in simulation.
                - multi-workers
                Defaults to "multi-workers".
            task_priority_rule (TaskPriorityRule, optional):
                Task priority rule for simulation.
                Defaults to TaskPriorityRule.TSLACK.
            worker_priority_rule (ResourcePriorityRule, optional):
                Worker priority rule for simulation.
                Defaults to ResourcePriorityRule.SSP.
            facility_priority_rule (ResourcePriorityRule, optional):
                Task priority rule for simulation.
                Defaults to TaskPriorityRule.TSLACK.
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            absence_time_list (List[int], optional):
                List of absence time in simulation.
                Defaults to None -> []. This means workers work every time.
            perform_auto_task_while_absence_time (bool, optional):
                Perform auto_task while absence time or not.
                Defaults to False.
                This means that auto_task does not be performed while absence time.
            initialize_state_info (bool, optional):
                Whether initializing state info of this project or not.
                Defaults to True.
            initialize_log_info (bool, optional):
                Whether initializing log info of this project or not.
                Defaults to True.
            max_time (int, optional):
                Max time of simulation.
                Defaults to 10000.
            unit_time (int, optional):
                Unit time of simulation.
                Defaults to 1.
            considering_due_time_of_tail_tasks (bool, optional):
                Consider due_time of tail tasks or not.
                Default to False.
            reverse_time_information (bool, optional):
                Reverse information of simulation log or not.
                Defaults to True.

        Note:
            This function is only for research and still in progress.
            Especially, this function is not suitable for simulation considering rework.
        """
        if absence_time_list is None:
            absence_time_list = []

        for workflow in self.workflow_list:
            workflow.reverse_dependencies()

        # reverse_dependency of workplace
        for workplace in self.workplace_list:
            workplace.dummy_output_workplace_list = workplace.input_workplace_list
            workplace.dummy_input_workplace_list = workplace.output_workplace_list
        for workplace in self.workplace_list:
            workplace.output_workplace_list = workplace.dummy_output_workplace_list
            workplace.input_workplace_list = workplace.dummy_input_workplace_list
            del (
                workplace.dummy_output_workplace_list,
                workplace.dummy_input_workplace_list,
            )

        auto_task_removing_after_simulation = set()
        try:
            if considering_due_time_of_tail_tasks:
                # Add dummy task for considering the difference of due_time
                for workflow in self.workflow_list:
                    tail_task_list = list(
                        filter(
                            lambda task: len(task.input_task_id_dependency_list) == 0,
                            workflow.task_list,
                        )
                    )
                    max_due_time = max([task.due_time for task in tail_task_list])
                    for tail_task in tail_task_list:
                        if tail_task.due_time < max_due_time:
                            auto_task = BaseTask(
                                "auto",
                                auto_task=True,
                                default_work_amount=max_due_time - tail_task.due_time,
                            )
                            tail_task.append_input_task_dependency(
                                auto_task, task_dependency_mode=BaseTaskDependency.FS
                            )
                            auto_task_removing_after_simulation.add(auto_task)
                            workflow.task_list.append(auto_task)

            self.simulate(
                task_priority_rule=task_priority_rule,
                error_tol=error_tol,
                absence_time_list=absence_time_list,
                perform_auto_task_while_absence_time=perform_auto_task_while_absence_time,
                initialize_log_info=initialize_log_info,
                initialize_state_info=initialize_state_info,
                max_time=max_time,
                unit_time=unit_time,
            )

        finally:
            self.simulation_mode = SimulationMode.BACKWARD
            for auto_task in auto_task_removing_after_simulation:
                auto_task_output_task_list = [
                    (task, dependency)
                    for task in self.get_all_task_list()
                    for input_task_id, dependency in task.input_task_id_dependency_list
                    if input_task_id == auto_task.ID
                ]
                for task, dependency in auto_task_output_task_list:
                    task.input_task_id_dependency_list.remove(
                        [auto_task.ID, dependency]
                    )
                for workflow in self.workflow_list:
                    if auto_task in workflow.task_list:
                        workflow.task_list.remove(auto_task)
            if reverse_log_information:
                self.reverse_log_information()

            for workflow in self.workflow_list:
                workflow.reverse_dependencies()

            # reverse_dependency of workplace
            for workplace in self.workplace_list:
                workplace.dummy_output_workplace_list = workplace.input_workplace_list
                workplace.dummy_input_workplace_list = workplace.output_workplace_list
            for workplace in self.workplace_list:
                workplace.output_workplace_list = workplace.dummy_output_workplace_list
                workplace.input_workplace_list = workplace.dummy_input_workplace_list
                del (
                    workplace.dummy_output_workplace_list,
                    workplace.dummy_input_workplace_list,
                )

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.cost_list = self.cost_list[::-1]
        total_step_length = len(self.cost_list)
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
        for product in self.product_list:
            product.reverse_log_information()
        for workflow in self.workflow_list:
            workflow.reverse_log_information()
        for team in self.team_list:
            team.reverse_log_information()
        for workplace in self.workplace_list:
            workplace.reverse_log_information()

    def __perform(self, only_auto_task=False, seed=None, increase_component_error=1.0):
        for workflow in self.workflow_list:

            for task in workflow.task_list:
                if only_auto_task:
                    if task.auto_task:
                        self.__perform_task(task, seed=seed)
                else:
                    self.__perform_task(
                        task,
                        seed=seed,
                        increase_component_error=increase_component_error,
                    )

    def __perform_task(self, task: BaseTask, seed=None, increase_component_error=1.0):
        if task.state == BaseTaskState.WORKING:
            work_amount_progress = 0.0
            no_error_probability = 1.0
            if task.auto_task:
                work_amount_progress = task.work_amount_progress_of_unit_step_time
            else:
                if task.need_facility:
                    min_length = min(
                        len(task.allocated_worker_id_list),
                        len(task.allocated_facility_id_list),
                    )
                    for i in range(min_length):
                        worker_id = task.allocated_worker_id_list[i]
                        worker = next(
                            (
                                w
                                for w in self.get_all_worker_list()
                                if w.ID == worker_id
                            ),
                            None,
                        )
                        w_progress = self.get_work_amount_skill_progress(
                            worker, task.name, seed=seed
                        )
                        facility_id = task.allocated_facility_id_list[i]
                        facility = next(
                            (
                                f
                                for f in self.get_all_facility_list()
                                if f.ID == facility_id
                            ),
                            None,
                        )
                        f_progress = self.get_work_amount_skill_progress(
                            facility, task.name, seed=seed
                        )
                        work_amount_progress += w_progress * f_progress
                        no_error_probability = (
                            no_error_probability
                            - worker.get_quality_skill_point(task.name, seed=seed)
                        )
                else:
                    for worker_id in task.allocated_worker_id_list:
                        worker = next(
                            (
                                w
                                for w in self.get_all_worker_list()
                                if w.ID == worker_id
                            ),
                            None,
                        )
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
                target_component = next(
                    (
                        component
                        for component in self.get_all_component_list()
                        if component.ID == task.target_component_id
                    ),
                    None,
                )
                target_component.update_error_value(
                    no_error_probability, increase_component_error, seed=seed
                )

    def get_work_amount_skill_progress(self, resource, task_name, seed=None):
        """
        Get progress of workamount by his or her contribution in this time.

        If he or she has multiple tasks in this time,
        progress `p_r(t)` is defined as follows:

        p_r(t)={ps_r(t)}/{N_r(t)}

        - `ps_r(t)`: progress if he or she has only this task in this time
        - `N_r(t)`: Number of allocated tasks to him or her in this time


        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Countermeasures against numerical error.
                Defaults to 1e-10.

        Returns:
            float: Progress of workamount by his or her contribution in this time
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
        sum_of_working_task_in_this_time = sum(
            map(
                lambda task: task.state == BaseTaskState.WORKING
                or task.state == BaseTaskState.WORKING_ADDITIONALLY,
                resource.assigned_task_list,
            )
        )
        return base_progress / float(sum_of_working_task_in_this_time)

    def __record(self, working=True):
        for workflow in self.workflow_list:
            workflow.record(working)
        for team in self.team_list:
            team.record_assigned_task_id()
            team.record_all_worker_state(working=working)
        for workplace in self.workplace_list:
            workplace.record_assigned_task_id()
            workplace.record_placed_component_id()
            workplace.record_all_facility_state(working=working)
        for product in self.product_list:
            product.record(working)

    def __update(self):
        for workflow in self.workflow_list:
            self.check_state_workflow(workflow, BaseTaskState.FINISHED)
        for product in self.product_list:
            # product should be checked after checking workflow state
            for component in product.component_list:
                self.check_state_component(component)
        self.__check_removing_placed_workplace()
        for workflow in self.workflow_list:
            self.check_state_workflow(workflow, BaseTaskState.READY)
        for product in self.product_list:
            # product should be checked after checking workflow state
            for component in product.component_list:
                self.check_state_component(component)
        for workflow in self.workflow_list:
            workflow.update_pert_data(self.time)

    def __check_removing_placed_workplace(self):
        """
        Check removing this product from placed_workplace or not.
        If all tasks of this product is finished, this product will be removed automatically.
        """

        all_components = [
            component
            for product in self.product_list
            for component in product.component_list
        ]

        all_children_components_id = set()
        for c in all_components:
            all_children_components_id.update(c.child_component_id_list)

        top_component_list = [
            component
            for component in all_components
            if component.ID not in all_children_components_id
        ]

        removing_placed_workplace_component_set = set()
        for c in top_component_list:
            targeted_task_list = self.get_target_task_list(c.targeted_task_id_list)
            all_finished_flag = all(
                map(
                    lambda task: task.state == BaseTaskState.FINISHED,
                    targeted_task_list,
                )
            )
            if all_finished_flag and c.placed_workplace is not None:
                removing_placed_workplace_component_set.add(c)

        for c in removing_placed_workplace_component_set:
            self.remove_component_on_workplace(c, c.placed_workplace)
            self.set_component_on_workplace(c, None)

    def __is_allocated_worker(self, worker, task):
        team = list(filter(lambda team: team.ID == worker.team_id, self.team_list))[0]
        targeted_task_list = self.get_target_task_list(team.targeted_task_id_list)
        return task in targeted_task_list

    def __is_allocated_facility(self, facility, task):
        workplace = list(
            filter(
                lambda workplace: workplace.ID == facility.workplace_id,
                self.workplace_list,
            )
        )[0]
        targeted_task_list = self.get_target_task_list(workplace.targeted_task_id_list)
        return task in targeted_task_list

    def __allocate(
        self,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
    ):
        all_task_list = self.get_all_task_list()

        # 1. Get ready task and free workers and facilities
        ready_and_working_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.READY
                or task.state == BaseTaskState.WORKING,
                all_task_list,
            )
        )

        worker_list = list(
            itertools.chain.from_iterable(
                list(map(lambda team: team.worker_list, self.team_list))
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
        target_workplace_id_list = [wp.ID for wp in self.workplace_list]

        for task in ready_and_working_task_list:
            if task.target_component_id is not None:
                # 3-1. Set target component of workplace if target component is ready
                component = next(
                    (
                        component
                        for component in self.get_all_component_list()
                        if component.ID == task.target_component_id
                    ),
                    None,
                )
                if self.is_ready_component(component):
                    candidate_workplace_list = [
                        workplace
                        for workplace in self.workplace_list
                        if workplace.ID in task.allocated_workplace_id_list
                    ]
                    candidate_workplace_list = sort_workplace_list(
                        candidate_workplace_list,
                        task.workplace_priority_rule,
                        name=task.name,
                    )
                    for workplace in candidate_workplace_list:
                        if workplace.ID in target_workplace_id_list:
                            conveyor_condition = True
                            if len(workplace.input_workplace_list) > 0:
                                if component.placed_workplace is None:
                                    conveyor_condition = True
                                elif not (
                                    component.placed_workplace
                                    in workplace.input_workplace_list
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
                                and workplace.can_put(component)
                                and skill_flag
                            ):
                                # 3-1-1. move ready_component
                                pre_workplace = component.placed_workplace

                                # 3-1-1-1. remove
                                if pre_workplace is None:
                                    for child_c_id in component.child_component_id_list:
                                        child_c = next(
                                            filter(
                                                lambda c, child_c_id=child_c_id: c.ID
                                                == child_c_id,
                                                self.get_all_component_list(),
                                            )
                                        )
                                        wp = child_c.placed_workplace
                                        if wp is not None:
                                            for c_wp in wp.placed_component_list:
                                                if any(
                                                    child_id == task.target_component_id
                                                    for child_id in c_wp.child_component_id_list
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
                    target_component = next(
                        (
                            component
                            for component in self.get_all_component_list()
                            if component.ID == task.target_component_id
                        ),
                        None,
                    )
                    placed_workplace = target_component.placed_workplace

                    if placed_workplace is not None:
                        free_facility_list = list(
                            filter(
                                lambda facility: facility.state
                                == BaseFacilityState.FREE,
                                placed_workplace.facility_list,
                            )
                        )

                        # Facility sorting
                        free_facility_list = sort_facility_list(
                            free_facility_list, task.facility_priority_rule
                        )

                        # candidate facilities
                        allocating_facilities = list(
                            filter(
                                lambda facility, task=task: facility.has_workamount_skill(
                                    task.name
                                )
                                and self.__is_allocated_facility(facility, task),
                                free_facility_list,
                            )
                        )

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
                                task.allocated_worker_id_list.append(worker.ID)
                                worker.assigned_task_list.append(task)
                                task.allocated_facility_id_list.append(facility.ID)
                                facility.assigned_task_list.append(task)
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
                            task.allocated_worker_id_list.append(worker.ID)
                            worker.assigned_task_list.append(task)
                            free_worker_list = [
                                w for w in free_worker_list if w.ID != worker.ID
                            ]

    def check_state_workflow(self, workflow: BaseWorkflow, state: BaseTaskState):
        """
        Check state of all BaseTasks in task_list.

        Args:
            state (BaseTaskState):
                Check target state.
                Search and update all tasks which can change only target state.
        """
        if state == BaseTaskState.READY:
            self.__check_ready_workflow(workflow)
        elif state == BaseTaskState.WORKING:
            self.__check_working_workflow(workflow)
        elif state == BaseTaskState.FINISHED:
            self.__check_finished_workflow(workflow)

    def __check_ready_workflow(self, workflow: BaseWorkflow):
        none_task_set = set(
            filter(lambda task: task.state == BaseTaskState.NONE, workflow.task_list)
        )
        for none_task in none_task_set:
            input_task_id_dependency_list = none_task.input_task_id_dependency_list

            # check READY condition by each dependency
            # FS: if input task is finished
            # SS: if input task is started
            # ...or this is head task
            ready = True
            for input_task_id, dependency in input_task_id_dependency_list:
                input_task = next(
                    filter(
                        lambda task, input_task_id=input_task_id: task.ID
                        == input_task_id,
                        workflow.task_list,
                    ),
                    None,
                )
                if dependency == BaseTaskDependency.FS:
                    if input_task.state == BaseTaskState.FINISHED:
                        ready = True
                    else:
                        ready = False
                        break
                elif dependency == BaseTaskDependency.SS:
                    if input_task.state == BaseTaskState.WORKING:
                        ready = True
                    else:
                        ready = False
                        break
                elif dependency == BaseTaskDependency.SF:
                    pass
                elif dependency == BaseTaskDependency.FF:
                    pass
            if ready:
                none_task.state = BaseTaskState.READY

    def __check_working_workflow(self, workflow: BaseWorkflow):
        ready_and_assigned_task_set = set(
            filter(
                lambda task: task.state == BaseTaskState.READY
                and len(task.allocated_worker_id_list) > 0,
                workflow.task_list,
            )
        )

        ready_auto_task_set = set(
            filter(
                lambda task: task.state == BaseTaskState.READY and task.auto_task,
                workflow.task_list,
            )
        )

        working_and_assigned_task_set = set(
            filter(
                lambda task: task.state == BaseTaskState.WORKING
                and len(task.allocated_worker_id_list) > 0,
                workflow.task_list,
            )
        )

        target_task_set = set()
        target_task_set.update(ready_and_assigned_task_set)
        target_task_set.update(ready_auto_task_set)
        target_task_set.update(working_and_assigned_task_set)

        for task in target_task_set:
            if task.state == BaseTaskState.READY:
                task.state = BaseTaskState.WORKING
                for worker_id in task.allocated_worker_id_list:
                    worker = next(
                        filter(
                            lambda w, worker_id=worker_id: w.ID == worker_id,
                            self.get_all_worker_list(),
                        ),
                        None,
                    )
                    if worker:
                        worker.state = BaseWorkerState.WORKING
                        # worker.assigned_task_list.append(task)
                if task.need_facility:
                    for facility_id in task.allocated_facility_id_list:
                        facility = next(
                            filter(
                                lambda f, facility_id=facility_id: f.ID == facility_id,
                                self.get_all_facility_list(),
                            ),
                            None,
                        )
                        if facility:
                            facility.state = BaseFacilityState.WORKING
                            # facility.assigned_task_list.append(task)

            elif task.state == BaseTaskState.WORKING:
                for worker_id in task.allocated_worker_id_list:
                    worker = next(
                        filter(
                            lambda w, worker_id=worker_id: w.ID == worker_id,
                            self.get_all_worker_list(),
                        ),
                        None,
                    )
                    if worker:
                        if worker.state == BaseWorkerState.FREE:
                            worker.state = BaseWorkerState.WORKING
                            # worker.assigned_task_list.append(task)
                    if task.need_facility:
                        for facility_id in task.allocated_facility_id_list:
                            facility = next(
                                filter(
                                    lambda f, facility_id=facility_id: f.ID
                                    == facility_id,
                                    self.get_all_facility_list(),
                                ),
                                None,
                            )
                            if facility and facility.state == BaseFacilityState.FREE:
                                facility.state = BaseFacilityState.WORKING
                                # facility.assigned_task_list.append(task)

    def __check_finished_workflow(self, workflow: BaseWorkflow, error_tol=1e-10):
        working_and_zero_task_set = set(
            filter(
                lambda task: task.state == BaseTaskState.WORKING
                and task.remaining_work_amount < 0.0 + error_tol,
                workflow.task_list,
            )
        )
        for task in working_and_zero_task_set:
            # check FINISH condition by each dependency
            # SF: if input task is working
            # FF: if input task is finished
            finished = True
            for input_task_id, dependency in task.input_task_id_dependency_list:
                input_task = next(
                    filter(
                        lambda task, input_task_id=input_task_id: task.ID
                        == input_task_id,
                        workflow.task_list,
                    ),
                    None,
                )
                if dependency == BaseTaskDependency.FS:
                    pass
                elif dependency == BaseTaskDependency.SS:
                    pass
                elif dependency == BaseTaskDependency.SF:
                    if input_task.state == BaseTaskState.WORKING:
                        finished = True
                    else:
                        finished = False
                        break
                elif dependency == BaseTaskDependency.FF:
                    if input_task.state == BaseTaskState.FINISHED:
                        finished = True
                    else:
                        finished = False
                        break
            if finished:
                task.state = BaseTaskState.FINISHED
                task.remaining_work_amount = 0.0

                for worker_id in task.allocated_worker_id_list:
                    worker = next(
                        filter(
                            lambda w, worker_id=worker_id: w.ID == worker_id,
                            self.get_all_worker_list(),
                        ),
                        None,
                    )
                    if worker:
                        if len(worker.assigned_task_list) > 0 and all(
                            list(
                                map(
                                    lambda task: task.state == BaseTaskState.FINISHED,
                                    worker.assigned_task_list,
                                )
                            )
                        ):
                            worker.state = BaseWorkerState.FREE
                            worker.assigned_task_list.remove(task)
                task.allocated_worker_id_list = []

                if task.need_facility:
                    for facility_id in task.allocated_facility_id_list:
                        facility = next(
                            filter(
                                lambda f, facility_id=facility_id: f.ID == facility_id,
                                self.get_all_facility_list(),
                            ),
                            None,
                        )
                        if facility:
                            if len(facility.assigned_task_list) > 0 and all(
                                list(
                                    map(
                                        lambda task: task.state
                                        == BaseTaskState.FINISHED,
                                        facility.assigned_task_list,
                                    )
                                )
                            ):
                                facility.state = BaseFacilityState.FREE
                                facility.assigned_task_list.remove(task)
                    task.allocated_facility_id_list = []

    def can_add_resources_to_task(self, task: BaseTask, worker=None, facility=None):
        """
        Judge whether target task can be assigned another resources or not.

        Args:
            task (BaseTask):
                Target task for checking.
            worker (BaseWorker):
                Target worker for allocating.
                Defaults to None.
            facility (BaseFacility):
                Target facility for allocating.
                Defaults to None.
        """
        if task.state == BaseTaskState.NONE:
            return False
        elif task.state == BaseTaskState.FINISHED:
            return False

        # True if none of the allocated resources have solo_working attribute True.
        for w_id in task.allocated_worker_id_list:
            w = next((w for w in self.get_all_worker_list() if w.ID == w_id), None)
            if w is not None:
                if w.solo_working:
                    return False
                for f_id in task.allocated_facility_id_list:
                    f = next(
                        (f for f in self.get_all_facility_list() if f.ID == f_id),
                        None,
                    )
                    if f.solo_working:
                        return False

        # solo_working check
        if worker is not None:
            if worker.solo_working:
                if len(task.allocated_worker_id_list) > 0:
                    return False
        if facility is not None:
            if facility.solo_working:
                if len(task.allocated_facility_id_list) > 0:
                    return False

        # Fixing allocating worker/facility id list check
        if worker is not None:
            if task.fixing_allocating_worker_id_list is not None:
                if worker.ID not in task.fixing_allocating_worker_id_list:
                    return False
        if facility is not None:
            if task.fixing_allocating_facility_id_list is not None:
                if facility.ID not in task.fixing_allocating_facility_id_list:
                    return False

        # multi-task in one facility check
        if facility is not None:
            if len(facility.assigned_task_list) > 0:
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
        Check READY component or not.

        READY component is defined by satisfying the following conditions:

          - All tasks are not NONE.
          - There is no WORKING task in this component.
          - The states of append_targeted_task includes READY.

        Returns:
            bool: this component is READY or not.
        """
        targeted_task_list = self.get_target_task_list(component.targeted_task_id_list)
        all_none_flag = all(
            [task.state == BaseTaskState.NONE for task in targeted_task_list]
        )

        any_working_flag = any(
            [task.state == BaseTaskState.WORKING for task in targeted_task_list]
        )

        any_ready_flag = any(
            [task.state == BaseTaskState.READY for task in targeted_task_list]
        )

        all_finished_flag = all(
            [task.state == BaseTaskState.FINISHED for task in targeted_task_list]
        )

        if all_finished_flag:
            return False

        if not all_none_flag and (not any_working_flag) and any_ready_flag:
            return True

        return False

    def remove_absence_time_list(self):
        """
        Remove record information on `absence_time_list`.
        """
        for product in self.product_list:
            product.remove_absence_time_list(self.absence_time_list)
        for workflow in self.workflow_list:
            workflow.remove_absence_time_list(self.absence_time_list)
        for team in self.team_list:
            team.remove_absence_time_list(self.absence_time_list)
        for workplace in self.workplace_list:
            workplace.remove_absence_time_list(self.absence_time_list)

        for step_time in sorted(self.absence_time_list, reverse=True):
            if step_time < len(self.cost_list):
                self.cost_list.pop(step_time)

        self.time = self.time - len(self.absence_time_list)
        self.absence_time_list = []

    def insert_absence_time_list(self, absence_time_list):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        # duplication check
        new_absence_time_list = []
        for time in absence_time_list:
            if time not in self.absence_time_list:
                new_absence_time_list.append(time)
        for product in self.product_list:
            product.insert_absence_time_list(new_absence_time_list)
        for workflow in self.workflow_list:
            workflow.insert_absence_time_list(new_absence_time_list)
        for team in self.team_list:
            team.insert_absence_time_list(absence_time_list)
        for workplace in self.workplace_list:
            workplace.insert_absence_time_list(absence_time_list)

        for step_time in sorted(new_absence_time_list):
            self.cost_list.insert(step_time, 0.0)

        self.time = self.time + len(new_absence_time_list)
        self.absence_time_list.extend(new_absence_time_list)

    def set_last_datetime(
        self, last_datetime, unit_timedelta=None, set_init_datetime=True
    ):
        """
        Set the last datetime to project simulation result.
        This means that calculate the init datetime of this project considering `last_datetime`.

        Args:
            last_datetime (datetime.datetime):
                Last datetime of project.
            unit_timedelta (datetime.timedelta, optional):
                Unit time of simulation.
                Defaults to None -> self.unit_timedelta
            set_init_datetime (bool, optional):
                Set calculated init_datetime or not in this project.
                Defaults to True.
        Returns:
            datetime.datetime: Init datetime of project considering the `last_datetime`
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
        self, target_component, placed_workplace, set_to_all_children=True
    ):
        """
        Set the `placed_workplace`.

        Args:
            target_component (BaseComponent):
                Target component to set `placed_workplace`.
            placed_workplace (BaseWorkplace):
                Workplace placed in this component
            set_to_all_children (bool):
                If True, set placed_workplace to all children components
                Default to True
        """
        target_component.placed_workplace = placed_workplace
        if placed_workplace is not None:
            if target_component not in placed_workplace.placed_component_list:
                placed_workplace.placed_component_list.append(target_component)

        if set_to_all_children:
            for child_c_id in target_component.child_component_id_list:
                child_c = next(
                    filter(
                        lambda c, child_c_id=child_c_id: c.ID == child_c_id,
                        self.get_all_component_list(),
                    )
                )
                self.set_component_on_workplace(
                    child_c, placed_workplace, set_to_all_children=set_to_all_children
                )

    def remove_component_on_workplace(
        self, target_component, placed_workplace, set_to_all_children=True
    ):
        """
        Remove the `placed_workplace`.

        Args:
            placed_component (BaseComponent):
                Component which places to this workplace
            remove_to_all_children_components (bool):
                If True, remove `placed_workplace` to all children components
                Default to True
        """
        placed_workplace.placed_component_list.remove(target_component)

        if set_to_all_children:
            for child_c_id in target_component.child_component_id_list:
                child_c = next(
                    filter(
                        lambda c, child_c_id=child_c_id: c.ID == child_c_id,
                        self.get_all_component_list(),
                    )
                )
                self.remove_component_on_workplace(
                    child_c,
                    placed_workplace,
                    set_to_all_children=set_to_all_children,
                )

    def get_all_task_list(self):
        """
        Get all task list in this project.

        Returns:
            List[BaseTask]: All task list in this project.
        """
        task_list = []
        for workflow in self.workflow_list:
            task_list.extend(workflow.task_list)
        return task_list

    def get_target_task_list(self, target_task_id_list):
        """
        Get tasks by their IDs.

        Args:
            target_task_id_list (list[str]):
                List of task IDs to filter.
        Returns:
            list[BaseTask]: List of tasks matching the provided IDs.
        """
        all_task_list = self.get_all_task_list()
        target_task_list = [
            task for task in all_task_list if task.ID in target_task_id_list
        ]
        return target_task_list

    def get_all_component_list(self):
        """
        Get all component list in this project.

        Returns:
            List[BaseComponent]: All component list in this project.
        """
        component_list = []
        for product in self.product_list:
            component_list.extend(product.component_list)
        return component_list

    def get_all_id_name_dict(self):
        """
        Get a flat dictionary of all id-name mappings in this project.

        Returns:
            dict: Flat dictionary containing all {id: name} mappings.
        """
        result = {}

        # BaseProduct
        for product in self.product_list:
            result[product.ID] = product.name

        # BaseComponent
        for component in self.get_all_component_list():
            result[component.ID] = component.name

        # BaseWorkflow
        for workflow in self.workflow_list:
            result[workflow.ID] = workflow.name

        # BaseTask
        for task in self.get_all_task_list():
            result[task.ID] = task.name

        # BaseTeam
        for team in self.team_list:
            result[team.ID] = team.name

        # BaseWorker
        for worker in self.get_all_worker_list():
            result[worker.ID] = worker.name

        # BaseWorkplace
        for workplace in self.workplace_list:
            result[workplace.ID] = workplace.name

        # BaseFacility
        for facility in self.get_all_facility_list():
            result[facility.ID] = facility.name

        return result

    def create_gantt_plotly(
        self,
        title="Gantt Chart",
        colors=None,
        index_col=None,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=False,
        show_colorbar=True,
        finish_margin=1.0,
        save_fig_path=None,
    ):
        """
        Create Gantt chart by plotly.

        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            title (str, optional):
                Title of Gantt chart.
                Defaults to "Gantt Chart".
            colors (Dict[str, str], optional):
                Color setting of plotly Gantt chart.
                Defaults to None -> dict(Component="rgb(246, 37, 105)",Task="rgb(146, 237, 5)"
                ,Worker="rgb(46, 137, 205)"
                ,Facility="rgb(46, 137, 205)",).
            index_col (str, optional):
                index_col of plotly Gantt chart.
                Defaults to None -> "Type".
            showgrid_x (bool, optional):
                showgrid_x of plotly Gantt chart.
                Defaults to True.
            showgrid_y (bool, optional):
                showgrid_y of plotly Gantt chart.
                Defaults to True.
            group_tasks (bool, optional):
                group_tasks of plotly Gantt chart.
                Defaults to True.
            show_colorbar (bool, optional):
                show_colorbar of plotly Gantt chart.
                Defaults to True.
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a gantt chart
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
        for product in self.product_list:
            df.extend(
                product.create_data_for_gantt_plotly(
                    self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
                )
            )
        for workflow in self.workflow_list:
            df.extend(
                workflow.create_data_for_gantt_plotly(
                    self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
                )
            )
        for team in self.team_list:
            df.extend(
                team.create_data_for_gantt_plotly(
                    self.init_datetime,
                    self.unit_timedelta,
                    finish_margin=finish_margin,
                    # view_ready=view_ready,
                    # view_absence=view_absence,
                )
            )
        for workplace in self.workplace_list:
            df.extend(
                workplace.create_data_for_gantt_plotly(
                    self.init_datetime,
                    self.unit_timedelta,
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

    def get_networkx_graph(self, view_workers=False, view_facilities=False):
        """
        Get the information of networkx graph.

        Args:
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
        Returns:
            G: networkx.Digraph()
        """

        g_product = nx.DiGraph()
        for product in self.product_list:
            g_product = nx.compose(g_product, product.get_networkx_graph())

        g_workflow = nx.DiGraph()
        for workflow in self.workflow_list:
            g_workflow = nx.compose(g_workflow, workflow.get_networkx_graph())

        g_team = nx.DiGraph()
        # 1. add all nodes
        for team in self.team_list:
            g_team.add_node(team)
        # 2. add all edges
        for team in self.team_list:
            if team.parent_team_id is not None:
                parent_team = next(
                    (team for team in self.team_list if team.ID == team.parent_team_id),
                    None,
                )
                g_team.add_edge(parent_team, team)
        if view_workers:
            for team in self.team_list:
                for w in team.worker_list:
                    g_team.add_node(w)
                    g_team.add_edge(team, w)

        g_workplace = nx.DiGraph()
        # 1. add all nodes
        for workplace in self.workplace_list:
            g_workplace.add_node(workplace)
        # 2. add all edges
        for workplace in self.workplace_list:
            if workplace.parent_workplace_id is not None:
                parent_workplace = next(
                    (
                        workplace
                        for workplace in self.workplace_list
                        if workplace.ID == workplace.parent_workplace_id
                    ),
                    None,
                )
                g_workplace.add_edge(parent_workplace, workplace)
        if view_facilities:
            for workplace in self.workplace_list:
                for w in workplace.facility_list:
                    g_workplace.add_node(w)
                    g_workplace.add_edge(workplace, w)

        g = nx.compose_all([g_product, g_workflow, g_team, g_workplace])

        # add edge between product and workflow
        for product in self.product_list:
            for c in product.component_list:
                targeted_task_list = self.get_target_task_list(c.targeted_task_id_list)
                for task in targeted_task_list:
                    g.add_edge(c, task)

        # add edge between workflow and team
        for team in self.team_list:
            targeted_task_list = self.get_target_task_list(team.targeted_task_id_list)
            for task in targeted_task_list:
                g.add_edge(team, task)

        if view_workers:
            for team in self.team_list:
                for w in team.worker_list:
                    # g.add_node(w)
                    g.add_edge(team, w)

        # add edge between workflow and workplace
        for workplace in self.workplace_list:
            targeted_task_list = self.get_target_task_list(
                workplace.targeted_task_id_list
            )
            for task in targeted_task_list:
                g.add_edge(workplace, task)

        if view_facilities:
            for workplace in self.workplace_list:
                for w in workplace.facility_list:
                    # g.add_node(w)
                    g.add_edge(workplace, w)

        return g

    def draw_networkx(
        self,
        g=None,
        pos=None,
        arrows=True,
        component_node_color="#FF6600",
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        view_facilities=False,
        workplace_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        figsize=None,
        dpi=100.0,
        save_fig_path=None,
        **kwargs,
    ):
        """
        Draw networkx.

        Args:
            g (networkx.SDigraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(g).
            arrows (bool, optional):
                Digraph or Graph(no arrows).
                Defaults to True.
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
            workplace_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            figsize ((float, float), optional):
                Width, height in inches.
                Default to None -> [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.
            **kwargs:
                another networkx settings.
        Returns:
            figure: Figure for a network
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
            nodelist=self.get_all_component_list(),
            node_color=component_node_color,
            **kwargs,
        )
        # Workflow
        normal_task_list = [
            task for task in self.get_all_task_list() if not task.auto_task
        ]
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=normal_task_list,
            node_color=task_node_color,
            **kwargs,
        )
        auto_task_list = [task for task in self.get_all_task_list() if task.auto_task]
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=auto_task_list,
            node_color=auto_task_node_color,
        )
        # Team
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=self.team_list,
            node_color=team_node_color,
            **kwargs,
        )
        if view_workers:
            worker_list = []
            for team in self.team_list:
                worker_list.extend(team.worker_list)

            nx.draw_networkx_nodes(
                g,
                pos,
                nodelist=worker_list,
                node_color=worker_node_color,
                **kwargs,
            )

        # Workplace
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=self.workplace_list,
            node_color=workplace_node_color,
            **kwargs,
        )
        if view_facilities:
            facility_list = []
            for workplace in self.workplace_list:
                facility_list.extend(workplace.facility_list)

            nx.draw_networkx_nodes(
                g,
                pos,
                nodelist=facility_list,
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
        g=None,
        pos=None,
        node_size=20,
        component_node_color="#FF6600",
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        workplace_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        view_facilities=False,
    ):
        """
        Get nodes and edges information of plotly network.

        Args:
            g (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(g).
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            workplace_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.

        Returns:
            component_node_trace: component nodes information of plotly network.
            task_node_trace: task nodes information of plotly network.
            auto_task_node_trace: auto task nodes information of plotly network.
            team_node_trace: team nodes information of plotly network.
            worker_node_trace: worker nodes information of plotly network.
            workplace_node_trace: Workplace Node information of plotly network.
            facility_node_trace: Facility Node information of plotly network.
            edge_trace: Edge information of plotly network.
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
        g=None,
        pos=None,
        title="Project",
        node_size=20,
        component_node_color="#FF6600",
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        workplace_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        view_facilities=False,
        save_fig_path=None,
    ):
        """
        Draw plotly network.

        Args:
            g (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(g).
            title (str, optional):
                Figure title of this network.
                Defaults to "Project".
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            workplace_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network
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

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time`.

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        for product in self.product_list:
            product.print_log(target_step_time)
        for workflow in self.workflow_list:
            workflow.print_log(target_step_time)
        for team in self.team_list:
            team.print_log(target_step_time)
        for workplace in self.workplace_list:
            workplace.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """
        Print all log in chronological order.
        """
        if self.simulation_mode == SimulationMode.BACKWARD:
            backward = True
        elif self.simulation_mode == SimulationMode.FORWARD:
            backward = False

        for workflow in self.workflow_list:
            if len(workflow.task_list) > 0:
                for t in range(len(workflow.task_list[0].state_record_list)):
                    print("TIME: ", t)
                    if backward:
                        t = len(workflow.task_list[0].state_record_list) - 1 - t
                    self.print_log(t)

    def write_simple_json(self, file_path, encoding="utf-8", indent=4):
        """
        Create json file of this project.

        Args:
            file_path (str):
                File path for saving this project data.
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
                "cost_list": self.cost_list,
                "simulation_mode": int(self.simulation_mode),
                "status": int(self.status),
            }
        )
        for product in self.product_list:
            dict_data["pDESy"].append(product.export_dict_json_data())
        for workflow in self.workflow_list:
            dict_data["pDESy"].append(workflow.export_dict_json_data())
        for team in self.team_list:
            dict_data["pDESy"].append(team.export_dict_json_data())
        for workplace in self.workplace_list:
            dict_data["pDESy"].append(workplace.export_dict_json_data())
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(dict_data, f, indent=indent)

    def read_simple_json(self, file_path, encoding="utf-8"):
        """
        Read json file which is created by BaseProject.write_simple_json().

        Args:
            file_path (str):
                File path for reading this project data.
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
        self.cost_list = project_json["cost_list"]
        self.simulation_mode = SimulationMode(project_json["simulation_mode"])
        self.status = BaseProjectStatus(project_json["status"])
        # 1. read all node and attr only considering ID info
        # product
        product_json_list = list(
            filter(lambda node: node["type"] == "BaseProduct", data)
        )
        for product_json in product_json_list:
            product = BaseProduct(component_list=[])
            product.read_json_data(product_json)
            self.product_list.append(product)
        # workflow
        workflow_json_list = list(
            filter(lambda node: node["type"] == "BaseWorkflow", data)
        )
        for workflow_json in workflow_json_list:
            workflow = BaseWorkflow(task_list=[])
            workflow.read_json_data(workflow_json)
            self.workflow_list.append(workflow)

        # team
        team_json_list = list(filter(lambda node: node["type"] == "BaseTeam", data))
        for team_json in team_json_list:
            team = BaseTeam(worker_list=[])
            team.read_json_data(team_json)
            self.team_list.append(team)

        # workplace
        workplace_json_list = list(
            filter(lambda node: node["type"] == "BaseWorkplace", data)
        )
        for workplace_json in workplace_json_list:
            workplace = BaseWorkplace(facility_list=[])
            workplace.read_json_data(workplace_json)
            self.workplace_list.append(workplace)

        all_component_list = self.get_all_component_list()
        all_task_list = self.get_all_task_list()
        # 2. update ID info to instance info
        # 2-1. component
        for c in all_component_list:
            c.child_component_id_list = [
                component.ID
                for component in all_component_list
                if component.ID in c.child_component_id_list
            ]
            c.targeted_task_id_list = [
                task.ID for task in all_task_list if task.ID in c.targeted_task_id_list
            ]
            c.placed_workplace = (
                [
                    workplace
                    for workplace in self.workplace_list
                    if workplace.ID == c.placed_workplace
                ]
                if c.placed_workplace is not None
                else None
            )
        # 2-2. task
        for t in all_task_list:
            t.input_task_id_dependency_list = [
                [
                    [task for task in all_task_list if task.ID == ID][0].ID,
                    BaseTaskDependency(dependency_number),
                ]
                for (ID, dependency_number) in t.input_task_id_dependency_list
            ]
            t.allocated_team_id_list = [
                [team.ID for team in self.team_list if team.ID == ID][0]
                for ID in t.allocated_team_id_list
            ]
            t.allocated_workplace_id_list = [
                [
                    workplace.ID
                    for workplace in self.workplace_list
                    if workplace.ID == ID
                ][0]
                for ID in t.allocated_workplace_id_list
            ]
            t.target_component_id = (
                [
                    component.ID
                    for component in all_component_list
                    if component.ID == t.target_component_id
                ][0]
                if t.target_component_id is not None
                else None
            )

            t.allocated_worker_id_list = [
                wid
                for wid in t.allocated_worker_id_list
                if wid in t.allocated_worker_id_list
            ]

            t.allocated_facility_id_list = [
                fid
                for fid in t.allocated_facility_id_list
                if fid in t.allocated_facility_id_list
            ]

        # 2-3. team
        for x in self.team_list:
            x.targeted_task_id_list = [
                task.ID for task in all_task_list if task.ID in x.targeted_task_id_list
            ]
            x.parent_team_id = (
                [team.ID for team in self.team_list if team.ID == x.parent_team_id][0]
                if x.parent_team_id is not None
                else None
            )
            for w in x.worker_list:
                w.assigned_task_list = [
                    task for task in all_task_list if task.ID in w.assigned_task_list
                ]

        # 2-4. workplace
        for x in self.workplace_list:
            x.targeted_task_id_list = [
                task.ID for task in all_task_list if task.ID in x.targeted_task_id_list
            ]
            x.parent_workplace_id = (
                [
                    workplace.ID
                    for workplace in self.workplace_list
                    if workplace.ID == x.parent_workplace_id
                ][0]
                if x.parent_workplace_id is not None
                else None
            )
            x.placed_component_list = [
                component
                for component in all_component_list
                if component.ID in x.placed_component_list
            ]
            for f in x.facility_list:
                f.assigned_task_list = [
                    task for task in all_task_list if task.ID in f.assigned_task_list
                ]

    def get_all_worker_list(self):
        """
        Get all worker list of this project.

        Returns:
            all_worker_list (list):
                All worker list of this project.
        """
        all_worker_list = []
        for team in self.team_list:
            all_worker_list.extend(team.worker_list)
        return all_worker_list

    def get_all_facility_list(self):
        """
        Get all facility list of this project.

        Returns:
            all_facility_list (list):
                All facility list of this project.
        """
        all_facility_list = []
        for workplace in self.workplace_list:
            all_facility_list.extend(workplace.facility_list)
        return all_facility_list

    def append_project_log_from_simple_json(self, file_path, encoding="utf-8"):
        """
        Append project log information from json file created by BaseProject.write_simple_json().
        TODO: This function is not yet verified sufficiently.

        Args:
            file_path (str):
                File path for reading targeted extended project data.
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
            self.cost_list.extend(project_json["cost_list"])

            # product
            all_component_list = self.get_all_component_list()
            product_json = list(
                filter(lambda node: node["type"] == "BaseProduct", data)
            )[0]
            for c_json in product_json["component_list"]:
                c = list(
                    filter(
                        lambda component, c_json=c_json: component.ID == c_json["ID"],
                        all_component_list,
                    )
                )[0]
                c.state = BaseComponentState(c_json["state"])
                c.state_record_list.extend(
                    [BaseComponentState(num) for num in c_json["state_record_list"]]
                )
                c.placed_workplace = c_json["placed_workplace"]
                c.placed_workplace_id_record.extend(
                    c_json["placed_workplace_id_record"]
                )

            # workflow
            workflow_j = list(
                filter(lambda node: node["type"] == "BaseWorkflow", data)
            )[0]
            for j in workflow_j["task_list"]:
                task = list(
                    filter(
                        lambda task, j=j: task.ID == j["ID"],
                        self.get_all_task_list(),
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
                task.allocated_worker_id_list = j["allocated_worker_id_list"]
                task.allocated_worker_id_record.extend(j["allocated_worker_id_record"])
                task.allocated_facility_id_list = j["allocated_facility_id_list"]
                task.allocated_facility_id_record.extend(
                    j["allocated_facility_id_record"]
                )

            # organization
            o_json = list(
                filter(lambda node: node["type"] == "BaseOrganization", data)
            )[0]
            # team
            team_list_j = o_json["team_list"]
            for team_j in team_list_j:
                team = list(
                    filter(
                        lambda team, team_j=team_j: team.ID == team_j["ID"],
                        self.team_list,
                    )
                )[0]
                team.cost_list.extend(team_j["cost_list"])
                for j in team_j["worker_list"]:
                    worker = list(
                        filter(
                            lambda worker, j=j: worker.ID == j["ID"],
                            team.worker_list,
                        )
                    )[0]
                    worker.state = BaseWorkerState(j["state"])
                    worker.state_record_list.extend(
                        [BaseWorkerState(num) for num in j["state_record_list"]],
                    )
                    worker.cost_list.extend(j["cost_list"])
                    worker.assigned_task_list = j["assigned_task_list"]
                    worker.assigned_task_id_record.extend(j["assigned_task_id_record"])

            # workplace
            workplace_list_j = o_json["workplace_list"]
            for workplace_j in workplace_list_j:
                workplace = list(
                    filter(
                        lambda workplace, workplace_j=workplace_j: workplace.ID
                        == workplace_j["ID"],
                        self.workplace_list,
                    )
                )[0]
                workplace.cost_list.extend(workplace_j["cost_list"])
                workplace.placed_component_list = workplace_j["placed_component_list"]
                workplace.placed_component_id_record.extend(
                    workplace_j["placed_component_id_record"]
                )
                for j in workplace_j["facility_list"]:
                    facility = list(
                        filter(
                            lambda worker, j=j: worker.ID == j["ID"],
                            workplace.facility_list,
                        )
                    )[0]
                    facility.state = BaseWorkerState(j["state"])
                    facility.state_record_list.extend(
                        [BaseWorkerState(num) for num in j["state_record_list"]],
                    )
                    facility.cost_list.extend(j["cost_list"])
                    facility.assigned_task_list = j["assigned_task_list"]
                    facility.assigned_task_id_record.extend(
                        j["assigned_task_id_record"]
                    )

    def get_target_mermaid_diagram(
        self,
        target_product_list: list[BaseProduct] = None,
        target_workflow_list: list[BaseWorkflow] = None,
        target_team_list: list[BaseTeam] = None,
        target_workplace_list: list[BaseWorkplace] = None,
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
            target_product_list (list[BaseProduct], optional):
                Target product list.
                Defaults to None.
            target_workflow_list (list[BaseWorkflow], optional):
                Target workflow list.
                Defaults to None.
            target_team_list (list[BaseTeam], optional):
                Target team list.
                Defaults to None.
            target_workplace_list (list[BaseWorkplace], optional):
                Target workplace list.
                Defaults to None.
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            link_type_str_workplace_workplace (str, optional):
                Link type string of each workplace and workplace.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        # product, workflow, organization
        for product in target_product_list:
            list_of_lines.extend(
                product.get_mermaid_diagram(
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )
        for workflow in target_workflow_list:
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
        for team in target_team_list:
            list_of_lines.extend(
                team.get_mermaid_diagram(
                    print_worker=print_worker,
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_worker,
                    subgraph=subgraph_team,
                    subgraph_direction=subgraph_direction_team,
                )
            )
        for workplace in target_workplace_list:
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
        for product in target_product_list:
            for c in product.component_list:
                targeted_task_list = self.get_target_task_list(c.targeted_task_id_list)
                for t in targeted_task_list:
                    if t.parent_workflow_id in [w.ID for w in target_workflow_list]:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_list:
            for t in workflow.task_list:
                for team_id in t.allocated_team_id_list:
                    if team_id in [team.ID for team in target_team_list]:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_list:
                    if workplace_id in [w.ID for w in target_workplace_list]:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        # workplace -> workplace
        for workplace in target_workplace_list:
            for input_workplace in workplace.input_workplace_list:
                list_of_lines.append(
                    f"{input_workplace.ID}{link_type_str_workplace_workplace}{workplace.ID}"
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
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        return self.get_target_mermaid_diagram(
            target_product_list=self.product_list,
            target_workflow_list=self.workflow_list,
            target_team_list=self.team_list,
            target_workplace_list=self.workplace_list,
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
        target_product_list: list[BaseProduct] = None,
        target_workflow_list: list[BaseWorkflow] = None,
        target_team_list: list[BaseTeam] = None,
        target_workplace_list: list[BaseWorkplace] = None,
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
            target_product_list (list[BaseProduct], optional):
                Target product list.
                Defaults to None -> [].
            target_workflow_list (list[BaseWorkflow], optional):
                Target workflow list.
                Defaults to None -> [].
            target_team_list (list[BaseTeam], optional):
                Target team list.
                Defaults to None -> [].
            target_workplace_list (list[BaseWorkplace], optional):
                Target workplace list.
                Defaults to None -> [].
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        if target_product_list is None:
            target_product_list = []
        if target_workflow_list is None:
            target_workflow_list = []
        if target_team_list is None:
            target_team_list = []
        if target_workplace_list is None:
            target_workplace_list = []
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_mermaid_diagram(
            target_product_list=target_product_list,
            target_workflow_list=target_workflow_list,
            target_team_list=target_team_list,
            target_workplace_list=target_workplace_list,
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
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        self.print_target_mermaid_diagram(
            target_product_list=self.product_list,
            target_workflow_list=self.workflow_list,
            target_team_list=self.team_list,
            target_workplace_list=self.workplace_list,
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
        target_product_list: list[BaseProduct],
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
        Get mermaid diagram of target information.

        Args:
            target_product_list (list[BaseProduct]):
                Target product list.
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for product in target_product_list:
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
        for product in target_product_list:
            for component in product.component_list:
                targeted_task_list = self.get_target_task_list(
                    component.targeted_task_id_list
                )
                for task in targeted_task_list:
                    target_task_set.add(task)

                    target_workflow = next(
                        (
                            w
                            for w in self.workflow_list
                            if w.ID == task.parent_workflow_id
                        ),
                        None,
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
            for task in workflow.task_list:
                for team_id in task.allocated_team_id_list:
                    target_team = next(
                        (team for team in self.team_list if team.ID == team_id), None
                    )
                    target_team_set.add(target_team)
                    for worker in target_team.worker_list:
                        target_worker_set.add(worker)
                for workplace_id in task.allocated_workplace_id_list:
                    target_workplace = next(
                        (w for w in self.workplace_list if w.ID == workplace_id), None
                    )
                    target_workplace_set.add(target_workplace)
                    for facility in target_workplace.facility_list:
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
        for product in target_product_list:
            for c in product.component_list:
                targeted_task_list = self.get_target_task_list(c.targeted_task_id_list)
                for t in targeted_task_list:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_list:
                for team_id in t.allocated_team_id_list:
                    if team_id in {team.ID for team in target_team_set}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_list:
                    if workplace_id in {w.ID for w in target_workplace_set}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_product_related_mermaid_diagram(
        self,
        target_product_list: list[BaseProduct],
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
            target_product_list (list[BaseProduct], optional):
                Target product list.
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_product_related_mermaid_diagram(
            target_product_list=target_product_list,
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
        target_team_list: list[BaseTeam],
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
        Get mermaid diagram of target information.

        Args:
            target_team_list (list[BaseProduct]):
                Target team list.
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for team in target_team_list:
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
        for team in target_team_list:
            targeted_task_list = self.get_target_task_list(team.targeted_task_id_list)
            for task in targeted_task_list:
                target_task_set.add(task)

                target_workflow = next(
                    (w for w in self.workflow_list if w.ID == task.parent_workflow_id),
                    None,
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

        target_workplace_set = set()
        target_facility_set = set()
        for workflow in target_workflow_set:
            for task in workflow.task_list:
                for workplace_id in task.allocated_workplace_id_list:
                    target_workplace = next(
                        (w for w in self.workplace_list if w.ID == workplace_id), None
                    )
                    target_workplace_set.add(target_workplace)
                    for facility in target_workplace.facility_list:
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
            for task in workflow.task_list:
                if task.target_component_id is not None:
                    target_component = next(
                        (
                            component
                            for component in self.get_all_component_list()
                            if component.ID == task.target_component_id
                        ),
                        None,
                    )
                    target_component_set.add(target_component)

                    target_product = next(
                        (
                            p
                            for p in self.product_list
                            if p.ID == target_component.parent_product_id
                        ),
                        None,
                    )
                    target_product_set.add(target_product)

        for product in target_product_set:
            list_of_lines.extend(
                product.get_target_component_mermaid_diagram(
                    target_component_list=target_component_set,
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )

        # product -> workflow
        target_workflow_id_set = {wf.ID for wf in target_workflow_set}
        for product in target_product_set:
            for c in product.component_list:
                targeted_task_list = self.get_target_task_list(c.targeted_task_id_list)
                for t in targeted_task_list:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_list:
                for team_id in t.allocated_team_id_list:
                    if team_id in {team.ID for team in target_team_list}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_list:
                    if workplace_id in {w.ID for w in target_workplace_set}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_team_related_mermaid_diagram(
        self,
        target_team_list: list[BaseTeam],
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
            target_team_list (list[BaseTeam], optional):
                Target team list.
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_team_related_mermaid_diagram(
            target_team_list=target_team_list,
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
        target_workplace_list: list[BaseWorkplace],
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
        Get mermaid diagram of target information.

        Args:
            target_workplace_list (list[BaseWorkplace]):
                Target workplace list.
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for workplace in target_workplace_list:
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
        for workplace in target_workplace_list:
            targeted_task_list = self.get_target_task_list(
                workplace.targeted_task_id_list
            )
            for task in targeted_task_list:
                target_task_set.add(task)

                target_workflow = next(
                    (w for w in self.workflow_list if w.ID == task.parent_workflow_id),
                    None,
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
        for workflow in target_workflow_set:
            for task in workflow.task_list:
                for team_id in task.allocated_team_id_list:
                    target_team = next(
                        (t for t in self.team_list if t.ID == team_id), None
                    )
                    if target_team is not None:
                        target_team_set.add(target_team)
                        for worker in target_team.worker_list:
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
            for task in workflow.task_list:
                if task.target_component_id is not None:
                    target_component = next(
                        (
                            component
                            for component in self.get_all_component_list()
                            if component.ID == task.target_component_id
                        ),
                        None,
                    )
                    target_component_set.add(target_component)

                    target_product = next(
                        (
                            p
                            for p in self.product_list
                            if p.ID == target_component.parent_product_id
                        ),
                        None,
                    )
                    target_product_set.add(target_product)

        for product in target_product_set:
            list_of_lines.extend(
                product.get_target_component_mermaid_diagram(
                    target_component_list=target_component_set,
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )

        # product -> workflow
        target_workflow_id_set = {wf.ID for wf in target_workflow_set}
        for product in target_product_set:
            for c in product.component_list:
                targeted_task_list = self.get_target_task_list(c.targeted_task_id_list)
                for t in targeted_task_list:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_set:
            for t in workflow.task_list:
                for team_id in t.allocated_team_id_list:
                    if team_id in {team.ID for team in target_team_set}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_list:
                    if workplace_id in {w.ID for w in target_workplace_list}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_workplace_related_mermaid_diagram(
        self,
        target_workplace_list: list[BaseWorkplace],
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
            target_workplace_list (list[BaseWorkplace]):
                Target workplace list.
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_workplace_related_mermaid_diagram(
            target_workplace_list=target_workplace_list,
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
        target_workflow_list: list[BaseWorkflow],
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
        Get mermaid diagram of target information.

        Args:
            target_workflow_list (list[BaseWorkflow]):
                Target workflow list.
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for workflow in target_workflow_list:
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
        for workflow in target_workflow_list:
            for task in workflow.task_list:
                for team_id in task.allocated_team_id_list:
                    target_team = next(
                        (t for t in self.team_list if t.ID == team_id), None
                    )
                    if target_team is not None:
                        target_team_set.add(target_team)
                        for worker in target_team.worker_list:
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
        for workflow in target_workflow_list:
            for task in workflow.task_list:
                for workplace_id in task.allocated_workplace_id_list:
                    target_workplace = next(
                        (w for w in self.workplace_list if w.ID == workplace_id), None
                    )
                    target_workplace_set.add(target_workplace)
                    for facility in target_workplace.facility_list:
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
        for workflow in target_workflow_list:
            for task in workflow.task_list:
                if task.target_component_id is not None:
                    target_component = next(
                        (
                            component
                            for component in self.get_all_component_list()
                            if component.ID == task.target_component_id
                        ),
                        None,
                    )
                    target_component_set.add(target_component)

                    target_product = next(
                        (
                            p
                            for p in self.product_list
                            if p.ID == target_component.parent_product_id
                        ),
                        None,
                    )
                    target_product_set.add(target_product)

        for product in target_product_set:
            list_of_lines.extend(
                product.get_target_component_mermaid_diagram(
                    target_component_list=target_component_set,
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )

        # product -> workflow
        target_workflow_id_set = {wf.ID for wf in target_workflow_list}
        for product in target_product_set:
            for c in product.component_list:
                targeted_task_list = self.get_target_task_list(c.targeted_task_id_list)
                for t in targeted_task_list:
                    if t.parent_workflow_id in target_workflow_id_set:
                        list_of_lines.append(
                            f"{c.ID}{link_type_str_component_task}{t.ID}"
                        )

        # team & workflow -> workflow
        for workflow in target_workflow_list:
            for t in workflow.task_list:
                for team_id in t.allocated_team_id_list:
                    if team_id in {team.ID for team in target_team_set}:
                        list_of_lines.append(
                            f"{t.ID}{link_type_str_worker_task}{team_id}"
                        )
                for workplace_id in t.allocated_workplace_id_list:
                    if workplace_id in {w.ID for w in target_workplace_set}:
                        list_of_lines.append(
                            f"{workplace_id}{link_type_str_facility_task}{t.ID}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_workflow_related_mermaid_diagram(
        self,
        target_workflow_list: list[BaseWorkflow],
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
            target_workflow_list (list[BaseWorkflow]):
                Target workflow list.
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph_product (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_product (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph_workflow (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workflow (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph_team (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_team (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph_workplace (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction_workplace (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_component_task (str, optional):
                Link type string of each component and task.
                Defaults to "-.-".
            link_type_str_worker_task (str, optional):
                Link type string of each worker and task.
                Defaults to "-.-".
            link_type_str_facility_task (str, optional):
                Link type string of each facility and task.
                Defaults to "-.-".
            link_type_str_worker_facility (str, optional):
                Link type string of each worker and facility.
                Defaults to "-.-".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_workflow_related_mermaid_diagram(
            target_workflow_list=target_workflow_list,
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
        Get mermaid diagram of all product.

        Args:
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        list_of_lines = []
        for product in self.product_list:
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
        Print mermaid diagram of all product.

        Args:
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_component (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            link_type_str_component (str, optional):
                Link type string of each component.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
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
        Get mermaid diagram of all workflow.
        Args:
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        list_of_lines = []
        for workflow in self.workflow_list:
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
        Print mermaid diagram of all workflow.

        Args:
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            link_type_str_task (str, optional):
                Link type string of each task.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
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
        Get mermaid diagram of all team.

        Args:
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        list_of_lines = []
        for team in self.team_list:
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
        Print mermaid diagram of all team.

        Args:
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_worker (str, optional):
                Link type string of each worker.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
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
        Get mermaid diagram of all workplace.

        Args:
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
            link_type_str_workplace_workplace (str, optional):
                Link type string of each workplace.
                Defaults to "-->".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        for workplace in self.workplace_list:
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
        for workplace in self.workplace_list:
            for input_workplace in workplace.input_workplace_list:
                list_of_lines.append(
                    f"{input_workplace.ID}{link_type_str_workplace_workplace}{workplace.ID}"
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
        Print mermaid diagram of all workplace.

        Args:
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            link_type_str_facility (str, optional):
                Link type string of each facility.
                Defaults to "-->".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
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
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Get mermaid diagram of all product.
        Args:
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        list_of_lines = []
        for product in self.product_list:
            list_of_lines.extend(
                product.get_gantt_mermaid(
                    section=section,
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_all_product_gantt_mermaid(
        self,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Print mermaid diagram of all product.
        Args:
            date_format (str, optional):
                Date format.
                Defaults to "X".
            axis_format (str, optional):
                Axis format.
                Defaults to "%s".
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_product_gantt_mermaid(
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
        )
        print(*list_of_lines, sep="\n")

    def get_all_workflow_gantt_mermaid(
        self,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Get mermaid diagram of all workflow.
        Args:
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        list_of_lines = []
        for workflow in self.workflow_list:
            list_of_lines.extend(
                workflow.get_gantt_mermaid(
                    section=section,
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_all_workflow_gantt_mermaid(
        self,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Print mermaid diagram of all workflow.
        Args:
            section (bool, optional):
                Section or not.
                Defaults to True.
            date_format (str, optional):
                Date format.
                Defaults to "X".
            axis_format (str, optional):
                Axis format.
                Defaults to "%s".
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_workflow_gantt_mermaid(
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
        )
        print(*list_of_lines, sep="\n")

    def get_all_team_gantt_mermaid(
        self,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Get mermaid diagram of all team.
        Args:
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        list_of_lines = []
        for team in self.team_list:
            list_of_lines.extend(
                team.get_gantt_mermaid(
                    section=section,
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_all_team_gantt_mermaid(
        self,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Print mermaid diagram of all team.
        Args:
            date_format (str, optional):
                Date format.
                Defaults to "X".
            axis_format (str, optional):
                Axis format.
                Defaults to "%s".
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_team_gantt_mermaid(
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
        )
        print(*list_of_lines, sep="\n")

    def get_all_workplace_gantt_mermaid(
        self,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Get mermaid diagram of all workplace.
        Args:
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        id_name_dict = self.get_all_id_name_dict()
        list_of_lines = []
        for workplace in self.workplace_list:
            list_of_lines.extend(
                workplace.get_gantt_mermaid(
                    section=section,
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_all_workplace_gantt_mermaid(
        self,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
    ):
        """
        Print mermaid diagram of all workplace.
        Args:
            date_format (str, optional):
                Date format.
                Defaults to "X".
            axis_format (str, optional):
                Axis format.
                Defaults to "%s".
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range time.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                Detailed information or not.
                Defaults to False.
            id_name_dict (dict[str, str], optional):
                ID to name dictionary.
                Defaults to None.
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_all_workplace_gantt_mermaid(
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
        )
        print(*list_of_lines, sep="\n")
