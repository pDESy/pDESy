#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_workflow."""

import abc
import datetime
import uuid
import warnings

import matplotlib.pyplot as plt

import networkx as nx

import plotly.figure_factory as ff
import plotly.graph_objects as go

from .base_facility import BaseFacilityState
from .base_task import BaseTask, BaseTaskDependency, BaseTaskState
from .base_worker import BaseWorkerState
from .base_subproject_task import BaseSubProjectTask


class BaseWorkflow(object, metaclass=abc.ABCMeta):
    """BaseWorkflow.

    BaseWorkflow class for expressing workflow in a project.
    BaseWorkflow is consist of multiple BaseTasks.
    This class will be used as template.

    Args:
        name (str, optional):
            Basic parameter.
            Name of this workflow.
            Defaults to None -> "Workflow".
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None -> str(uuid.uuid4()).
        task_list (List[BaseTask], optional):
            Basic parameter.
            List of BaseTask in this BaseWorkflow.
            Default to None -> [].
        critical_path_length (float, optional):
            Basic variable.
            Critical path length of PERT/CPM.
            Defaults to 0.0.
    """

    def __init__(
        self,
        # Basic parameters
        name=None,
        ID=None,
        task_list=None,
        # Basic variables
        critical_path_length=0.0,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "Workflow"
        self.ID = ID if ID is not None else str(uuid.uuid4())

        self.task_list = []
        if task_list is not None:
            self.extend_child_task_list(task_list)
        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        self.critical_path_length = (
            critical_path_length if critical_path_length != 0.0 else 0.0
        )

    def __str__(self):
        """str.

        Returns:
            str: name list of BaseTask
        Examples:
            >>> w = BaseWorkflow(task_list=[BaseTask('t1')])
            >>> print([t.name for t in w.task_list])
            ['t1']
        """
        return "{}".format(list(map(lambda task: str(task), self.task_list)))

    def append_child_task(self, task):
        """
        Append target task to this workflow.
        Args:
            task (BaseTask): target task
        """
        self.task_list.append(task)
        task.parent_workflow = self

    def extend_child_task_list(self, task_list):
        """
        Extend target task_list to this workflow.
        Args:
            task_list (List[BaseTask]): target task list
        """
        for task in task_list:
            self.append_child_task(task)

    def export_dict_json_data(self):
        """
        Export the information of this workflow to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
            task_list=[t.export_dict_json_data() for t in self.task_list],
            critical_path_length=self.critical_path_length,
        )
        return dict_json_data

    def read_json_data(self, json_data):
        """
        Read the JSON data for creating BaseWorkflow instance.

        Args:
            json_data (dict): JSON data.
        """
        self.name = json_data["name"]
        self.ID = json_data["ID"]
        self.task_list = []
        j_list = json_data["task_list"]
        for j in j_list:
            if j["type"] == "BaseTask":
                self.task_list.append(
                    BaseTask(
                        name=j["name"],
                        ID=j["ID"],
                        default_work_amount=j["default_work_amount"],
                        work_amount_progress_of_unit_step_time=j[
                            "work_amount_progress_of_unit_step_time"
                        ],
                        input_task_list=j["input_task_list"],
                        output_task_list=j["output_task_list"],
                        allocated_team_list=j["allocated_team_list"],
                        allocated_workplace_list=j["allocated_workplace_list"],
                        need_facility=j["need_facility"],
                        target_component=j["target_component"],
                        default_progress=j["default_progress"],
                        due_time=j["due_time"],
                        auto_task=j["auto_task"],
                        fixing_allocating_worker_id_list=j[
                            "fixing_allocating_worker_id_list"
                        ],
                        fixing_allocating_facility_id_list=j[
                            "fixing_allocating_facility_id_list"
                        ],
                        # Basic variables
                        est=j["est"],
                        eft=j["eft"],
                        lst=j["lst"],
                        lft=j["lft"],
                        remaining_work_amount=j["remaining_work_amount"],
                        remaining_work_amount_record_list=j[
                            "remaining_work_amount_record_list"
                        ],
                        state=BaseTaskState(j["state"]),
                        state_record_list=[
                            BaseTaskState(num) for num in j["state_record_list"]
                        ],
                        allocated_worker_list=j["allocated_worker_list"],
                        allocated_worker_id_record=j["allocated_worker_id_record"],
                        allocated_facility_list=j["allocated_facility_list"],
                        allocated_facility_id_record=j["allocated_facility_id_record"],
                    )
                )
            elif j["type"] == "BaseSubProjectTask":
                self.task_list.append(
                    BaseSubProjectTask(
                        file_path=j["file_path"],
                        unit_timedelta=j["unit_timedelta"],
                        read_json_file=j["read_json_file"],
                        remove_absence_time_list=j["remove_absence_time_list"],
                        name=j["name"],
                        ID=j["ID"],
                        default_work_amount=j["default_work_amount"],
                        work_amount_progress_of_unit_step_time=j[
                            "work_amount_progress_of_unit_step_time"
                        ],
                        input_task_list=j["input_task_list"],
                        output_task_list=j["output_task_list"],
                        allocated_team_list=j["allocated_team_list"],
                        allocated_workplace_list=j["allocated_workplace_list"],
                        need_facility=j["need_facility"],
                        target_component=j["target_component"],
                        default_progress=j["default_progress"],
                        due_time=j["due_time"],
                        auto_task=j["auto_task"],
                        fixing_allocating_worker_id_list=j[
                            "fixing_allocating_worker_id_list"
                        ],
                        fixing_allocating_facility_id_list=j[
                            "fixing_allocating_facility_id_list"
                        ],
                        # Basic variables
                        est=j["est"],
                        eft=j["eft"],
                        lst=j["lst"],
                        lft=j["lft"],
                        remaining_work_amount=j["remaining_work_amount"],
                        remaining_work_amount_record_list=j[
                            "remaining_work_amount_record_list"
                        ],
                        state=BaseTaskState(j["state"]),
                        state_record_list=[
                            BaseTaskState(num) for num in j["state_record_list"]
                        ],
                        allocated_worker_list=j["allocated_worker_list"],
                        allocated_worker_id_record=j["allocated_worker_id_record"],
                        allocated_facility_list=j["allocated_facility_list"],
                        allocated_facility_id_record=j["allocated_facility_id_record"],
                    )
                )

        self.critical_path_length = json_data["critical_path_length"]

    def extract_none_task_list(self, target_time_list):
        """
        Extract NONE task list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract none task from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseTask]: List of BaseTask
        """
        return self.__extract_state_task_list(target_time_list, BaseTaskState.NONE)

    def extract_ready_task_list(self, target_time_list):
        """
        Extract READY task list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract ready task from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseTask]: List of BaseTask
        """
        return self.__extract_state_task_list(target_time_list, BaseTaskState.READY)

    def extract_working_task_list(self, target_time_list):
        """
        Extract WORKING task list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract working task from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseTask]: List of BaseTask
        """
        return self.__extract_state_task_list(target_time_list, BaseTaskState.WORKING)

    def extract_finished_task_list(self, target_time_list):
        """
        Extract FINISHED task list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract finished task from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseTask]: List of BaseTask
        """
        return self.__extract_state_task_list(target_time_list, BaseTaskState.FINISHED)

    def __extract_state_task_list(self, target_time_list, target_state):
        """
        Extract state task list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract target_state task from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
            target_state (BaseTaskState):
                Target state.
        Returns:
            List[BaseTask]: List of BaseTask
        """
        task_set = set()
        for task in self.task_list:
            extract_flag = True
            for time in target_time_list:
                if len(task.state_record_list) <= time:
                    extract_flag = False
                    break
                if task.state_record_list[time] != target_state:
                    extract_flag = False
                    break
            if extract_flag:
                task_set.add(task)
        return list(task_set)

    def get_task_list(
        self,
        # Basic parameters
        name=None,
        ID=None,
        default_work_amount=None,
        input_task_list=None,
        output_task_list=None,
        allocated_team_list=None,
        allocated_workplace_list=None,
        need_facility=None,
        target_component=None,
        default_progress=None,
        due_time=None,
        auto_task=None,
        fixing_allocating_worker_id_list=None,
        fixing_allocating_facility_id_list=None,
        # search param
        est=None,
        eft=None,
        lst=None,
        lft=None,
        remaining_work_amount=None,
        state=None,
        allocated_worker_list=None,
        allocated_worker_id_record=None,
        allocated_facility_list=None,
        allocated_facility_id_record=None,
    ):
        """
        Get task list by using search conditions related to BaseTask parameter.

        If there is no searching condition, this function returns all `task_list`

        Args:
            name (str, optional):
                Target task name.
                Default to None.
            ID (str, optional):
                Target task ID.
                Defaults to None.
            default_work_amount (float, optional):
                Target task default_work_amount
                Defaults to None.
            input_task_list (List[BaseTask,BaseTaskDependency], optional):
                Target task input_task_list
                Defaults to None.
            output_task_list (List[BaseTask,BaseTaskDependency], optional):
                Target task output_task_list
                Defaults to None.
            allocated_team_list (List[BaseTeam], optional):
                Target task allocated_team_list
                Defaults to None.
            allocated_workplace_list (List[BaseWorkplace], optional):
                Target task allocated_workplace_list
                Defaults to None.
            need_facility (bool, optional):
                Target task need_facility
                Defaults to None.
            target_component (BaseComponent, optional):
                Target task target_component
                Defaults to None.
            default_progress (float, optional):
                Target task default_progress
                Defaults to None.
            due_time (int, optional):
                Target task due_time
                Defaults to None.
            auto_task (bool, optional):
                Target task auto_task
                Defaults to None.
            fixing_allocating_worker_id_list (List[str], optional):
                Target task fixing_allocating_worker_id_list
                Defaults to None.
            fixing_allocating_facility_id_list (List[str], optional):
                Target task fixing_allocating_facility_id_list
                Defaults to None.
            est (float, optional):
                Target task est
                Defaults to None.
            eft (float, optional):
                Target task eft
                Defaults to None.
            lst (float, optional):
                Target task lst
                Defaults to None.
            lft (float, optional):
                Target task lft
                Defaults to None.
            remaining_work_amount (float, optional):
                Target task remaining_work_amount
                Defaults to None.
            state (BaseTaskState, optional):
                Target task state
                Defaults to None.
            allocated_worker_list (List[BaseWorker], optional):
                Target task allocated_worker_list
                Defaults to None.
            allocated_worker_id_record (List[List[str]], optional):
                Target task allocated_worker_id_record
                Defaults to None.
            allocated_facility_list (List[BaseFacility], optional):
                Target task allocated_facility_list
                Defaults to None.
            allocated_facility_id_record (List[List[str]], optional):
                Target task allocated_facility_id_record
                Defaults to None.
        Returns:
            List[BaseTask]: List of BaseTask
        """
        task_list = self.task_list
        if name is not None:
            task_list = list(filter(lambda task: task.name == name, task_list))
        if ID is not None:
            task_list = list(filter(lambda task: task.ID == ID, task_list))
        if default_work_amount is not None:
            task_list = list(
                filter(
                    lambda task: task.default_work_amount == default_work_amount,
                    task_list,
                )
            )
        if input_task_list is not None:
            task_list = list(
                filter(lambda task: task.input_task_list == input_task_list, task_list)
            )
        if output_task_list is not None:
            task_list = list(
                filter(
                    lambda task: task.output_task_list == output_task_list, task_list
                )
            )
        if allocated_team_list is not None:
            task_list = list(
                filter(
                    lambda task: task.allocated_team_list == allocated_team_list,
                    task_list,
                )
            )
        if allocated_workplace_list is not None:
            task_list = list(
                filter(
                    lambda task: task.allocated_workplace_list
                    == allocated_workplace_list,
                    task_list,
                )
            )
        if need_facility is not None:
            task_list = list(
                filter(lambda task: task.need_facility == need_facility, task_list)
            )
        if target_component is not None:
            task_list = list(
                filter(
                    lambda task: task.target_component == target_component, task_list
                )
            )
        if default_progress is not None:
            task_list = list(
                filter(
                    lambda task: task.default_progress == default_progress, task_list
                )
            )
        if due_time is not None:
            task_list = list(filter(lambda task: task.due_time == due_time, task_list))
        if auto_task is not None:
            task_list = list(
                filter(lambda task: task.auto_task == auto_task, task_list)
            )
        if fixing_allocating_worker_id_list is not None:
            task_list = list(
                filter(
                    lambda task: task.fixing_allocating_worker_id_list
                    == fixing_allocating_worker_id_list,
                    task_list,
                )
            )
        if fixing_allocating_facility_id_list is not None:
            task_list = list(
                filter(
                    lambda task: task.fixing_allocating_facility_id_list
                    == fixing_allocating_facility_id_list,
                    task_list,
                )
            )
        if est is not None:
            task_list = list(filter(lambda task: task.est == est, task_list))
        if eft is not None:
            task_list = list(filter(lambda task: task.eft == eft, task_list))
        if lst is not None:
            task_list = list(filter(lambda task: task.lst == lst, task_list))
        if lft is not None:
            task_list = list(filter(lambda task: task.lft == lft, task_list))
        if remaining_work_amount is not None:
            task_list = list(
                filter(
                    lambda task: task.remaining_work_amount == remaining_work_amount,
                    task_list,
                )
            )
        if state is not None:
            task_list = list(filter(lambda task: task.state == state, task_list))
        if allocated_worker_list is not None:
            task_list = list(
                filter(
                    lambda task: task.allocated_worker_list == allocated_worker_list,
                    task_list,
                )
            )
        if allocated_worker_id_record is not None:
            task_list = list(
                filter(
                    lambda task: task.allocated_worker_id_record
                    == allocated_worker_id_record,
                    task_list,
                )
            )
        if allocated_facility_list is not None:
            task_list = list(
                filter(
                    lambda task: task.allocated_facility_list
                    == allocated_facility_list,
                    task_list,
                )
            )
        if allocated_facility_id_record is not None:
            task_list = list(
                filter(
                    lambda task: task.allocated_facility_id_record
                    == allocated_facility_id_record,
                    task_list,
                )
            )
        return task_list

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the changeable variables of BaseWorkflow including PERT calculation.

        If `state_info` is True, the following attributes are initialized.

          - `critical_path_length`
          - PERT data
          - The state of each task after all tasks are initialized.

        BaseTask in `task_list` are also initialized by this function.

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaults to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        for task in self.task_list:
            task.initialize(state_info=state_info, log_info=log_info)
            if task.parent_workflow is None:
                task.parent_workflow = self
        if state_info:
            self.critical_path_length = 0.0
            self.update_PERT_data(0)
            self.check_state(-1, BaseTaskState.READY)

    def reverse_log_information(self):
        """Reverse log information of all."""
        for t in self.task_list:
            t.reverse_log_information()

    def record(self, working=True):
        """Record the state of all tasks in `task_list`."""
        for task in self.task_list:
            task.record_allocated_workers_facilities_id()
            task.record_state(working=working)
            task.record_remaining_work_amount()

    def update_PERT_data(self, time: int):
        """
        Update PERT data (est,eft,lst,lft) of each BaseTask in task_list.

        Args:
            time (int):
                Simulation time.
        """
        self.__set_est_eft_data(time)
        self.__set_lst_lft_criticalpath_data(time)

    def check_state(self, time: int, state: BaseTaskState):
        """
        Check state of all BaseTasks in task_list.

        Args:
            time (int):
                Simulation time
            state (BaseTaskState):
                Check target state.
                Search and update all tasks which can change only target state.
        """
        if state == BaseTaskState.READY:
            self.__check_ready(time)
        elif state == BaseTaskState.WORKING:
            self.__check_working(time)
        elif state == BaseTaskState.FINISHED:
            self.__check_finished(time)

    def __check_ready(self, time: int):
        none_task_set = set(
            filter(lambda task: task.state == BaseTaskState.NONE, self.task_list)
        )
        for none_task in none_task_set:
            input_task_list = none_task.input_task_list

            # check READY condition by each dependency
            # FS: if input task is finished
            # SS: if input task is started
            # ...or this is head task
            ready = True
            for input_task, dependency in input_task_list:
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

    def __check_working(self, time: int):
        ready_and_assigned_task_set = set(
            filter(
                lambda task: task.state == BaseTaskState.READY
                and len(task.allocated_worker_list) > 0,
                self.task_list,
            )
        )

        ready_auto_task_without_component_set = set(
            filter(
                lambda task: task.state == BaseTaskState.READY
                and task.auto_task
                and task.target_component is None,
                self.task_list,
            )
        )

        ready_auto_task_with_component_set = set(
            filter(
                lambda task: task.state == BaseTaskState.READY
                and task.auto_task
                and task.target_component is not None
                and task.target_component.placed_workplace
                in task.allocated_workplace_list,
                self.task_list,
            )
        )

        working_and_assigned_task_set = set(
            filter(
                lambda task: task.state == BaseTaskState.WORKING
                and len(task.allocated_worker_list) > 0,
                self.task_list,
            )
        )

        target_task_set = set()
        target_task_set.update(ready_and_assigned_task_set)
        target_task_set.update(ready_auto_task_without_component_set)
        target_task_set.update(ready_auto_task_with_component_set)
        target_task_set.update(working_and_assigned_task_set)

        for task in target_task_set:
            if task.state == BaseTaskState.READY:
                task.state = BaseTaskState.WORKING
                for worker in task.allocated_worker_list:
                    worker.state = BaseWorkerState.WORKING
                    # worker.assigned_task_list.append(task)
                if task.need_facility:
                    for facility in task.allocated_facility_list:
                        facility.state = BaseFacilityState.WORKING
                        # facility.assigned_task_list.append(task)

            elif task.state == BaseTaskState.WORKING:
                for worker in task.allocated_worker_list:
                    if worker.state == BaseWorkerState.FREE:
                        worker.state = BaseWorkerState.WORKING
                        # worker.assigned_task_list.append(task)
                    if task.need_facility:
                        for facility in task.allocated_facility_list:
                            if facility.state == BaseFacilityState.FREE:
                                facility.state = BaseFacilityState.WORKING
                                # facility.assigned_task_list.append(task)

    def __check_finished(self, time: int, error_tol=1e-10):
        working_and_zero_task_set = set(
            filter(
                lambda task: task.state == BaseTaskState.WORKING
                and task.remaining_work_amount < 0.0 + error_tol,
                self.task_list,
            )
        )
        for task in working_and_zero_task_set:
            # check FINISH condition by each dependency
            # SF: if input task is working
            # FF: if input task is finished
            finished = True
            for input_task, dependency in task.input_task_list:
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

                for worker in task.allocated_worker_list:
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
                task.allocated_worker_list = []

                if task.need_facility:
                    for facility in task.allocated_facility_list:
                        if len(facility.assigned_task_list) > 0 and all(
                            list(
                                map(
                                    lambda task: task.state == BaseTaskState.FINISHED,
                                    facility.assigned_task_list,
                                )
                            )
                        ):
                            facility.state = BaseFacilityState.FREE
                            facility.assigned_task_list.remove(task)

                    task.allocated_facility_list = []

    def __set_est_eft_data(self, time: int):
        input_task_set = set()

        # 1. Set the earliest finish time of head tasks.
        for task in self.task_list:
            task.est = time
            if len(task.input_task_list) == 0:
                task.eft = time + task.remaining_work_amount
                input_task_set.add(task)

        # 2. Calculate PERT information of all tasks
        while len(input_task_set) > 0:
            next_task_set = set()
            for input_task in input_task_set:
                for next_task, dependency in input_task.output_task_list:
                    pre_est = next_task.est
                    est = 0
                    eft = 0
                    if dependency == BaseTaskDependency.FS:
                        est = input_task.est + input_task.remaining_work_amount
                        eft = est + next_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.SS:
                        est = input_task.est + 0
                        eft = est + next_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.FF:
                        est = input_task.est + 0
                        eft = est + next_task.remaining_work_amount
                        if input_task.eft > eft:
                            eft = input_task.eft
                    elif dependency == BaseTaskDependency.SF:
                        est = input_task.est + 0
                        eft = est + next_task.remaining_work_amount
                        if input_task.est > eft:
                            eft = input_task.est
                    else:
                        est = input_task.est + input_task.remaining_work_amount
                        eft = est + next_task.remaining_work_amount
                    if est >= pre_est:
                        next_task.est = est
                        next_task.eft = eft
                    next_task_set.add(next_task)

            input_task_set = next_task_set

    def __set_lst_lft_criticalpath_data(self, time: int):
        # 1. Extract the list of tail tasks.
        output_task_set = set(
            filter(lambda task: len(task.output_task_list) == 0, self.task_list)
        )

        # 2. Update the information of critical path of this workflow.
        self.critical_path_length = max(output_task_set, key=lambda task: task.eft).eft
        for task in output_task_set:
            task.lft = self.critical_path_length
            task.lst = task.lft - task.remaining_work_amount

        # 3. Calculate PERT information of all tasks
        while len(output_task_set) > 0:
            prev_task_set = set()
            for output_task in output_task_set:
                for prev_task, dependency in output_task.input_task_list:
                    pre_lft = prev_task.lft
                    lst = 0
                    lft = 0
                    if dependency == BaseTaskDependency.FS:
                        lft = output_task.lst
                        lst = lft - prev_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.SS:
                        lst = output_task.lst
                        lft = lst + prev_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.FF:
                        lst = output_task.lst
                        lft = lst + prev_task.remaining_work_amount
                        if output_task.lft < lft:
                            lft = output_task.lft
                    elif dependency == BaseTaskDependency.SF:
                        lst = output_task.lst
                        lft = lst + prev_task.remaining_work_amount
                        if output_task.lft < lst:
                            lst = output_task.lft
                    else:
                        lft = output_task.lst
                        lst = lft - prev_task.remaining_work_amount
                    if pre_lft < 0 or pre_lft >= lft:
                        prev_task.lst = lst
                        prev_task.lft = lft
                    prev_task_set.add(prev_task)

            output_task_set = prev_task_set

    def reverse_dependencies(self):
        """
        Reverse all task dependencies in task_list.

        Note:
            This method is developed only for backward simulation.
        """
        # 1.
        for task in self.task_list:
            task.dummy_output_task_list = task.input_task_list
            task.dummy_input_task_list = task.output_task_list

        # 2.
        for task in self.task_list:
            task.output_task_list = task.dummy_output_task_list
            task.input_task_list = task.dummy_input_task_list
            del task.dummy_output_task_list, task.dummy_input_task_list

    def perform(
        self, time: int, only_auto_task=False, seed=None, increase_component_error=1.0
    ):
        """
        Perform BaseTask in task_list in simulation.

        Args:
            time (int):
                Simulation time.
            only_auto_task (bool, optional):
                Perform only auto task or not.
                Defaults to False.
            seed (int, optional):
                Random seed for describing deviation of progress.
                Defaults to None.
            increase_component_error (float, optional):
                For advanced simulation.
                Increment error value when error has occurred.
                Defaults to 1.0.
        Note:
            This method includes advanced code of custom simulation.
            We have to separate basic code and advanced code in the future.
        """
        for task in self.task_list:
            if only_auto_task:
                if task.auto_task:
                    task.perform(time, seed=seed)
            else:
                task.perform(
                    time, seed=seed, increase_component_error=increase_component_error
                )

    def remove_absence_time_list(self, absence_time_list):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for t in self.task_list:
            if not isinstance(t, BaseSubProjectTask):
                t.remove_absence_time_list(absence_time_list)

    def insert_absence_time_list(self, absence_time_list):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for t in self.task_list:
            if not isinstance(t, BaseSubProjectTask):
                t.insert_absence_time_list(absence_time_list)

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time`.

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        for task in self.task_list:
            task.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward=False):
        """
        Print all log in chronological order.
        """
        if len(self.task_list) > 0:
            for t in range(len(self.task_list[0].state_record_list)):
                print("TIME: ", t)
                if backward:
                    t = len(self.task_list[0].state_record_list) - 1 - t
                self.print_log(t)

    def plot_simple_gantt(
        self,
        finish_margin=1.0,
        view_auto_task=False,
        view_ready=False,
        task_color="#00EE00",
        auto_task_color="#005500",
        ready_color="#C0C0C0",
        figsize=[6.4, 4.8],
        dpi=100.0,
        save_fig_path=None,
    ):
        """
        Plot Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            view_auto_task (bool, optional):
                View auto_task or not.
                Defaults to False.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            task_color (str, optional):
                Task color setting information.
                Defaults to "#00EE00".
            auto_task_color (str, optional):
                Auto Task color setting information.
                Defaults to "#005500".
            ready_color (str, optional):
                Ready Task color setting information.
                Defaults to "#C0C0C0".
            figsize ((float, float), optional):
                Width, height in inches.
                Default to [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
        """
        fig, gnt = self.create_simple_gantt(
            finish_margin=finish_margin,
            view_auto_task=view_auto_task,
            view_ready=view_ready,
            task_color=task_color,
            auto_task_color=auto_task_color,
            ready_color=ready_color,
            figsize=figsize,
            dpi=dpi,
            save_fig_path=save_fig_path,
        )
        return fig

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        view_auto_task=False,
        view_ready=False,
        task_color="#00EE00",
        auto_task_color="#005500",
        ready_color="#C0C0C0",
        figsize=[6.4, 4.8],
        dpi=100.0,
        save_fig_path=None,
    ):
        """
        Create Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            view_auto_task (bool, optional):
                View auto_task or not.
                Defaults to False.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            task_color (str, optional):
                Task color setting information.
                Defaults to "#00EE00".
            auto_task_color (str, optional):
                Auto Task color setting information.
                Defaults to "#005500".
            ready_color (str, optional):
                Ready Task color setting information.
                Defaults to "#C0C0C0".
            figsize ((float, float), optional):
                Width, height in inches.
                Default to [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
            gnt: ax in plt.subplots()
        """
        fig, gnt = plt.subplots()
        fig.figsize = figsize
        fig.dpi = dpi
        gnt.set_xlabel("step")
        gnt.grid(True)

        target_task_list = list(filter(lambda task: not task.auto_task, self.task_list))
        if view_auto_task:
            target_task_list = self.task_list

        yticks = [10 * (n + 1) for n in range(len(target_task_list))]
        yticklabels = [task.name for task in target_task_list]

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        for ttime in range(len(target_task_list)):
            task = target_task_list[ttime]
            (
                ready_time_list,
                working_time_list,
            ) = task.get_time_list_for_gannt_chart(finish_margin=finish_margin)

            if view_ready:
                gnt.broken_barh(
                    ready_time_list, (yticks[ttime] - 5, 9), facecolors=(ready_color)
                )
            if task.auto_task:
                gnt.broken_barh(
                    working_time_list,
                    (yticks[ttime] - 5, 9),
                    facecolors=(auto_task_color),
                )
            else:
                gnt.broken_barh(
                    working_time_list, (yticks[ttime] - 5, 9), facecolors=(task_color)
                )

        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig, gnt

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        view_ready=False,
    ):
        """
        Create data for gantt plotly from task_list.

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
            list[dict]: Gantt plotly information of this BaseWorkflow
        """
        df = []
        for task in self.task_list:
            df.extend(
                task.create_data_for_gantt_plotly(
                    init_datetime,
                    unit_timedelta,
                    finish_margin=finish_margin,
                    view_ready=view_ready,
                )
            )
        return df

    def create_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        title="Gantt Chart",
        colors=None,
        index_col=None,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=True,
        show_colorbar=True,
        finish_margin=1.0,
        view_ready=False,
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
                Defaults to None ->
                dict(WORKING="rgb(146, 237, 5)", READY="rgb(107, 127, 135)").
            index_col (str, optional):
                index_col of plotly Gantt chart.
                Defaults to None -> "State".
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
            else {"WORKING": "rgb(146, 237, 5)", "READY": "rgb(107, 127, 135)"}
        )
        index_col = index_col if index_col is not None else "State"
        df = self.create_data_for_gantt_plotly(
            init_datetime,
            unit_timedelta,
            finish_margin=finish_margin,
            view_ready=view_ready,
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

    def get_networkx_graph(self):
        """
        Get the information of networkx graph.

        Returns:
            G: networkx.Digraph()
        """
        G = nx.DiGraph()

        # 1. add all nodes
        for task in self.task_list:
            G.add_node(task)

        # 2. add all edges
        for task in self.task_list:
            for input_task, dependency in task.input_task_list:
                G.add_edge(input_task, task)

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        figsize=[6.4, 4.8],
        dpi=100.0,
        save_fig_path=None,
        **kwds,
    ):
        """
        Draw networkx.

        Args:
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
            arrows (bool, optional):
                Digraph or Graph(no arrows).
                Defaults to True.
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
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
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

        # normal task
        normal_task_list = [task for task in self.task_list if not task.auto_task]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=normal_task_list,
            node_color=task_node_color,
            # **kwds,
        )

        # auto task
        auto_task_list = [task for task in self.task_list if task.auto_task]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=auto_task_list,
            node_color=auto_task_node_color,
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
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
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
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".

        Returns:
            task_node_trace: Normal Task Node information of plotly network.
            auto_task_node_trace: Auto Task Node information of plotly network.
            edge_trace: Edge information of plotly network.
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

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

        for node in G.nodes:
            x, y = pos[node]
            if not node.auto_task:
                task_node_trace["x"] = task_node_trace["x"] + (x,)
                task_node_trace["y"] = task_node_trace["y"] + (y,)
                task_node_trace["text"] = task_node_trace["text"] + (node,)
            elif node.auto_task:
                auto_task_node_trace["x"] = auto_task_node_trace["x"] + (x,)
                auto_task_node_trace["y"] = auto_task_node_trace["y"] + (y,)
                auto_task_node_trace["text"] = auto_task_node_trace["text"] + (node,)

        edge_trace = go.Scatter(
            x=[],
            y=[],
            line={"width": 1, "color": "#888"},
            hoverinfo="none",
            mode="lines",
        )

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace["x"] += (xposx, yposx)
            edge_trace["y"] += (xposy, yposy)

        return task_node_trace, auto_task_node_trace, edge_trace

    def draw_plotly_network(
        self,
        G=None,
        pos=None,
        title="Workflow",
        node_size=20,
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
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
                Defaults to "Workflow".
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)
        (
            task_node_trace,
            auto_task_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(
            G,
            pos,
            node_size=node_size,
            task_node_color=task_node_color,
            auto_task_node_color=auto_task_node_color,
        )
        fig = go.Figure(
            data=[edge_trace, task_node_trace, auto_task_node_trace],
            layout=go.Layout(
                title=title,
                showlegend=False,
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

    def get_mermaid_diagram(
        self,
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        link_type_str: str = "-->",
        print_dependency_type: bool = False,
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this workflow.
        Args:
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            link_type_str (str, optional):
                Link type string.
                Defaults to "-->".
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
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

        for task in self.task_list:
            list_of_lines.extend(
                task.get_mermaid_diagram(
                    shape=shape_task,
                    print_work_amount_info=print_work_amount_info,
                )
            )

        for task in self.task_list:
            dependency_type_mark = ""
            for input_task, dependency in task.input_task_list:
                if dependency == BaseTaskDependency.FS:
                    dependency_type_mark = "|FS|"
                elif dependency == BaseTaskDependency.SS:
                    dependency_type_mark = "|SS|"
                elif dependency == BaseTaskDependency.FF:
                    dependency_type_mark = "|FF|"
                elif dependency == BaseTaskDependency.SF:
                    dependency_type_mark = "|SF|"
                if not print_dependency_type:
                    dependency_type_mark = ""
                list_of_lines.append(
                    f"{input_task.ID}{link_type_str}{dependency_type_mark}{task.ID}"
                )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        link_type_str: str = "-->",
        print_dependency_type: bool = False,
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this workflow.
        Args:
            orientations (str, optional):
                Orientation of mermaid diagram.
                    https://mermaid.js.org/syntax/flowchart.html#direction
                Defaults to "LR".
            shape_task (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            link_type_str (str, optional):
                Link type string.
                Defaults to "-->".
            print_dependency_type (bool, optional):
                Print dependency type information or not.
                Defaults to False.
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_mermaid_diagram(
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            link_type_str=link_type_str,
            print_dependency_type=print_dependency_type,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")
