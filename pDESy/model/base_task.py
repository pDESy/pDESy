#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_task."""

import abc
import datetime
import uuid
from enum import IntEnum

from .base_priority_rule import ResourcePriorityRuleMode, WorkplacePriorityRuleMode


class BaseTaskState(IntEnum):
    """BaseTaskState."""

    NONE = 0
    READY = 1
    WORKING = 2
    WORKING_ADDITIONALLY = 3
    FINISHED = -1


class BaseTaskDependency(IntEnum):
    """BaseTaskDependency."""

    FS = 0  # Finish to Start
    SS = 1  # Start to Start
    FF = 2  # Finish to Finish
    SF = 3  # Finish to Start


class BaseTask(object, metaclass=abc.ABCMeta):
    """BaseTask.

    BaseTask class for expressing target workflow.
    This class will be used as template.

    Args:
        name (str, optional):
            Basic parameter.
            Name of this task.
            Defaults to None -> "New Task".
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None -> str(uuid.uuid4()).
        default_work_amount (float, optional):
            Basic parameter.
            Default workamount of this BaseTask.
            Defaults to None -> 10.0.
        work_amount_progress_of_unit_step_time (float, optional)
            Baseline of work amount progress of unit step time.
            Default to None -> 1.0.
        input_task_list (List[BaseTask,BaseTaskDependency], optional):
            Basic parameter.
            List of input BaseTask and type of dependency(FS, SS, SF, F/F).
            Defaults to None -> [].
        output_task_list (List[BaseTask,BaseTaskDependency], optional):
            Basic parameter.
            List of input BaseTask and type of dependency(FS, SS, SF, F/F).
            Defaults to None -> [].
        allocated_team_list (List[BaseTeam], optional):
            Basic parameter.
            List of allocated BaseTeam
            Defaults to None -> [].
        allocated_workplace_list (List[BaseWorkplace], optional):
            Basic parameter.
            List of allocated BaseWorkplace.
            Defaults to None -> [].
        parent_workflow (BaseWorkflow, optional):
            Basic parameter.
            Parent workflow.
            Defaults to None.
        workplace_priority_rule (WorkplacePriorityRuleMode, optional):
            Workplace priority rule for simulation.
            Defaults to WorkplacePriorityRuleMode.FSS.
        worker_priority_rule (ResourcePriorityRule, optional):
            Worker priority rule for simulation.
            Defaults to ResourcePriorityRule.SSP.
        facility_priority_rule (ResourcePriorityRule, optional):
            Task priority rule for simulation.
            Defaults to TaskPriorityRule.TSLACK.
        need_facility (bool, optional):
            Basic parameter.
            Whether one facility is needed for performing this task or not.
            Defaults to False
        target_component (BaseComponent, optional):
            Basic parameter.
            Target BaseComponent.
            Defaults to None.
        default_progress (float, optional):
            Basic parameter.
            Progress before starting simulation (0.0 ~ 1.0)
            Defaults to None -> 0.0.
        due_time (int, optional):
            Basic parameter.
            Defaults to None -> int(-1).
        auto_task (bool, optional):
            Basic parameter.
            If True, this task is performed automatically
            even if there are no allocated workers.
            Defaults to False.
        fixing_allocating_worker_id_list (List[str], optional):
            Basic parameter.
            Allocating worker ID list for fixing allocation in simulation.
            Defaults to None.
        fixing_allocating_facility_id_list (List[str], optional):
            Basic parameter.
            Allocating facility ID list for fixing allocation in simulation.
            Defaults to None.
        est (float, optional):
            Basic variable.
            Earliest start time of CPM. This will be updated step by step.
            Defaults to 0.0.
        eft (float, optional):
            Basic variable.
            Earliest finish time of CPM. This will be updated step by step.
            Defaults to 0.0.
        lst (float, optional):
            Basic variable.
            Latest start time of CPM. This will be updated step by step.
            Defaults to -1.0.
        lft (float, optional):
            Basic variable.
            Latest finish time of CPM. This will be updated step by step.
            Defaults to -1.0.
        remaining_work_amount (float, optional):
            Basic variable.
            Remaining workamount in simulation.
            Defaults to None -> default_work_amount * (1.0 - default_progress).
        remaining_work_amount_record_list (List[float], optional):
            Basic variable.
            Record of remaining workamount in simulation.
            Defaults to None -> [].
        state (BaseTaskState, optional):
            Basic variable.
            State of this task in simulation.
            Defaults to BaseTaskState.NONE.
        state_record_list (List[BaseTaskState], optional):
            Basic variable.
            Record list of state.
            Defaults to None -> [].
        allocated_worker_list (List[BaseWorker], optional):
            Basic variable.
            State of allocating worker list in simulation.
            Defaults to None -> [].
        allocated_worker_id_record (List[List[str]], optional):
            Basic variable.
            State of allocating worker id list in simulation.
            Defaults to None -> [].
        allocated_facility_list (List[BaseFacility], optional):
            Basic variable.
            State of allocating facility list in simulation.
            Defaults to None -> [].
        allocated_facility_id_record (List[List[str]], optional):
            Basic variable.
            State of allocating facility id list in simulation.
            Defaults to None -> [].
        additional_work_amount (float, optional):
            Advanced parameter.
            Defaults to None.
        additional_task_flag (bool, optional):
            Advanced variable.
            Defaults to False.
        actual_work_amount (float, optional):
            Advanced variable.
            Default to None -> default_work_amount*(1.0-default_progress)
    """

    def __init__(
        self,
        # Basic parameters
        name=None,
        ID=None,
        default_work_amount=None,
        work_amount_progress_of_unit_step_time=None,
        input_task_list=None,
        output_task_list=None,
        allocated_team_list=None,
        allocated_workplace_list=None,
        parent_workflow=None,
        workplace_priority_rule=WorkplacePriorityRuleMode.FSS,
        worker_priority_rule=ResourcePriorityRuleMode.MW,
        facility_priority_rule=ResourcePriorityRuleMode.SSP,
        need_facility=False,
        target_component=None,
        default_progress=None,
        due_time=None,
        auto_task=False,
        fixing_allocating_worker_id_list=None,
        fixing_allocating_facility_id_list=None,
        # Basic variables
        est=0.0,
        eft=0.0,
        lst=-1.0,
        lft=-1.0,
        remaining_work_amount=None,
        remaining_work_amount_record_list=None,
        state=BaseTaskState.NONE,
        state_record_list=None,
        allocated_worker_list=None,
        allocated_worker_id_record=None,
        allocated_facility_list=None,
        allocated_facility_id_record=None,
        # Advanced parameters for customized simulation
        additional_work_amount=None,
        # Advanced variables for customized simulation
        additional_task_flag=False,
        actual_work_amount=None,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Task"
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.default_work_amount = (
            default_work_amount if default_work_amount is not None else 10.0
        )
        self.work_amount_progress_of_unit_step_time = (
            work_amount_progress_of_unit_step_time
            if work_amount_progress_of_unit_step_time is not None
            else 1.0
        )
        self.input_task_list = input_task_list if input_task_list is not None else []
        self.output_task_list = output_task_list if output_task_list is not None else []
        self.allocated_team_list = (
            allocated_team_list if allocated_team_list is not None else []
        )
        self.allocated_workplace_list = (
            allocated_workplace_list if allocated_workplace_list is not None else []
        )
        self.parent_workflow = parent_workflow if parent_workflow is not None else None
        self.workplace_priority_rule = (
            workplace_priority_rule
            if workplace_priority_rule is not None
            else WorkplacePriorityRuleMode.FSS
        )
        self.worker_priority_rule = (
            worker_priority_rule
            if worker_priority_rule is not None
            else ResourcePriorityRuleMode.SSP
        )
        self.facility_priority_rule = (
            facility_priority_rule
            if facility_priority_rule is not None
            else ResourcePriorityRuleMode.SSP
        )
        self.need_facility = need_facility
        self.target_component = (
            target_component if target_component is not None else None
        )
        self.default_progress = (
            default_progress if default_progress is not None else 0.0
        )
        self.due_time = due_time if due_time is not None else int(-1)
        self.auto_task = auto_task if auto_task is not False else False
        self.fixing_allocating_worker_id_list = (
            fixing_allocating_worker_id_list
            if fixing_allocating_worker_id_list is not None
            else None
        )
        self.fixing_allocating_facility_id_list = (
            fixing_allocating_facility_id_list
            if fixing_allocating_facility_id_list is not None
            else None
        )
        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        self.est = est if est != 0.0 else 0.0  # Earliest start time
        self.eft = eft if eft != 0.0 else 0.0  # Earliest finish time
        self.lst = lst if lst != 0.0 else -1.0  # Latest start time
        self.lft = lft if lft != 0.0 else -1.0  # Latest finish time
        if remaining_work_amount is not None:
            self.remaining_work_amount = remaining_work_amount
        else:
            self.remaining_work_amount = self.default_work_amount * (
                1.0 - self.default_progress
            )

        if remaining_work_amount_record_list is not None:
            self.remaining_work_amount_record_list = remaining_work_amount_record_list
        else:
            self.remaining_work_amount_record_list = []

        if state is not BaseTaskState.NONE:
            self.state = state
        else:
            self.state = BaseTaskState.NONE

        if state_record_list is not None:
            self.state_record_list = state_record_list
        else:
            self.state_record_list = []

        if allocated_worker_list is not None:
            self.allocated_worker_list = allocated_worker_list
        else:
            self.allocated_worker_list = []

        if allocated_worker_id_record is not None:
            self.allocated_worker_id_record = allocated_worker_id_record
        else:
            self.allocated_worker_id_record = []

        if allocated_facility_list is not None:
            self.allocated_facility_list = allocated_facility_list
        else:
            self.allocated_facility_list = []

        if allocated_facility_id_record is not None:
            self.allocated_facility_id_record = allocated_facility_id_record
        else:
            self.allocated_facility_id_record = []

        # --
        # Advanced parameter for customized simulation
        self.additional_work_amount = (
            additional_work_amount if additional_work_amount is not None else 0.0
        )
        # --
        # Advanced variables for customized simulation
        if additional_task_flag is not False:
            self.additional_task_flag = additional_task_flag
        else:
            self.additional_task_flag = False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )

    def __str__(self):
        """str.

        Returns:
            str: name of BaseTask
        Examples:
            >>> task = BaseTask("task1")
            >>> print(task)
            'task1'
        """
        return "{}".format(self.name)

    def export_dict_json_data(self):
        """
        Export the information of this task to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
            default_work_amount=self.default_work_amount,
            work_amount_progress_of_unit_step_time=self.work_amount_progress_of_unit_step_time,
            input_task_list=[
                (task.ID, int(dependency)) for task, dependency in self.input_task_list
            ],
            output_task_list=[
                (task.ID, int(dependency)) for task, dependency in self.output_task_list
            ],
            allocated_team_list=[team.ID for team in self.allocated_team_list],
            allocated_workplace_list=[
                workplace.ID for workplace in self.allocated_workplace_list
            ],
            need_facility=self.need_facility,
            target_component=(
                self.target_component.ID if self.target_component is not None else None
            ),
            default_progress=self.default_progress,
            due_time=self.due_time,
            auto_task=self.auto_task,
            fixing_allocating_worker_id_list=self.fixing_allocating_worker_id_list,
            fixing_allocating_facility_id_list=self.fixing_allocating_facility_id_list,
            est=self.est,
            eft=self.eft,
            lst=self.lst,
            lft=self.lft,
            remaining_work_amount=self.remaining_work_amount,
            remaining_work_amount_record_list=[
                float(rwa) for rwa in self.remaining_work_amount_record_list
            ],
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            allocated_worker_list=[worker.ID for worker in self.allocated_worker_list],
            allocated_worker_id_record=self.allocated_worker_id_record,
            allocated_facility_list=[
                facility.ID for facility in self.allocated_facility_list
            ],
            allocated_facility_id_record=self.allocated_facility_id_record,
        )
        return dict_json_data

    def append_input_task(self, input_task, task_dependency_mode=BaseTaskDependency.FS):
        """
        Append input task to `input_task_list`.

        Args:
            input_task (BaseTask):
                Input BaseTask
            task_dependency_mode (BaseTaskDependency, optional):
                Task Dependency mode between input_task to this task.
                Default to BaseTaskDependency.FS
        Examples:
            >>> task = BaseTask("task")
            >>> print([input_t.name for input_t in task.input_task_list])
            []
            >>> task1 = BaseTask("task1")
            >>> task.append_input_task(task1)
            >>> print([input_t.name for input_t in task.input_task_list])
            ['task1']
            >>> print([parent_t.name for parent_t in task1.output_task_list])
            ['task']
        """
        self.input_task_list.append([input_task, task_dependency_mode])
        input_task.output_task_list.append([self, task_dependency_mode])
        input_task.parent_workflow = self.parent_workflow

    def extend_input_task_list(
        self, input_task_list, task_dependency_mode=BaseTaskDependency.FS
    ):
        """
        Extend the list of input tasks to `input_task_list`.

        Args:
            input_task_list (List[BaseTask]):
                List of input BaseTask
            task_dependency_mode (BaseTaskDependency):
                Task Dependency mode between input_task to this task.
        Examples:
            >>> task = BaseTask("task")
            >>> print([input_t.name for input_t in task.input_task_list])
            []
            >>> task1 = BaseTask("task1")
            >>> task.append_input_task(task1)
            >>> print([input_t.name for input_t in task.input_task_list])
            ['task1']
            >>> print([parent_t.name for parent_t in task1.output_task_list])
            ['task']
        """
        for input_task in input_task_list:
            self.input_task_list.append([input_task, task_dependency_mode])
            input_task.output_task_list.append([self, task_dependency_mode])
            input_task.parent_workflow = self.parent_workflow

    def initialize(self, error_tol=1e-10, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseTask.

        If `state_info` is True, the following attributes are initialized.

          - `est`
          - `eft`
          - `lst`
          - `lft`
          - `remaining_work_amount`
          - `state`
          - `allocated_worker_list`
          - `allocated_facility_list`
          - `additional_task_flag`
          - `actual_work_amount`

        If `log_info` is True the following attributes are initialized.

            - `remaining_work_amount_record_list`
            - `state_record_list`
            - `allocated_worker_id_record`
            - `allocated_facility_id_record`

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaults to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
            error_tol (float):
                error toleration of work amount for checking the state of this task.
                Defaults to 1e-10.
        """
        if state_info:
            self.est = 0.0  # Earliest start time
            self.eft = 0.0  # Earliest finish time
            self.lst = -1.0  # Latest start time
            self.lft = -1.0  # Latest finish time
            self.remaining_work_amount = self.default_work_amount * (
                1.0 - self.default_progress
            )
            self.state = BaseTaskState.NONE
            self.allocated_worker_list = []
            self.allocated_facility_list = []
            self.additional_task_flag = False
            self.actual_work_amount = self.default_work_amount * (
                1.0 - self.default_progress
            )
        if log_info:
            self.remaining_work_amount_record_list = []
            self.state_record_list = []
            self.allocated_worker_id_record = []
            self.allocated_facility_id_record = []

        if state_info and log_info:
            if self.default_progress >= (1.00 - error_tol):
                self.state = BaseTaskState.FINISHED

    def perform(self, time: int, seed=None, increase_component_error=1.0):
        """
        Perform this BaseTask in this simulation.

        Args:
            time (int):
                Simulation time executing this method.
            seed (int, optional):
                Random seed for describing deviation of progress.
                Defaults to None.
            increase_component_error (float, optional):
                For advanced simulation.
                Increment error value when error has occurred.
                Defaults to 1.0.
        Note:
            This method includes advanced code of custom simulation.
            We have to separete basic code and advanced code in the future.
        """
        if self.state == BaseTaskState.WORKING:
            work_amount_progress = 0.0
            noErrorProbability = 1.0
            if self.auto_task:
                work_amount_progress = self.work_amount_progress_of_unit_step_time
            else:
                if self.need_facility:
                    min_length = min(
                        len(self.allocated_worker_list),
                        len(self.allocated_facility_list),
                    )
                    for i in range(min_length):
                        worker = self.allocated_worker_list[i]
                        w_progress = worker.get_work_amount_skill_progress(
                            self.name, seed=seed
                        )
                        facility = self.allocated_facility_list[i]
                        f_progress = facility.get_work_amount_skill_progress(
                            self.name, seed=seed
                        )
                        work_amount_progress += w_progress * f_progress
                        noErrorProbability = (
                            noErrorProbability
                            - worker.get_quality_skill_point(self.name, seed=seed)
                        )
                else:
                    for worker in self.allocated_worker_list:
                        work_amount_progress = (
                            work_amount_progress
                            + worker.get_work_amount_skill_progress(
                                self.name, seed=seed
                            )
                        )
                        noErrorProbability = (
                            noErrorProbability
                            - worker.get_quality_skill_point(self.name, seed=seed)
                        )

            self.remaining_work_amount = (
                self.remaining_work_amount - work_amount_progress
            )

            if self.target_component is not None:
                self.target_component.update_error_value(
                    noErrorProbability, increase_component_error, seed=seed
                )

    def can_add_resources(self, worker=None, facility=None):
        """
        Judge whether this task can be assigned another resources or not.

        Args:
            worker (BaseWorker):
                Target worker for allocating.
                Defaults to None.
            facility (BaseFacility):
                Target facility for allocating.
                Defaults to None.
        """
        if self.state == BaseTaskState.NONE:
            return False
        elif self.state == BaseTaskState.FINISHED:
            return False

        # True if none of the allocated resources have solo_working attribute True.
        for w in self.allocated_worker_list:
            if w.solo_working:
                return False
        for f in self.allocated_facility_list:
            if f.solo_working:
                return False

        # solo_working check
        if worker is not None:
            if worker.solo_working:
                if len(self.allocated_worker_list) > 0:
                    return False
        if facility is not None:
            if facility.solo_working:
                if len(self.allocated_facility_list) > 0:
                    return False

        # Fixing allocating worker/facility id list check
        if worker is not None:
            if self.fixing_allocating_worker_id_list is not None:
                if worker.ID not in self.fixing_allocating_worker_id_list:
                    return False
        if facility is not None:
            if self.fixing_allocating_facility_id_list is not None:
                if facility.ID not in self.fixing_allocating_facility_id_list:
                    return False

        # multi-task in one facility check
        if facility is not None:
            if len(facility.assigned_task_list) > 0:
                return False

        # skill check
        if facility is not None:
            if facility.has_workamount_skill(self.name):
                if worker.has_facility_skill(
                    facility.name
                ) and worker.has_workamount_skill(self.name):
                    return True
                else:
                    return False
            else:
                return False
        elif worker is not None:
            if worker.has_workamount_skill(self.name):
                return True
            else:
                return False
        else:
            return False

    def record_allocated_workers_facilities_id(self):
        """
        Record allocated worker & facilities id.

        Target attributes are `allocated_worker_id_record` and `allocated_facility_id_record`.
        """
        self.allocated_worker_id_record.append(
            [worker.ID for worker in self.allocated_worker_list]
        )
        self.allocated_facility_id_record.append(
            [facility.ID for facility in self.allocated_facility_list]
        )

    def record_state(self, working=True):
        """Record current 'state' in 'state_record_list'."""
        if working:
            self.state_record_list.append(self.state)
        else:
            if self.state == BaseTaskState.WORKING:
                self.state_record_list.append(BaseTaskState.READY)
            else:
                self.state_record_list.append(self.state)

    def record_remaining_work_amount(self):
        """Record current `remaining_work_amount`."""
        self.remaining_work_amount_record_list.append(self.remaining_work_amount)

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.remaining_work_amount_record_list = self.remaining_work_amount_record_list[
            ::-1
        ]
        self.state_record_list = self.state_record_list[::-1]
        self.allocated_worker_id_record = self.allocated_worker_id_record[::-1]
        self.allocated_facility_id_record = self.allocated_facility_id_record[::-1]

    def get_state_from_record(self, time: int):
        """
        Get the state information in time.

        Args:
            time (int):
                target simulation time

        Returns:
            BaseTaskState: Task State information.
        """
        return self.state_record_list[time]

    def remove_absence_time_list(self, absence_time_list):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.state_record_list):
                self.remaining_work_amount_record_list.pop(step_time)
                self.allocated_worker_id_record.pop(step_time)
                self.allocated_facility_id_record.pop(step_time)
                self.state_record_list.pop(step_time)

    def insert_absence_time_list(self, absence_time_list):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list):
            if step_time < len(self.state_record_list):
                if step_time == 0:
                    self.remaining_work_amount_record_list.insert(
                        self.default_work_amount * (1.0 - self.default_progress)
                    )
                    self.allocated_worker_id_record.insert(step_time, None)
                    self.allocated_facility_id_record.insert(step_time, None)
                    self.state_record_list.insert(step_time, BaseTaskState.NONE)
                else:
                    self.remaining_work_amount_record_list.insert(
                        step_time, self.remaining_work_amount_record_list[step_time - 1]
                    )
                    self.allocated_worker_id_record.insert(
                        step_time, self.allocated_worker_id_record[step_time - 1]
                    )
                    self.allocated_facility_id_record.insert(
                        step_time, self.allocated_facility_id_record[step_time - 1]
                    )

                    insert_state_before = self.state_record_list[step_time - 1]
                    insert_state_after = self.state_record_list[step_time]
                    if insert_state_before == BaseTaskState.WORKING:
                        if insert_state_after == BaseTaskState.FINISHED:
                            insert_state = BaseTaskState.FINISHED
                        else:
                            insert_state = BaseTaskState.READY
                        self.state_record_list.insert(step_time, insert_state)
                    elif (
                        insert_state_before == BaseTaskState.NONE
                        and insert_state_after == BaseTaskState.WORKING
                    ):
                        self.state_record_list.insert(step_time, BaseTaskState.READY)
                    else:
                        self.state_record_list.insert(
                            step_time, self.state_record_list[step_time - 1]
                        )

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time` as follows:

        - ID
        - name
        - default_work_amount
        - remaining_work_amount_record_list
        - state_record_list[target_step_time]
        - allocated_worker_id_record[target_step_time]
        - allocated_facility_id_record[target_step_time]

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        print(
            self.ID,
            self.name,
            self.default_work_amount,
            max(self.remaining_work_amount_record_list[target_step_time], 0.0),
            self.state_record_list[target_step_time],
            self.allocated_worker_id_record[target_step_time],
            self.allocated_facility_id_record[target_step_time],
        )

    def print_all_log_in_chronological_order(self, backward=False):
        """
        Print all log in chronological order.
        """
        for t in range(self.state_record_list):
            print("TIME: ", t)
            if backward:
                t = len(self.state_record_list) - 1 - t
            self.print_log(t)

    def get_time_list_for_gannt_chart(self, finish_margin=1.0):
        """
        Get ready/working time_list for drawing Gantt chart.

        Args:
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
        Returns:
            List[tuple(int, int)]: ready_time_list including start_time, length
            List[tuple(int, int)]: working_time_list including start_time, length
        """
        ready_time_list = []
        working_time_list = []
        previous_state = BaseTaskState.NONE
        from_time = -1
        to_time = -1
        for time, state in enumerate(self.state_record_list):
            if state != previous_state:
                if from_time == -1:
                    from_time = time
                elif to_time == -1:
                    to_time = time
                    if state == BaseTaskState.NONE or state == BaseTaskState.FINISHED:
                        if previous_state == BaseTaskState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseTaskState.READY:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseTaskState.READY:
                        if previous_state == BaseTaskState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseTaskState.WORKING:
                        if previous_state == BaseTaskState.READY:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    from_time = time
                    to_time = -1
            previous_state = state

        # Suspended because of max time limitation
        if from_time > -1 and to_time == -1:
            if previous_state == BaseTaskState.WORKING:
                working_time_list.append((from_time, time - from_time + finish_margin))
            elif previous_state == BaseTaskState.READY:
                ready_time_list.append((from_time, time - from_time + finish_margin))

        return ready_time_list, working_time_list

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        view_ready=False,
    ):
        """
        Create data for gantt plotly.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.

        Returns:
            list[dict]: Gantt plotly information of this BaseTask
        """
        df = []
        (
            ready_time_list,
            working_time_list,
        ) = self.get_time_list_for_gannt_chart(finish_margin=finish_margin)

        if view_ready:
            for from_time, length in ready_time_list:
                to_time = from_time + length
                df.append(
                    {
                        "Task": self.name,
                        "Start": (init_datetime + from_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Finish": (init_datetime + to_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "State": "READY",
                        "Type": "Task",
                    }
                )
        for from_time, length in working_time_list:
            to_time = from_time + length
            df.append(
                {
                    "Task": self.name,
                    "Start": (init_datetime + from_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Finish": (init_datetime + to_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "State": "WORKING",
                    "Type": "Task",
                }
            )
        return df

    def get_mermaid_diagram(
        self,
        shape: str = "rect",
        print_work_amount_info: bool = True,
        subgraph: bool = False,
        subgraph_name: str = "Task",
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this task.
        Args:
            shape (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Subgraph name.
                Defaults to "Product".
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {subgraph_name}")
            list_of_lines.append(f"direction {subgraph_direction}")
        node_label = self.name
        if print_work_amount_info:
            node_label += f"<br>{self.default_work_amount}/{self.remaining_work_amount}"
        list_of_lines.append(f"{self.ID}@{{shape: {shape}, label: '{node_label}'}}")

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        shape: str = "rect",
        print_work_amount_info: bool = True,
        subgraph: bool = False,
        subgraph_name: str = "Task",
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this task.
        Args:
            orientations (str, optional):
                Orientation of mermaid diagram.
                    https://mermaid.js.org/syntax/flowchart.html#direction
                Defaults to "LR".
            shape (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Subgraph name.
                Defaults to "Task".
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_mermaid_diagram(
            shape=shape,
            print_work_amount_info=print_work_amount_info,
            subgraph=subgraph,
            subgraph_name=subgraph_name,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")
