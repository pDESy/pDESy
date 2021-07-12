#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from enum import IntEnum
import datetime
from .base_priority_rule import ResourcePriorityRuleMode


class BaseTaskState(IntEnum):
    """BaseTaskState"""

    NONE = 0
    READY = 1
    WORKING = 2
    WORKING_ADDITIONALLY = 3
    FINISHED = -1


class BaseTaskDependency(IntEnum):
    """BaseTaskDependency"""

    FS = 0  # Finish to Start
    SS = 1  # Start to Start
    FF = 2  # Finish to Finish
    SF = 3  # Finish to Start


class BaseTask(object, metaclass=abc.ABCMeta):
    """BaseTask
    BaseTask class for expressing target workflow.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter.
            Name of this task.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        default_work_amount (float, optional):
            Basic parameter.
            Defalt workamount of this BaseTask.
            Defaults to None -> 10.0.
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
        worker_priority_rule (ResourcePriorityRule, oprional):
            Worker priority rule for simulation.
            Deraults to ResourcePriorityRule.SSP.
        facility_priority_rule (ResourcePriorityRule, oprional):
            Task priority rule for simulation.
            Deraults to TaskPriorityRule.TSLACK.
        need_facility (bool, optional):
            Basic parameter.
            Whether one facility is needed for performing this task or not.
            Default to False
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
            Default to False.
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
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        default_work_amount=None,
        input_task_list=None,
        output_task_list=None,
        allocated_team_list=None,
        allocated_workplace_list=None,
        parent_workflow=None,
        worker_priority_rule=ResourcePriorityRuleMode.SSP,
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
        state=BaseTaskState.NONE,
        state_record_list=None,
        allocated_worker_list=None,
        allocated_worker_id_record=None,
        allocated_facility_list=None,
        allocated_facility_id_record=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.default_work_amount = (
            default_work_amount if default_work_amount is not None else 10.0
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

    def __str__(self):
        """
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
            type="BaseTask",
            name=self.name,
            ID=self.ID,
            default_work_amount=self.default_work_amount,
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
            target_component=self.target_component.ID
            if self.target_component is not None
            else None,
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
        Append input task to `input_task_list`

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

    def extend_input_task_list(
        self, input_task_list, task_dependency_mode=BaseTaskDependency.FS
    ):
        """
        Extend the list of input tasks to `input_task_list`

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

        If `log_info` is True the following attributes are initialized.

            - `state_record_list`
            - `allocated_worker_id_record`
            - `allocated_facility_id_record`

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
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
        if log_info:
            self.state_record_list = []
            self.allocated_worker_id_record = []
            self.allocated_facility_id_record = []

        if state_info and log_info:
            if (0.00 + error_tol) < self.default_progress and self.default_progress < (
                1.00 - error_tol
            ):
                self.state = BaseTaskState.READY
            elif self.default_progress >= (1.00 - error_tol):
                self.state = BaseTaskState.FINISHED

    def perform(self, time: int, seed=None):
        """
        Perform this BaseTask in this simulation

        Args:
            time (int):
                Simulation time executing this method.
            seed (int, optional):
                Random seed for describing deviation of progress.
                Defaults to None.
        """
        if self.state == BaseTaskState.WORKING:
            work_amount_progress = 0.0

            if self.auto_task:
                work_amount_progress = 1.0
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
                else:
                    for worker in self.allocated_worker_list:
                        work_amount_progress = (
                            work_amount_progress
                            + worker.get_work_amount_skill_progress(
                                self.name, seed=seed
                            )
                        )
            self.remaining_work_amount = (
                self.remaining_work_amount - work_amount_progress
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
        Record allocated worker & facilities id to `allocated_worker_id_record` and `allocated_facility_id_record`.
        """
        self.allocated_worker_id_record.append(
            [worker.ID for worker in self.allocated_worker_list]
        )
        self.allocated_facility_id_record.append(
            [facility.ID for facility in self.allocated_facility_list]
        )

    def record_state(self):
        """
        Record current 'state' in 'state_record_list'
        """
        self.state_record_list.append(self.state)

    def reverse_log_information(self):
        """
        Reverse log information of all.
        """
        self.state_record_list = self.state_record_list[::-1]
        self.allocated_worker_id_record = self.allocated_worker_id_record[::-1]
        self.allocated_facility_id_record = self.allocated_facility_id_record[::-1]

    def get_state_from_record(self, time: int):
        """
        Get the state information in time

        Args:
            time (int):
                target simulation time

        Returns:
            BaseTaskState: Task State information.
        """
        return self.state_record_list[time]

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

            if previous_state == BaseTaskState.WORKING:
                working_time_list.append(
                    (from_time, time - 1 - from_time + finish_margin)
                )
            elif previous_state == BaseTaskState.READY:
                ready_time_list.append(
                    (from_time, time - 1 - from_time + finish_margin)
                )
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
            for (from_time, length) in ready_time_list:
                to_time = from_time + length
                df.append(
                    dict(
                        Task=self.name,
                        Start=(init_datetime + from_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        Finish=(init_datetime + to_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        State="READY",
                        Type="Task",
                    )
                )
        for (from_time, length) in working_time_list:
            to_time = from_time + length
            df.append(
                dict(
                    Task=self.name,
                    Start=(init_datetime + from_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    Finish=(init_datetime + to_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    State="WORKING",
                    Type="Task",
                )
            )
        return df
