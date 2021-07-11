#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta
import json
import datetime
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from .base_product import BaseProduct
from .base_component import BaseComponent
from .base_workflow import BaseWorkflow
from .base_task import BaseTask, BaseTaskState, BaseTaskDependency
from .base_organization import BaseOrganization
from .base_team import BaseTeam
from .base_worker import BaseWorker, BaseWorkerState
from .base_priority_rule import TaskPriorityRuleMode, sort_task_list, sort_resource_list
from enum import IntEnum
import itertools
from .base_workplace import BaseWorkplace
from .base_facility import BaseFacility, BaseFacilityState
import warnings


class SimulationMode(IntEnum):
    """SimulationMode"""

    NONE = 0
    FOWARD = 1
    BACKWARD = -1


class BaseProject(object, metaclass=ABCMeta):
    """BaseProject
    BaseProject class for expressing target project
    including product, organization and workflow.
    This class will be used as template.

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
        simulation_mode (SimulationMode, optional):
            Basic variable.
            Simulation mode.
            Defaults to None -> SimulationMode.NONE
        log_txt (str, optional):
            Basic variable.
            Log text of simulation.
            Default to None -> []
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
        simulation_mode=None,
        log_txt=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.init_datetime = (
            init_datetime if init_datetime is not None else datetime.datetime.now()
        )
        self.unit_timedelta = (
            unit_timedelta
            if unit_timedelta is not None
            else datetime.timedelta(minutes=1)
        )

        # Changeable variable on simulation
        # --
        # Basic variables
        if product is not None:
            self.product = product
        else:
            self.product = None

        if organization is not None:
            self.organization = organization
        else:
            self.organization = None

        if workflow is not None:
            self.workflow = workflow
        else:
            self.workflow = None

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

        if log_txt is not None:
            self.log_txt = log_txt
        else:
            self.log_txt = []

    def __str__(self):
        """
        Returns:
            str: time and name lists of product, organization and workflow.
        """
        return "TIME: {}\nPRODUCT\n{}\n\nORGANIZATION\n{}\n\nWORKFLOW\n{}".format(
            self.time, str(self.product), str(self.organization), str(self.workflow)
        )

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseProject.
        If `state_info` is True, the following attributes are initialized.

          - `time`

        If `log_info` is True, the following attributes are initialized.

          - `cost_list`
          - `simulation_mode`
          - `log_txt`

        BaseProduct in `product`, BaseOrganization in `organization` and BaseWorkflow in `workflow`
        are also initialized by this function.

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        if state_info:
            self.time = 0
        if log_info:
            self.cost_list = []
            self.simulation_mode = SimulationMode.NONE
            self.log_txt = []
        self.organization.initialize(state_info=state_info, log_info=log_info)
        self.workflow.initialize(state_info=state_info, log_info=log_info)
        self.product.initialize(state_info=state_info, log_info=log_info)
        # product should be initialized after initializing workflow

    def simulate(
        self,
        task_performed_mode="multi-workers",
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        error_tol=1e-10,
        print_debug=False,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
        initialize_state_info=True,
        initialize_log_info=True,
        max_time=10000,
        unit_time=1,
    ):
        """
        Simulation function for simulate this BaseProject.

        Args:
            task_performed_mode (str, optional):
                Mode of performed task in simulation.
                pDESy has the following options of this mode in simulation.

                  - multi-workers

                Defaults to "multi-workers".
            task_priority_rule (TaskPriorityRule, oprional):
                Task priority rule for simulation.
                Deraults to TaskPriorityRule.TSLACK.
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            print_debug (bool, optional):
                Whether print debug is include or not
                Defaults to False.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every time.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.
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

        # check whether implementation or target mode simulation is finish
        # Future Warning
        if print_debug:
            warnings.warn(
                "`print_debug` mode will be extinguished in the next version. "
                "Please use `output_simlog()` function for debugging.",
                FutureWarning,
            )
        # -----------------------------------------------------------------------------

        self.initialize(state_info=initialize_state_info, log_info=initialize_log_info)

        self.simulation_mode = SimulationMode.FOWARD

        while True:
            log_txt_this_time = []
            # 1. Check finished or not
            state_list = list(map(lambda task: task.state, self.workflow.task_list))
            if all(state == BaseTaskState.FINISHED for state in state_list):
                self.__record(print_debug=print_debug, log_txt=log_txt_this_time)
                return

            # Error check
            if self.time >= max_time:
                text = "Time Over! Please check your simulation model or increase max_time value"
                log_txt_this_time.append(text)
                self.log_txt.append(log_txt_this_time)
                raise Exception(text)

            # check now is business time or not
            working = True
            now_date_time = ""

            if (
                not weekend_working
                or work_start_hour is not None
                or work_finish_hour is not None
            ):
                now_date_time = self.init_datetime + self.time * self.unit_timedelta
                working = self.is_business_time(
                    now_date_time, weekend_working, work_start_hour, work_finish_hour
                )

            log_txt_this_time.append(f"{self.time},{now_date_time},{working}")
            if print_debug:
                print("---")
                print(self.time, now_date_time, working)

            # 2. Allocate free workers to READY tasks
            if working:
                self.__allocate_component_to_workplace(
                    task_priority_rule=task_priority_rule,
                    print_debug=print_debug,
                    log_txt=log_txt_this_time,
                )
                self.__allocate_single_task_workers(
                    task_priority_rule=task_priority_rule,
                    print_debug=print_debug,
                    log_txt=log_txt_this_time,
                )

            # 3. Pay cost to all workers and facilities in this time
            if working:
                cost_this_time = self.organization.add_labor_cost(only_working=True)
            else:
                cost_this_time = self.organization.add_labor_cost(
                    add_zero_to_all_workers=True, add_zero_to_all_facilities=True
                )
            self.cost_list.append(cost_this_time)

            # 4, Perform
            if working:
                if mode == 1:
                    self.__perform(print_debug=print_debug, log_txt=log_txt_this_time)

            # 5. Record
            self.__record(print_debug=print_debug, log_txt=log_txt_this_time)
            # 6. Update
            self.__update(print_debug=print_debug, log_txt=log_txt_this_time)

            self.log_txt.append(log_txt_this_time)
            self.time = self.time + unit_time

    def backward_simulate(
        self,
        task_performed_mode="multi-workers",
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        error_tol=1e-10,
        print_debug=False,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
        initialize_state_info=True,
        initialize_log_info=True,
        max_time=10000,
        unit_time=1,
        considering_due_time_of_tail_tasks=False,
        reverse_log_information=True,
    ):
        """
        Backward Simulation function for simulate this BaseProject.

        Args:
            task_performed_mode (str, optional):
                Mode of performed task in simulation.
                pDESy has the following options of this mode in simulation.
                - multi-workers
                Defaults to "multi-workers".
            task_priority_rule (TaskPriorityRule, oprional):
                Task priority rule for simulation.
                Deraults to TaskPriorityRule.TSLACK.
            worker_priority_rule (ResourcePriorityRule, oprional):
                Worker priority rule for simulation.
                Deraults to ResourcePriorityRule.SSP.
            facility_priority_rule (ResourcePriorityRule, oprional):
                Task priority rule for simulation.
                Deraults to TaskPriorityRule.TSLACK.
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            print_debug (bool, optional):
                Whether print debug is include or not
                Defaults to False.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every time.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.
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

        self.workflow.reverse_dependencies()

        autotask_removing_after_simulation = []
        try:
            if considering_due_time_of_tail_tasks:
                # Add dummy task for considering the difference of due_time
                tail_task_list = list(
                    filter(
                        lambda task: len(task.input_task_list) == 0,
                        self.workflow.task_list,
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
                        autotask_removing_after_simulation.append(auto_task)
                        self.workflow.task_list.append(auto_task)

            self.simulate(
                task_performed_mode=task_performed_mode,
                task_priority_rule=task_priority_rule,
                error_tol=error_tol,
                print_debug=print_debug,
                weekend_working=weekend_working,
                work_start_hour=work_start_hour,
                work_finish_hour=work_finish_hour,
                initialize_log_info=initialize_log_info,
                initialize_state_info=initialize_state_info,
                max_time=max_time,
                unit_time=unit_time,
            )

            if reverse_log_information:
                self.reverse_log_information()

        finally:
            self.simulation_mode = SimulationMode.BACKWARD
            for autotask in autotask_removing_after_simulation:
                for task, dependency in autotask.output_task_list:
                    task.input_task_list.remove([autotask, dependency])
                self.workflow.task_list.remove(autotask)
            self.workflow.reverse_dependencies()

    def reverse_log_information(self):
        """
        Reverse log information of all.
        """
        self.cost_list = self.cost_list[::-1]
        self.log_txt = self.log_txt[::-1]
        self.product.reverse_log_information()
        self.organization.reverse_log_information()
        self.workflow.reverse_log_information()

    def __perform(self, print_debug=False, log_txt=[]):

        worker_list = list(
            itertools.chain.from_iterable(
                list(map(lambda team: team.worker_list, self.organization.team_list))
            )
        )
        facility_list = list(
            itertools.chain.from_iterable(
                list(
                    map(
                        lambda workplace: workplace.facility_list,
                        self.organization.workplace_list,
                    )
                )
            )
        )
        log_txt.append("Allocation result in this time")
        for worker in worker_list:
            log_txt.append(
                worker.name
                + ":"
                + ",".join(
                    [assigned_task.name for assigned_task in worker.assigned_task_list]
                )
            )
        for facility in facility_list:
            log_txt.append(
                facility.name
                + ":"
                + ",".join(
                    [
                        assigned_task.name
                        for assigned_task in facility.assigned_task_list
                    ]
                )
            )
        log_txt.append("PERFORM")

        if print_debug:
            print("Allocation result in this time")

            for worker in worker_list:
                print(
                    worker.name,
                    ":",
                    [assigned_task.name for assigned_task in worker.assigned_task_list],
                )
            for facility in facility_list:
                print(
                    facility.name,
                    ":",
                    [
                        assigned_task.name
                        for assigned_task in facility.assigned_task_list
                    ],
                )
            print("PERFORM")
        self.workflow.perform(self.time)

    def __record(self, print_debug=False, log_txt=[]):
        log_txt.append("RECORD")
        if print_debug:
            print("RECORD")
        self.workflow.record()
        self.organization.record()
        self.product.record()

    def __update(self, print_debug=False, log_txt=[]):
        log_txt.append("UPDATE")
        if print_debug:
            print("UPDATE")
        self.workflow.check_state(self.time, BaseTaskState.FINISHED)
        self.product.check_state()  # product should be checked after checking workflow state
        remove_txt = self.product.check_removing_placed_workplace(
            print_debug=print_debug
        )
        if len(remove_txt) > 0:
            log_txt.extend(remove_txt)
        self.workflow.check_state(self.time, BaseTaskState.READY)
        self.workflow.update_PERT_data(self.time)

    def __allocate_component_to_workplace(
        self,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        print_debug=False,
        log_txt=[],
    ):

        # LOG: Check free workplace before setting components
        log_txt.append("ALLOCATE")
        log_txt.append("Workplace - Component before setting components in this time")
        for workplace in self.organization.workplace_list:
            log_txt.append(
                workplace.name
                + ":"
                + ",".join([c.name for c in workplace.placed_component_list])
            )
        if print_debug:
            print("ALLOCATE")
            print("Workplace - Component before setting components in this time")
            for workplace in self.organization.workplace_list:
                print(
                    workplace.name
                    + ":"
                    + ",".join([c.name for c in workplace.placed_component_list])
                )

        target_workplace_id_list = [wp.ID for wp in self.organization.workplace_list]

        # 1. Extract READY components
        ready_component_list = list(
            filter(lambda c: c.is_ready() is True, self.product.component_list)
        )

        log_txt.append("Ready Component list before allocating")
        log_txt.append(",".join([c.name for c in ready_component_list]))
        if print_debug:
            print("Ready Component list before allocating")
            print(",".join([c.name for c in ready_component_list]))

        # 2. Get ready task from READY components
        all_task_list_from_ready_component_list = list(
            itertools.chain.from_iterable(
                list(map(lambda c: c.targeted_task_list, ready_component_list))
            )
        )
        ready_task_list = list(
            filter(
                lambda t: t.state == BaseTaskState.READY,
                all_task_list_from_ready_component_list,
            )
        )

        # 3. Decide which workplace put each ready component
        ready_task_list = sort_task_list(ready_task_list, task_priority_rule)
        for ready_task in ready_task_list:
            ready_component = ready_task.target_component
            for workplace in ready_task.allocated_workplace_list:
                if workplace.ID in target_workplace_id_list:
                    if (
                        workplace.can_put(ready_component)
                        and workplace.get_total_workamount_skill(ready_task.name)
                        > 1e-10
                    ):
                        # move ready_component from None to workplace
                        pre_workplace = ready_component.placed_workplace
                        if pre_workplace is not None:
                            ready_component.set_placed_workplace(None)
                            pre_workplace.remove_placed_component(ready_component)
                        ready_component.set_placed_workplace(workplace)
                        workplace.set_placed_component(ready_component)
                        break

        # LOG: Check free workplace after setting components
        log_txt.append("Workplace - Component after setting components in this time")
        for workplace in self.organization.workplace_list:
            log_txt.append(
                workplace.name
                + ":"
                + ",".join([c.name for c in workplace.placed_component_list])
            )
        if print_debug:
            print("Workplace - Component after setting components in this time")
            for workplace in self.organization.workplace_list:
                print(
                    workplace.name
                    + ":"
                    + ",".join([c.name for c in workplace.placed_component_list])
                )

    def __allocate_single_task_workers(
        self,
        task_priority_rule=TaskPriorityRuleMode.TSLACK,
        print_debug=False,
        log_txt=[],
    ):

        # 1. Get ready task and free workers and facilities
        ready_and_working_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.READY
                or task.state == BaseTaskState.WORKING,
                self.workflow.task_list,
            )
        )

        if print_debug:
            print("Ready & Working Task List")
            print(
                [
                    (rtask.name, rtask.remaining_work_amount)
                    for rtask in ready_and_working_task_list
                ]
            )

        # Candidate allocating task list (auto_task=False)
        ready_and_working_task_list = list(
            filter(lambda task: not task.auto_task, ready_and_working_task_list)
        )

        worker_list = list(
            itertools.chain.from_iterable(
                list(map(lambda team: team.worker_list, self.organization.team_list))
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
        for task in ready_and_working_task_list:

            # Worker sorting
            free_worker_list = sort_resource_list(
                free_worker_list, task.worker_priority_rule, name=task.name
            )

            allocating_workers = list(
                filter(
                    lambda worker: worker.has_workamount_skill(task.name)
                    and self.__is_allocated_worker(worker, task),
                    free_worker_list,
                )
            )

            if task.need_facility:

                # Search candidate facilities from the list of placed_workplace
                placed_workplace = task.target_component.placed_workplace

                if placed_workplace is not None:

                    free_facility_list = list(
                        filter(
                            lambda facility: facility.state == BaseFacilityState.FREE,
                            placed_workplace.facility_list,
                        )
                    )

                    # Facility sorting
                    free_facility_list = sort_resource_list(
                        free_facility_list, task.facility_priority_rule
                    )

                    # candidate facilities
                    allocating_facilities = list(
                        filter(
                            lambda facility: facility.has_workamount_skill(task.name)
                            and self.__is_allocated_facility(facility, task),
                            free_facility_list,
                        )
                    )

                    for facility in allocating_facilities:
                        for worker in allocating_workers:
                            if task.can_add_resources(worker=worker, facility=facility):
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
                for worker in allocating_workers:
                    if task.can_add_resources(worker=worker):
                        task.allocated_worker_list.append(worker)
                        worker.assigned_task_list.append(task)
                        free_worker_list = [
                            w for w in free_worker_list if w.ID != worker.ID
                        ]

        # 4. Update state of task newly allocated workers and facilities (READY -> WORKING)
        self.workflow.check_state(self.time, BaseTaskState.WORKING)
        self.product.check_state()  # product should be checked after checking workflow state

    def __is_allocated_worker(self, worker, task):
        team = list(
            filter(lambda team: team.ID == worker.team_id, self.organization.team_list)
        )[0]
        return task in team.targeted_task_list

    def __is_allocated_facility(self, facility, task):
        workplace = list(
            filter(
                lambda workplace: workplace.ID == facility.workplace_id,
                self.organization.workplace_list,
            )
        )[0]
        return task in workplace.targeted_task_list

    def is_business_time(
        self,
        target_datetime: datetime.datetime,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
    ):
        """
        Check whether target_datetime is business time or not in this project.

        Args:
            target_datetime (datetime.datetime):
                Target datetime of checking business time or not.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every time.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.

        Returns:
            bool: whether target_datetime is business time or not.
        """
        if not weekend_working:
            if target_datetime.weekday() >= 5:
                return False
            else:
                if work_start_hour is not None and work_finish_hour is not None:
                    if (
                        target_datetime.hour >= work_start_hour
                        and target_datetime.hour <= work_finish_hour
                    ):
                        return True
                    else:
                        return False
                else:
                    return True

        else:
            if work_start_hour is not None and work_finish_hour is not None:
                if (
                    target_datetime.hour >= work_start_hour
                    and target_datetime.hour <= work_finish_hour
                ):
                    return True
                else:
                    return False
            else:
                return True

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
        Method for creating Gantt chart by plotly.
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

        TODO:
            Now, save_fig_path can be utilized only json and html format.
            Saving figure png, jpg, svg file is not implemented...
        """
        colors = (
            colors
            if colors is not None
            else dict(
                Component="rgb(246, 37, 105)",
                Task="rgb(146, 237, 5)",
                Worker="rgb(46, 137, 205)",
                Facility="rgb(46, 137, 205)",
            )
        )
        index_col = index_col if index_col is not None else "Type"
        df = []
        df.extend(
            self.product.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            )
        )
        df.extend(
            self.workflow.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            ),
        )
        df.extend(
            self.organization.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
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
            # fig.write_image(save_fig_path)
            dot_point = save_fig_path.rfind(".")

            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            elif save_mode in ["png", "jpg", "jpeg", "webp", "svg", "pdf", "eps"]:
                # We need to install plotly/orca
                # and set `plotly.io.orca.config.executable = '/path/to/orca'``
                # fig_go_figure = go.Figure(fig)
                # fig_go_figure.write_html(save_fig_path)
                save_mode = "error"

            if save_mode == "error":
                warnings.warn(
                    "Sorry, the function of saving this type is not implemented now. "
                    "pDESy is only support html and json in saving plotly."
                )

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
        Gp = self.product.get_networkx_graph()
        Gw = self.workflow.get_networkx_graph()
        Go = self.organization.get_networkx_graph(
            view_workers=view_workers, view_facilities=view_facilities
        )
        G = nx.compose_all([Gp, Gw, Go])

        # add edge between product and workflow
        for c in self.product.component_list:
            for task in c.targeted_task_list:
                G.add_edge(c, task)

        # add edge between workflow and team in organization
        for team in self.organization.team_list:
            for task in team.targeted_task_list:
                G.add_edge(team, task)

        if view_workers:
            for team in self.organization.team_list:
                for w in team.worker_list:
                    # G.add_node(w)
                    G.add_edge(team, w)

        # add edge between workflow and workplace in organization
        for workplace in self.organization.workplace_list:
            for task in workplace.targeted_task_list:
                G.add_edge(workplace, task)

        if view_facilities:
            for workplace in self.organization.workplace_list:
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
        Draw networkx

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
            nodelist=self.product.component_list,
            node_color=component_node_color,
        )
        # Workflow
        normal_task_list = [
            task for task in self.workflow.task_list if not task.auto_task
        ]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=normal_task_list,
            node_color=task_node_color,
        )
        auto_task_list = [task for task in self.workflow.task_list if task.auto_task]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=auto_task_list,
            node_color=auto_task_node_color,
        )
        # Organization - Team
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=self.organization.team_list,
            node_color=team_node_color,
            # **kwds,
        )
        if view_workers:

            worker_list = []
            for team in self.organization.team_list:
                worker_list.extend(team.worker_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=worker_list,
                node_color=worker_node_color,
                # **kwds,
            )

        # Organization - Workplace
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=self.organization.workplace_list,
            node_color=workplace_node_color,
            # **kwds,
        )
        if view_facilities:

            facility_list = []
            for workplace in self.organization.workplace_list:
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
            marker=dict(
                color=component_node_color,
                size=node_size,
            ),
        )

        task_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=task_node_color,
                size=node_size,
            ),
        )

        auto_task_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=auto_task_node_color,
                size=node_size,
            ),
        )

        team_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=team_node_color,
                size=node_size,
            ),
        )

        worker_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=worker_node_color,
                size=node_size,
            ),
        )

        workplace_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=workplace_node_color,
                size=node_size,
            ),
        )

        facility_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=facility_node_color,
                size=node_size,
            ),
        )

        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0, color="#888"), hoverinfo="none", mode="lines"
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
        Draw plotly network

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

        TODO:
            Now, save_fig_path can be utilized only json and html format.
            Saving figure png, jpg, svg file is not implemented...
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
                    dict(
                        ax=edge_trace["x"][index * 2],
                        ay=edge_trace["y"][index * 2],
                        axref="x",
                        ayref="y",
                        x=edge_trace["x"][index * 2 + 1],
                        y=edge_trace["y"][index * 2 + 1],
                        xref="x",
                        yref="y",
                        showarrow=True,
                        arrowhead=5,
                    )
                    for index in range(0, int(len(edge_trace["x"]) / 2))
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        if save_fig_path is not None:
            # fig.write_image(save_fig_path)
            dot_point = save_fig_path.rfind(".")

            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            elif save_mode in ["png", "jpg", "jpeg", "webp", "svg", "pdf", "eps"]:
                # We need to install plotly/orca
                # and set `plotly.io.orca.config.executable = '/path/to/orca'``
                # fig_go_figure = go.Figure(fig)
                # fig_go_figure.write_html(save_fig_path)
                save_mode = "error"

            if save_mode == "error":
                warnings.warn(
                    "Sorry, the function of saving this type is not implemented now. "
                    "pDESy is only support html and json in saving plotly."
                )

        return fig

    def output_simlog(self, file_path):
        """
        Create simulation log text file.
        Args:
            file_path (str):
                File path for saving simulation log.
        """
        res = "\n".join(",".join(map(str, x)) for x in self.log_txt)
        with open(file_path, "w") as f:
            f.write(res)

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
                "type": "BaseProject",
                "init_datetime": self.init_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "unit_timedelta": str(self.unit_timedelta.total_seconds()),
                "time": self.time,
                "cost_list": self.cost_list,
                "simulation_mode": int(self.simulation_mode),
                "log_txt": self.log_txt,
            }
        )
        dict_data["pDESy"].append(self.product.export_dict_json_data())
        dict_data["pDESy"].append(self.workflow.export_dict_json_data())
        dict_data["pDESy"].append(self.organization.export_dict_json_data())
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
        self.init_datetime = datetime.datetime.strptime(
            project_json["init_datetime"], "%Y-%m-%d %H:%M:%S"
        )
        self.unit_timedelta = datetime.timedelta(
            seconds=float(project_json["unit_timedelta"])
        )
        self.time = project_json["time"]
        self.cost_list = project_json["cost_list"]
        self.simulation_mode = SimulationMode(project_json["simulation_mode"])
        self.log_txt = project_json["log_txt"]
        # 1. read all node and attr only considering ID info
        # product
        product_json = list(filter(lambda node: node["type"] == "BaseProduct", data))[0]
        product = BaseProduct(component_list=[])
        product.read_json_data(product_json)
        self.product = product
        # workflow
        workflow_json = list(filter(lambda node: node["type"] == "BaseWorkflow", data))[
            0
        ]
        workflow = BaseWorkflow(task_list=[])
        workflow.read_json_data(workflow_json)
        self.workflow = workflow
        # organization
        organization_json = list(
            filter(lambda node: node["type"] == "BaseOrganization", data)
        )[0]
        organization = BaseOrganization(team_list=[], workplace_list=[])
        organization.read_json_data(organization_json)
        self.organization = organization

        # 2. update ID info to instance info
        # 2-1. component
        for c in self.product.component_list:
            c.parent_component_list = [
                self.product.get_component_list(ID=ID)[0]
                for ID in c.parent_component_list
            ]
            c.child_component_list = [
                self.product.get_component_list(ID=ID)[0]
                for ID in c.child_component_list
            ]
            c.targeted_task_list = [
                self.workflow.get_task_list(ID=ID)[0] for ID in c.targeted_task_list
            ]
            c.placed_workplace = (
                self.organization.get_workplace_list(ID=c.placed_workplace)[0]
                if c.placed_workplace is not None
                else None
            )
        # 2-2. task
        for t in self.workflow.task_list:
            t.input_task_list = [
                [
                    self.workflow.get_task_list(ID=ID)[0],
                    BaseTaskDependency(dependency_number),
                ]
                for (ID, dependency_number) in t.input_task_list
            ]
            t.output_task_list = [
                [
                    self.workflow.get_task_list(ID=ID)[0],
                    BaseTaskDependency(dependency_number),
                ]
                for (ID, dependency_number) in t.output_task_list
            ]
            t.allocated_team_list = [
                self.organization.get_team_list(ID=ID)[0]
                for ID in t.allocated_team_list
            ]
            t.allocated_workplace_list = [
                self.organization.get_workplace_list(ID=ID)[0]
                for ID in t.allocated_workplace_list
            ]
            t.target_component = (
                self.product.get_component_list(ID=t.target_component)[0]
                if t.target_component is not None
                else None
            )
            t.allocated_worker_list = [
                self.organization.get_worker_list(ID=ID)[0]
                for ID in t.allocated_worker_list
            ]
            t.allocated_facility_list = [
                self.organization.get_facility_list(ID=ID)[0]
                for ID in t.allocated_facility_list
            ]
        # 2-3. organziation
        # 2-3-1. team
        for x in self.organization.team_list:
            x.targeted_task_list = [
                self.workflow.get_task_list(ID=ID)[0] for ID in x.targeted_task_list
            ]
            x.parent_team = (
                self.organization.get_team_list(ID=x.parent_team)[0]
                if x.parent_team is not None
                else None
            )
            for w in x.worker_list:
                w.assigned_task_list = [
                    self.workflow.get_task_list(ID=ID)[0] for ID in w.assigned_task_list
                ]

        # 2-3-2. workplace
        for x in self.organization.workplace_list:
            x.targeted_task_list = [
                self.workflow.get_task_list(ID=ID)[0] for ID in x.targeted_task_list
            ]
            x.parent_workplace = (
                self.organization.get_workplace_list(ID=x.parent_workplace)[0]
                if x.parent_workplace is not None
                else None
            )
            x.placed_component_list = [
                self.product.get_component_list(ID=ID)[0]
                for ID in x.placed_component_list
            ]
            for f in x.facility_list:
                f.assigned_task_list = [
                    self.workflow.get_task_list(ID=ID)[0] for ID in f.assigned_task_list
                ]

    # ---
    # READ FUNCTION
    # ---

    # def read_pDESy_web_json(self, file_path: str, encoding=None):
    #     """
    #     Read json file from pDESy.org.
    #     This method is not stable now.

    #     Args:
    #         file_path (str):
    #             file path by getting pDESy.org
    #         encoding ([type], optional):
    #             Defaults to None -> utf-8.
    #     TODO:
    #         pDESy.org for describing project in web browser should be developed...
    #     """
    #     encoding = encoding if encoding is not None else "utf-8"
    #     pdes_json = open(file_path, "r", encoding=encoding)
    #     data = json.load(pdes_json)

    #     # Get Product information including Components without dependency
    #     cd_list = list(filter(lambda node: node["type"] == "Component", data))
    #     component_list = [
    #         BaseComponent(
    #             cd["name"],
    #             ID=cd["id"],
    #             error_tolerance=float(cd["userData"]["errorTolerance"]),
    #         )
    #         for cd in cd_list
    #     ]

    #     # Get Workflow information including Tasks without dependency
    #     td_list = list(filter(lambda node: node["type"] == "Task", data))
    #     task_list = [
    #         BaseTask(
    #             td["name"],
    #             ID=td["id"],
    #             default_work_amount=float(td["userData"]["workAmount"]),
    #             default_progress=float(td["userData"]["progress"]),
    #             additional_work_amount=float(td["userData"]["additionalWorkAmount"]),
    #         )
    #         for td in td_list
    #     ]

    #     # Get Organization information including Teams without dependency
    #     team_list = []
    #     ted_list = list(filter(lambda node: node["type"] == "Team", data))
    #     for team_data in ted_list:
    #         worker_list = []
    #         worker_list_data = team_data["userData"]["WorkerList"]
    #         if type(worker_list_data["Worker"]) is dict:
    #             worker_list_data["Worker"] = [worker_list_data["Worker"]]
    #         for worker_data in worker_list_data["Worker"]:
    #             work_amount_skill_mean_info = {}
    #             work_amount_skill_sd_info = {}
    #             quality_skill_mean_info = {}
    #             # quality_skill_sd_info = {}
    #             if "WorkAmountSkill" in worker_data:
    #                 if type(worker_data["WorkAmountSkill"]) is list:
    #                     for skill_data in worker_data["WorkAmountSkill"]:
    #                         work_amount_skill_mean_info[skill_data["-name"]] = float(
    #                             skill_data["-value"]
    #                         )
    #                         work_amount_skill_sd_info[skill_data["-name"]] = float(
    #                             skill_data["-value_sd"]
    #                         )
    #                 elif type(worker_data["WorkAmountSkill"]) is dict:
    #                     work_amount_skill_mean_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value"])
    #                     work_amount_skill_sd_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
    #             # if "QualitySkill" in worker_data:
    #             #     if type(worker_data["QualitySkill"]) is list:
    #             #         for skill_data in worker_data["QualitySkill"]:
    #             #             quality_skill_mean_info[skill_data["-name"]] = float(
    #             #                 skill_data["-value"]
    #             #             )
    #             #             # quality_skill_sd_info[skill_data['-name']] =
    #             #             # float(skill_data['-value_sd'])
    #             #     elif type(worker_data["QualitySkill"]) is dict:
    #             #         quality_skill_mean_info[
    #             #             worker_data["QualitySkill"]["-name"]
    #             #         ] = float(worker_data["QualitySkill"]["-value"])
    #             worker_list.append(
    #                 BaseWorker(
    #                     worker_data["Name"],
    #                     team_id=team_data["id"],
    #                     cost_per_time=float(worker_data["Cost"]),
    #                     workamount_skill_mean_map=work_amount_skill_mean_info,
    #                     workamount_skill_sd_map=work_amount_skill_sd_info,
    #                     quality_skill_mean_map=quality_skill_mean_info,
    #                 )
    #             )
    #         team_list.append(
    #             BaseTeam(team_data["name"],ID=team_data["id"],worker_list=worker_list)
    #         )

    #     # Get Links information including
    #     # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
    #     l_list = list(filter(lambda node: node["type"] == "draw2d.Connection", data))
    #     for link in l_list:
    #         org_id = link["source"]["node"]
    #         org_type = list(filter(lambda node: node["id"]==org_id, data))[0]["type"]
    #         dst_id = link["target"]["node"]
    #         dst_type = list(filter(lambda node: node["id"]==dst_id, data))[0]["type"]
    #         if org_type == "Component" and dst_type == "Component":
    #             org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
    #             dst_c = list(filter(lambda c: c.ID == dst_id, component_list))[0]
    #             org_c.parent_component_list.append(dst_c)
    #             dst_c.child_component_list.append(org_c)
    #         elif org_type == "Task" and dst_type == "Task":
    #             org_task = list(filter(lambda c: c.ID == org_id, task_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
    #             org_task.output_task_list.append(dst_task)
    #             dst_task.input_task_list.append(org_task)
    #         elif org_type == "Team" and dst_type == "Team":
    #             org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
    #             dst_team = list(filter(lambda c: c.ID == dst_id, team_list))[0]
    #             # org_task.output_task_id_list.append(dst_task.ID)
    #             dst_team.parent_team_id = org_team.ID
    #         elif org_type == "Component" and dst_type == "Task":
    #             org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
    #             org_c.targeted_task_list.append(dst_task)
    #             dst_task.target_component_list.append(org_c)
    #         elif org_type == "Team" and dst_type == "Task":
    #             org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
    #             org_team.targeted_task_list.append(dst_task)
    #             dst_task.allocated_team_list.append(org_team)

    #     # Aggregate
    #     self.product = BaseProduct(component_list)
    #     self.workflow = BaseWorkflow(task_list)
    #     self.organization = BaseOrganization(team_list)

    # def read_pDES_json(self, file_path: str, encoding=None):
    #     """
    #     Read json file converted from pDES file.
    #     This method is not stable now.

    #     Args:
    #         file_path (str):
    #             file path by getting pDES and converted to json
    #         encoding ([type], optional):
    #             Defaults to None -> utf-8.
    #     """
    #     encoding = encoding if encoding is not None else "utf-8"
    #     pdes_json = open(file_path, "r", encoding=encoding)
    #     data = json.load(pdes_json)

    #     # Get Product information including Components without dependency
    #     cd_list = data["ProjectDiagram"]["NodeElementList"]["ComponentNode"]
    #     component_list = [
    #         BaseComponent(
    #             cd["Name"], ID=cd["-id"],
    #         )
    #         for cd in cd_list
    #     ]

    #     # Get Workflow information including Tasks without dependency
    #     td_list = data["ProjectDiagram"]["NodeElementList"]["TaskNode"]
    #     task_list = [
    #         BaseTask(
    #             td["Name"],
    #             ID=td["-id"],
    #             default_work_amount=float(td["WorkAmount"]),
    #             default_progress=float(td["Progress"]),
    #             # additional_work_amount=float(td["AdditionalWorkAmount"]),
    #         )
    #         for td in td_list
    #     ]

    #     # Get Organization information including Teams without dependency
    #     team_list = []
    #     ted_list = data["ProjectDiagram"]["NodeElementList"]["TeamNode"]
    #     for team_data in ted_list:
    #         worker_list = []
    #         worker_list_data = team_data["WorkerList"]
    #         if type(worker_list_data["Worker"]) is dict:
    #             worker_list_data["Worker"] = [worker_list_data["Worker"]]
    #         for worker_data in worker_list_data["Worker"]:
    #             work_amount_skill_mean_info = {}
    #             work_amount_skill_sd_info = {}
    #             quality_skill_mean_info = {}
    #             # quality_skill_sd_info = {}
    #             if "WorkAmountSkill" in worker_data:
    #                 if type(worker_data["WorkAmountSkill"]) is list:
    #                     for skill_data in worker_data["WorkAmountSkill"]:
    #                         work_amount_skill_mean_info[skill_data["-name"]] = float(
    #                             skill_data["-value"]
    #                         )
    #                         work_amount_skill_sd_info[skill_data["-name"]] = float(
    #                             skill_data["-value_sd"]
    #                         )
    #                 elif type(worker_data["WorkAmountSkill"]) is dict:
    #                     work_amount_skill_mean_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value"])
    #                     work_amount_skill_sd_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
    #             # if "QualitySkill" in worker_data:
    #             #     if type(worker_data["QualitySkill"]) is list:
    #             #         for skill_data in worker_data["QualitySkill"]:
    #             #             quality_skill_mean_info[skill_data["-name"]] = float(
    #             #                 skill_data["-value"]
    #             #             )
    #             #             # quality_skill_sd_info[skill_data['-name']]
    #             #             #  = float(skill_data['-value_sd'])
    #             #     elif type(worker_data["QualitySkill"]) is dict:
    #             #         quality_skill_mean_info[
    #             #             worker_data["QualitySkill"]["-name"]
    #             #         ] = float(worker_data["QualitySkill"]["-value"])
    #             worker_list.append(
    #                 BaseWorker(
    #                     worker_data["Name"],
    #                     team_id=team_data["-id"],
    #                     cost_per_time=float(worker_data["Cost"]),
    #                     workamount_skill_mean_map=work_amount_skill_mean_info,
    #                     workamount_skill_sd_map=work_amount_skill_sd_info,
    #                     quality_skill_mean_map=quality_skill_mean_info,
    #                 )
    #             )
    #         team_list.append(
    #             BaseTeam(
    #                 team_data["Name"], ID=team_data["-id"], worker_list=worker_list
    #             )
    #         )
    #     self.organization = BaseOrganization(team_list)

    #     # Get Links information including
    #     # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
    #     l_list = data["ProjectDiagram"]["LinkList"]["Link"]
    #     for link in l_list:
    #         if link["-type"] == "ComponentLink":
    #             org_c = list(filter(lambda c: c.ID==link["-org"], component_list))[0]
    #             dst_c = list(filter(lambda c: c.ID==link["-dst"], component_list))[0]
    #             org_c.parent_component_list.append(dst_c)
    #             dst_c.child_component_list.append(org_c)
    #         elif link["-type"] == "TaskLink":
    #             org_task = list(filter(lambda c: c.ID == link["-org"], task_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
    #             org_task.output_task_list.append(dst_task)
    #             dst_task.input_task_list.append(org_task)
    #         elif link["-type"] == "TeamLink":
    #             org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
    #             dst_team = list(filter(lambda c: c.ID == link["-dst"], team_list))[0]
    #             # org_task.output_task_id_list.append(dst_task.ID)
    #             dst_team.get_work_amount_skill_progress_team_id = org_team.ID
    #         elif link["-type"] == "TargetComponentLink":
    #             org_c = list(filter(lambda c: c.ID==link["-org"], component_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
    #             org_c.targeted_task_list.append(dst_task)
    #             dst_task.target_component_list.append(org_c)
    #         elif link["-type"] == "AllocationLink":
    #             org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
    #             org_team.targeted_task_list.append(dst_task)
    #             dst_task.allocated_team_list.append(org_team)

    #     # Aggregate
    #     self.product = BaseProduct(component_list)
    #     self.workflow = BaseWorkflow(task_list)
    #     self.organization = BaseOrganization(team_list)
