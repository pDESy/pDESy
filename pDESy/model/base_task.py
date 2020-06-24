#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from enum import IntEnum
import datetime


class BaseTaskState(IntEnum):
    NONE = 0
    READY = 1
    WORKING = 2
    WORKING_ADDITIONALLY = 3
    FINISHED = -1


class BaseTask(object, metaclass=abc.ABCMeta):
    """BaseTask
    BaseTask class for expressing target workflow.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter.
            Name of this team.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        default_work_amount (float, optional):
            Basic parameter.
            Defalt workamount of this BaseTask.
            Defaults to None -> 10.0.
        input_task_list (List[BaseTask], optional):
            Basic parameter.
            List of input BaseTask.
            Defaults to None -> [].
        output_task_list (List[BaseTask], optional):
            Basic parameter.
            List of output BaseTask.
            Defaults to None -> [].
        allocated_team_list (List[BaseTeam], optional):
            Basic parameter.
            List of allocated BaseTeam
            Defaults to None -> [].
        allocated_factory_list (List[BaseFactory], optional):
            Basic parameter.
            List of allocated BaseFactory
            Defaults to None -> [].
        need_facility (bool, optional):
            Basic parameter.
            Whether one facility is needed for performing this task or not.
            Default to False
        target_component_list (List[BaseComponent], optional):
            Basic parameter.
            List of target BaseCompoenent.
            Defaults to None -> [].
        default_progress (float, optional):
            Basic parameter.
            Progress before starting simulation (0.0 ~ 1.0)
            Defaults to None -> 0.0.
        auto_task (bool, optional):
            Basic parameter.
            If True, this task is performed automatically
            even if there are no allocated workers.
            Default to False.
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
        ready_time_list (List[float], optional):
            Basic variable.
            History or record of READY time in simumation.
            Defaults to None -> [].
        start_time_list (List[float], optional):
            Basic variable.
            History or record of start WORKING time in simumation.
            Defaults to None -> [].
        finish_time_list (List[float], optional):
            Basic variable.
            History or record of finish WORKING time in simumation.
            Defaults to None -> [].
        allocated_worker_list (List[BaseResource], optional):
            Basic variable.
            State of allocating resource list in simumation.
            Defaults to None -> [].
        allocated_worker_id_record (List[List[str]], optional):
            Basic variable.
            State of allocating resource id list in simumation.
            Defaults to None -> [].
        allocated_facility_list (List[BaseFacility], optional):
            Basic variable.
            State of allocating facility list in simumation.
            Defaults to None -> [].
        allocated_facility_id_record (List[List[str]], optional):
            Basic variable.
            State of allocating facility id list in simumation.
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
        allocated_factory_list=None,
        need_facility=False,
        target_component_list=None,
        default_progress=None,
        auto_task=False,
        # Basic variables
        est=0.0,
        eft=0.0,
        lst=-1.0,
        lft=-1.0,
        remaining_work_amount=None,
        state=BaseTaskState.NONE,
        ready_time_list=None,
        start_time_list=None,
        finish_time_list=None,
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
        self.allocated_factory_list = (
            allocated_factory_list if allocated_factory_list is not None else []
        )
        self.need_facility = need_facility
        self.target_component_list = (
            target_component_list if target_component_list is not None else []
        )
        self.default_progress = (
            default_progress if default_progress is not None else 0.0
        )
        self.auto_task = auto_task if auto_task is not False else False
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

        if ready_time_list is not None:
            self.ready_time_list = ready_time_list
        else:
            self.ready_time_list = []

        if start_time_list is not None:
            self.start_time_list = start_time_list
        else:
            self.start_time_list = []

        if finish_time_list is not None:
            self.finish_time_list = finish_time_list
        else:
            self.finish_time_list = []

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

    def append_input_task(self, input_task):
        """
        Append input task

        Args:
            input_task (BaseTask):
                Input BaseTask
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
        self.input_task_list.append(input_task)
        input_task.output_task_list.append(self)

    def extend_input_task_list(self, input_task_list):
        """
        Extend the list of input tasks

        Args:
            input_task_list (List[BaseTask]):
                List of input BaseTask
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
        self.input_task_list.extend(input_task_list)
        for input_task in input_task_list:
            input_task.output_task_list.append(self)

    def initialize(self, error_tol=1e-10):
        """
        Initialize the changeable variables of BaseTask

        - est
        - eft
        - lst
        - lft
        - remaining_work_amount
        - state
        - ready_time_list
        - start_time_list
        - finish_time_list
        - allocated_worker_list
        - allocated_worker_id_record
        - allocated_facility_list
        - allocated_facility_id_record
        """
        self.est = 0.0  # Earliest start time
        self.eft = 0.0  # Earliest finish time
        self.lst = -1.0  # Latest start time
        self.lft = -1.0  # Latest finish time
        self.remaining_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )
        self.state = BaseTaskState.NONE
        self.ready_time_list = []
        self.start_time_list = []
        self.finish_time_list = []
        self.allocated_worker_list = []
        self.allocated_worker_id_record = []
        self.allocated_facility_list = []
        self.allocated_facility_id_record = []

        if (0.00 + error_tol) < self.default_progress and self.default_progress < (
            1.00 - error_tol
        ):
            self.state = BaseTaskState.READY
            self.ready_time_list.append(int(-1))
        elif self.default_progress >= (1.00 - error_tol):
            self.state = BaseTaskState.FINISHED
            self.ready_time_list.append(int(-1))
            self.start_time_list.append(int(-1))
            self.finish_time_list.append(int(-1))

    def perform(self, time: int, seed=None):
        """
        Perform this BaseTask in this simulation

        Args:
            time (int):
                Simulation time executing this method.
            seed (int, optional):
                Random seed for describing deviation of progress.
                If workamount
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
                        facility = self.allocated_facility_list[i]
                        work_amount_progress = work_amount_progress
                        +worker.get_work_amount_skill_progress(
                            self.name, seed=seed
                        ) * facility.get_work_amount_skill_progress(
                            self.name, seed=seed
                        )
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

    def record_allocated_workers_facilities_id(self):
        """
        Record allocated worker & facilities id in this time.
        """
        self.allocated_worker_id_record.append(
            [worker.ID for worker in self.allocated_worker_list]
        )
        self.allocated_facility_id_record.append(
            [facility.ID for facility in self.allocated_facility_list]
        )

    def get_state_from_record(self, time: int):
        """
        Get the state information in time

        Args:
            time (int):
                target simulation time

        Returns:
            BaseTaskState: Task State information.
        """

        if time < self.ready_time_list[0]:
            return BaseTaskState.NONE
        elif self.ready_time_list[0] <= time and time < self.start_time_list[0]:
            return BaseTaskState.READY
        elif self.start_time_list[0] <= time and time < self.finish_time_list[0]:
            return BaseTaskState.WORKING
        else:
            if len(self.finish_time_list) == 1:
                return BaseTaskState.FINISHED
            else:
                for i in range(len(self.finish_time_list) - 1):
                    if (
                        self.finish_time_list[i] <= time
                        and time < self.ready_time_list[i + 1]
                    ):
                        return BaseTaskState.FINISHED
                    elif (
                        self.ready_time_list[i + 1] <= time
                        and time < self.start_time_list[i + 1]
                    ):
                        return BaseTaskState.READY
                    elif (
                        self.start_time_list[i + 1] <= time
                        and time < self.finish_time_list[i + 1]
                    ):
                        return BaseTaskState.WORKING

                if self.finish_time_list[-1] <= time:
                    return BaseTaskState.FINISHED

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        view_ready=False,
    ):
        """
        Create data for gantt plotly
        from ready_time_list, start_time_list and finish_time_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulattion
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
        for ready_time, start_time, finish_time in zip(
            self.ready_time_list, self.start_time_list, self.finish_time_list
        ):
            if view_ready:
                df.append(
                    dict(
                        Task=self.name,
                        Start=(init_datetime + ready_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        Finish=(init_datetime + (start_time) * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        State="READY",
                        Type="Task",
                    )
                )

            df.append(
                dict(
                    Task=self.name,
                    Start=(init_datetime + start_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    Finish=(
                        init_datetime + (finish_time + finish_margin) * unit_timedelta
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    State="WORKING",
                    Type="Task",
                )
            )
        return df
