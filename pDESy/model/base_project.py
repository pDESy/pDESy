#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_project."""

import datetime
import itertools
import json
import uuid
import warnings
from abc import ABCMeta
from enum import IntEnum

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
            "TIME: {}\nPRODUCT\n{}\n\nWorkflow\n{}\n\nTEAM\n{}\n\nWORKPLACE\n{}".format(
                self.time,
                str(self.product_list),
                str(self.workflow_list),
                str(self.team_list),
                str(self.workplace_list),
            )
        )

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
        for product in self.product_list:
            product.initialize(state_info=state_info, log_info=log_info)
        for team in self.team_list:
            team.initialize(state_info=state_info, log_info=log_info)
        for workplace in self.workplace_list:
            workplace.initialize(state_info=state_info, log_info=log_info)

    def simulate(
        self,
        task_performed_mode="multi-workers",
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        error_tol=1e-10,
        absence_time_list=[],
        perform_auto_task_while_absence_time=False,
        initialize_state_info=True,
        initialize_log_info=True,
        max_time=10000,
        unit_time=1,
    ):
        """
        Simulate this BaseProject.

        Args:
            task_performed_mode (str, optional):
                Mode of performed task in simulation.
                pDESy has the following options of this mode in simulation.

                  - multi-workers

                Defaults to "multi-workers".
            task_priority_rule (TaskPriorityRule, optional):
                Task priority rule for simulation.
                Defaults to TaskPriorityRule.TSLACK.
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            absence_time_list (List[int], optional):
                List of absence time in simulation.
                Defaults to []. This means workers work every time.
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
        if not (task_performed_mode == "multi-workers"):
            raise Exception(
                "Please check "
                "task_performed_mode"
                " which is equal to "
                "multi-workers"
                ""
            )

        # set simulation mode
        mode = 0
        if task_performed_mode == "multi-workers":
            mode = 1  # TaskPerformedBySingleTaskWorkers in pDES
        # -----------------------------------------------------------------------------

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
                workflow.check_state(self.time, BaseTaskState.WORKING)
            for product in self.product_list:
                product.check_state()  # product should be checked after checking workflow state

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
                if mode == 1:
                    self.__perform()
            elif perform_auto_task_while_absence_time:
                for workflow in self.workflow_list:
                    workflow.perform(self.time, only_auto_task=True)

            # 5. Record
            self.__record(working=working)

            # 6. Update time
            self.time = self.time + unit_time

    def backward_simulate(
        self,
        task_performed_mode="multi-workers",
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        error_tol=1e-10,
        absence_time_list=[],
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
                Defaults to []. This means workers work every time.
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
        for workflow in self.workflow_list:
            workflow.reverse_dependencies()

        # reverse_dependency of workplace
        # TODO create method for reverse_dependency of workplace
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

        # reverse_dependency of team, but not yet implemented..
        # TODO define input_team_list and output_team_list in BaseTeam
        # TODO create method for reverse_dependency of team

        autotask_removing_after_simulation = set()
        try:
            if considering_due_time_of_tail_tasks:
                # Add dummy task for considering the difference of due_time
                for workflow in self.workflow_list:
                    tail_task_list = list(
                        filter(
                            lambda task: len(task.input_task_list) == 0,
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
                            tail_task.append_input_task(
                                auto_task, task_dependency_mode=BaseTaskDependency.FS
                            )
                            autotask_removing_after_simulation.add(auto_task)
                            workflow.task_list.append(auto_task)

            self.simulate(
                task_performed_mode=task_performed_mode,
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
            for autotask in autotask_removing_after_simulation:
                for task, dependency in autotask.output_task_list:
                    task.input_task_list.remove([autotask, dependency])
                for workflow in self.workflow_list:
                    if autotask in workflow.task_list:
                        workflow.task_list.remove(autotask)
            if reverse_log_information:
                self.reverse_log_information()

            for workflow in self.workflow_list:
                workflow.reverse_dependencies()

            # reverse_dependency of workplace
            # TODO create method for reverse_dependency of workplace
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

            # reverse_dependency of team, but not yet implemented..
            # TODO define input_team_list and output_team_list in BaseTeam
            # TODO create method for reverse_dependency of team

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

    def __perform(self):
        for workflow in self.workflow_list:
            workflow.perform(self.time)

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
            workflow.check_state(self.time, BaseTaskState.FINISHED)
        for product in self.product_list:
            product.check_state()  # product should be checked after checking workflow state
            product.check_removing_placed_workplace()
        for workflow in self.workflow_list:
            workflow.check_state(self.time, BaseTaskState.READY)
        for product in self.product_list:
            product.check_state()  # product should be checked after checking workflow state
        for workflow in self.workflow_list:
            workflow.update_PERT_data(self.time)

    def __is_allocated_worker(self, worker, task):
        team = list(filter(lambda team: team.ID == worker.team_id, self.team_list))[0]
        return task in team.targeted_task_list

    def __is_allocated_facility(self, facility, task):
        workplace = list(
            filter(
                lambda workplace: workplace.ID == facility.workplace_id,
                self.workplace_list,
            )
        )[0]
        return task in workplace.targeted_task_list

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
            if task.target_component is not None:
                # 3-1. Set target component of workplace if target component is ready
                component = task.target_component
                if component.is_ready():
                    candidate_workplace_list = task.allocated_workplace_list
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

                            if (
                                conveyor_condition
                                and workplace.can_put(component)
                                and workplace.get_total_workamount_skill(task.name)
                                > 1e-10
                            ):
                                # 3-1-1. move ready_component
                                pre_workplace = component.placed_workplace

                                # 3-1-1-1. remove
                                if pre_workplace is None:
                                    for child_c in component.child_component_list:
                                        wp = child_c.placed_workplace
                                        if wp is not None:
                                            for c_wp in wp.placed_component_list:
                                                if task.target_component.ID in [
                                                    c.ID
                                                    for c in c_wp.parent_component_list
                                                ]:
                                                    wp.remove_placed_component(c_wp)

                                elif pre_workplace is not None:
                                    pre_workplace.remove_placed_component(component)

                                component.set_placed_workplace(None)

                                # 3-1-1-2. regsister
                                component.set_placed_workplace(workplace)
                                workplace.set_placed_component(component)
                                break

            if not task.auto_task:
                # 3-2. Allocate ready tasks to free workers and facilities

                if task.need_facility:
                    # Search candidate facilities from the list of placed_workplace
                    placed_workplace = task.target_component.placed_workplace

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
                                lambda facility: facility.has_workamount_skill(
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
                                    lambda worker: worker.has_workamount_skill(
                                        task.name
                                    )
                                    and self.__is_allocated_worker(worker, task)
                                    and task.can_add_resources(
                                        worker=worker, facility=facility
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
                                task.allocated_worker_list.append(worker)
                                worker.assigned_task_list.append(task)
                                task.allocated_facility_list.append(facility)
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
                            lambda worker: worker.has_workamount_skill(task.name)
                            and self.__is_allocated_worker(worker, task),
                            free_worker_list,
                        )
                    )

                    # Allocate free workers to tasks
                    for worker in allocating_workers:
                        if task.can_add_resources(worker=worker):
                            task.allocated_worker_list.append(worker)
                            worker.assigned_task_list.append(task)
                            free_worker_list = [
                                w for w in free_worker_list if w.ID != worker.ID
                            ]

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

        G_product = nx.DiGraph()
        for product in self.product_list:
            G_product = nx.compose(G_product, product.get_networkx_graph())

        G_workflow = nx.DiGraph()
        for workflow in self.workflow_list:
            G_workflow = nx.compose(G_workflow, workflow.get_networkx_graph())

        G_team = nx.DiGraph()
        # 1. add all nodes
        for team in self.team_list:
            G_team.add_node(team)
        # 2. add all edges
        for team in self.team_list:
            if team.parent_team is not None:
                G_team.add_edge(team.parent_team, team)
        if view_workers:
            for team in self.team_list:
                for w in team.worker_list:
                    G_team.add_node(w)
                    G_team.add_edge(team, w)

        G_workplace = nx.DiGraph()
        # 1. add all nodes
        for workplace in self.workplace_list:
            G_workplace.add_node(workplace)
        # 2. add all edges
        for workplace in self.workplace_list:
            if workplace.parent_workplace is not None:
                G_workplace.add_edge(workplace.parent_workplace, workplace)
        if view_facilities:
            for workplace in self.workplace_list:
                for w in workplace.facility_list:
                    G_workplace.add_node(w)
                    G_workplace.add_edge(workplace, w)

        G = nx.compose_all([G_product, G_workflow, G_team, G_workplace])

        # add edge between product and workflow
        for product in self.product_list:
            for c in product.component_list:
                for task in c.targeted_task_list:
                    G.add_edge(c, task)

        # add edge between workflow and team
        for team in self.team_list:
            for task in team.targeted_task_list:
                G.add_edge(team, task)

        if view_workers:
            for team in self.team_list:
                for w in team.worker_list:
                    # G.add_node(w)
                    G.add_edge(team, w)

        # add edge between workflow and workplace
        for workplace in self.workplace_list:
            for task in workplace.targeted_task_list:
                G.add_edge(workplace, task)

        if view_facilities:
            for workplace in self.workplace_list:
                for w in workplace.facility_list:
                    # G.add_node(w)
                    G.add_edge(workplace, w)

        return G

    def draw_networkx(
        self,
        G=None,
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
        figsize=[6.4, 4.8],
        dpi=100.0,
        save_fig_path=None,
        **kwds,
    ):
        """
        Draw networkx.

        Args:
            G (networkx.SDigraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
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
                Default to [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """
        fig = plt.figure(figsize=figsize, dpi=dpi)
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)

        # Product
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=self.get_all_component_list(),
            node_color=component_node_color,
        )
        # Workflow
        normal_task_list = [
            task for task in self.get_all_task_list() if not task.auto_task
        ]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=normal_task_list,
            node_color=task_node_color,
        )
        auto_task_list = [task for task in self.get_all_task_list() if task.auto_task]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=auto_task_list,
            node_color=auto_task_node_color,
        )
        # Team
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=self.team_list,
            node_color=team_node_color,
            # **kwds,
        )
        if view_workers:
            worker_list = []
            for team in self.team_list:
                worker_list.extend(team.worker_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=worker_list,
                node_color=worker_node_color,
                # **kwds,
            )

        # Workplace
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=self.workplace_list,
            node_color=workplace_node_color,
            # **kwds,
        )
        if view_facilities:
            facility_list = []
            for workplace in self.workplace_list:
                facility_list.extend(workplace.facility_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=facility_list,
                node_color=facility_node_color,
                # **kwds,
            )

        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        plt.axis("off")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig

    def get_node_and_edge_trace_for_plotly_network(
        self,
        G=None,
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
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
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
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)

        component_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
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
            hoverinfo="text",
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
            hoverinfo="text",
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
            hoverinfo="text",
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
            hoverinfo="text",
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
            hoverinfo="text",
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
            hoverinfo="text",
            marker={
                "color": facility_node_color,
                "size": node_size,
            },
        )

        edge_trace = go.Scatter(
            x=[],
            y=[],
            line={"width": 0, "color": "#888"},
            hoverinfo="none",
            mode="lines",
        )

        for node in G.nodes:
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

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace["x"] += (xposx, yposx)
            edge_trace["y"] += (xposy, yposy)

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
        G=None,
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
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
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
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)
        (
            component_node_trace,
            task_node_trace,
            auto_task_node_trace,
            team_node_trace,
            worker_node_trace,
            workplace_node_trace,
            facility_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(G, pos, node_size=node_size)
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

    def print_all_log_in_chronological_order(self, backward=None):
        """
        Print all log in chronological order.
        """
        if backward is not None:
            backward = backward
        elif self.simulation_mode == SimulationMode.BACKWARD:
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
            c.parent_component_list = [
                component
                for component in all_component_list
                if component.ID in c.parent_component_list
            ]
            c.child_component_list = [
                component
                for component in all_component_list
                if component.ID in c.child_component_list
            ]
            c.targeted_task_list = [
                task for task in all_task_list if task.ID in c.targeted_task_list
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
            t.input_task_list = [
                [
                    [task for task in all_task_list if task.ID == ID][0],
                    BaseTaskDependency(dependency_number),
                ]
                for (ID, dependency_number) in t.input_task_list
            ]
            t.output_task_list = [
                [
                    [task for task in all_task_list if task.ID == ID][0],
                    BaseTaskDependency(dependency_number),
                ]
                for (ID, dependency_number) in t.output_task_list
            ]
            t.allocated_team_list = [
                [team for team in self.team_list if team.ID == ID][0]
                for ID in t.allocated_team_list
            ]
            t.allocated_workplace_list = [
                [workplace for workplace in self.workplace_list if workplace.ID == ID][
                    0
                ]
                for ID in t.allocated_workplace_list
            ]
            t.target_component = (
                [
                    component
                    for component in all_component_list
                    if component.ID == t.target_component
                ][0]
                if t.target_component is not None
                else None
            )

            worker_dict = {worker.ID: worker for worker in self.get_all_worker_list()}
            t.allocated_worker_list = [
                worker_dict[wid]
                for wid in t.allocated_worker_list
                if wid in worker_dict
            ]

            facility_dict = {
                facility.ID: facility for facility in self.get_all_facility_list()
            }
            t.allocated_facility_list = [
                facility_dict[fid]
                for fid in t.allocated_facility_list
                if fid in facility_dict
            ]

        # 2-3. team
        for x in self.team_list:
            x.targeted_task_list = [
                task for task in all_task_list if task.ID in x.targeted_task_list
            ]
            x.parent_team = (
                [team for team in self.team_list if team.ID == x.parent_team][0]
                if x.parent_team is not None
                else None
            )
            for w in x.worker_list:
                w.assigned_task_list = [
                    task for task in all_task_list if task.ID in w.assigned_task_list
                ]

        # 2-4. workplace
        for x in self.workplace_list:
            x.targeted_task_list = [
                task for task in all_task_list if task.ID in x.targeted_task_list
            ]
            x.parent_workplace = (
                [
                    workplace
                    for workplace in self.workplace_list
                    if workplace.ID == x.parent_workplace
                ][0]
                if x.parent_workplace is not None
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
        Append project log information from json file which is created by BaseProject.write_simple_json().
        TODO: This function is not yet verified sufficiently.

        Args:
            file_path (str):
                File path for reading targeted extended project data.
        """
        warnings.warn(
            "This function is not yet verified sufficiently.",
            UserWarning,
        )
        pdes_json = open(file_path, "r", encoding=encoding)
        json_data = json.load(pdes_json)
        data = json_data["pDESy"]
        project_json = list(filter(lambda node: node["type"] == "BaseProject", data))[0]

        target_absence_time_list = [
            self.time + t for t in project_json["absence_time_list"]
        ]
        self.absence_time_list.extend(target_absence_time_list)

        self.time = self.time + int(project_json["time"])
        self.cost_list.extend(project_json["cost_list"])

        # product
        all_component_list = self.get_all_component_list()
        product_json = list(filter(lambda node: node["type"] == "BaseProduct", data))[0]
        for c_json in product_json["component_list"]:
            c = list(
                filter(
                    lambda component: component.ID == c_json["ID"],
                    all_component_list,
                )
            )[0]
            c.state = BaseComponentState(c_json["state"])
            c.state_record_list.extend(
                [BaseComponentState(num) for num in c_json["state_record_list"]]
            )
            c.placed_workplace = c_json["placed_workplace"]
            c.placed_workplace_id_record.extend(c_json["placed_workplace_id_record"])

        # workflow
        workflow_j = list(filter(lambda node: node["type"] == "BaseWorkflow", data))[0]
        for j in workflow_j["task_list"]:
            task = list(
                filter(
                    lambda task: task.ID == j["ID"],
                    self.workflow.task_list,
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
            task.allocated_worker_list = j["allocated_worker_list"]
            task.allocated_worker_id_record.extend(j["allocated_worker_id_record"])
            task.allocated_facility_list = j["allocated_facility_list"]
            task.allocated_facility_id_record.extend(j["allocated_facility_id_record"])

        # organization
        o_json = list(filter(lambda node: node["type"] == "BaseOrganization", data))[0]
        # team
        team_list_j = o_json["team_list"]
        for team_j in team_list_j:
            team = list(
                filter(
                    lambda team: team.ID == team_j["ID"],
                    self.team_list,
                )
            )[0]
            team.cost_list.extend(team_j["cost_list"])
            for j in team_j["worker_list"]:
                worker = list(
                    filter(
                        lambda worker: worker.ID == j["ID"],
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
                    lambda workplace: workplace.ID == workplace_j["ID"],
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
                        lambda worker: worker.ID == j["ID"],
                        workplace.facility_list,
                    )
                )[0]
                facility.state = BaseWorkerState(j["state"])
                facility.state_record_list.extend(
                    [BaseWorkerState(num) for num in j["state_record_list"]],
                )
                facility.cost_list.extend(j["cost_list"])
                facility.assigned_task_list = j["assigned_task_list"]
                facility.assigned_task_id_record.extend(j["assigned_task_id_record"])

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

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        # product, workflow, organization
        for product in self.product_list:
            list_of_lines.extend(
                product.get_mermaid_diagram(
                    shape_component=shape_component,
                    link_type_str=link_type_str_component,
                    subgraph=subgraph_product,
                    subgraph_direction=subgraph_direction_product,
                )
            )
        for workflow in self.workflow_list:
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
        for team in self.team_list:
            list_of_lines.extend(
                team.get_mermaid_diagram(
                    print_worker=print_worker,
                    shape_worker=shape_worker,
                    link_type_str=link_type_str_worker,
                    subgraph=subgraph_team,
                    subgraph_direction=subgraph_direction_team,
                )
            )
        for workplace in self.workplace_list:
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
        for product in self.product_list:
            for c in product.component_list:
                for t in c.targeted_task_list:
                    list_of_lines.append(f"{c.ID}{link_type_str_component_task}{t.ID}")

        # team & workflow -> workflow
        for workflow in self.workflow_list:
            for t in workflow.task_list:
                for team in t.allocated_team_list:
                    list_of_lines.append(f"{team.ID}{link_type_str_worker_task}{t.ID}")
                for workplace in t.allocated_workplace_list:
                    list_of_lines.append(
                        f"{workplace.ID}{link_type_str_facility_task}{t.ID}"
                    )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

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
        print(f"flowchart {orientations}")
        list_of_lines = self.get_mermaid_diagram(
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
