#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_workflow."""

import abc
import datetime
import sys
import uuid
import warnings

from collections import deque

import matplotlib.pyplot as plt

import networkx as nx

import plotly.figure_factory as ff
import plotly.graph_objects as go

from pDESy.model.base_priority_rule import (
    ResourcePriorityRuleMode,
    WorkplacePriorityRuleMode,
)

from .base_task import BaseTask, BaseTaskDependency, BaseTaskState
from .base_subproject_task import BaseSubProjectTask


class BaseWorkflow(object, metaclass=abc.ABCMeta):
    """BaseWorkflow.

    BaseWorkflow class for expressing workflow in a project.
    BaseWorkflow consists of multiple BaseTasks.
    This class will be used as a template.

    Args:
        name (str, optional): Name of this workflow. Defaults to None -> "Workflow".
        ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
        task_set (set[BaseTask], optional): List of BaseTask in this BaseWorkflow. Default to None -> set().
        critical_path_length (float, optional): Critical path length of PERT/CPM. Defaults to 0.0.
    """

    def __init__(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        task_set: set[BaseTask] = None,
        # Basic variables
        critical_path_length: float = 0.0,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "Workflow"
        self.ID = ID if ID is not None else str(uuid.uuid4())

        self.task_set = set()
        if task_set is not None:
            self.update_task_set(task_set)
        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        self.critical_path_length = (
            critical_path_length if critical_path_length != 0.0 else 0.0
        )
        # cache
        self._topology_cache = None

    def __invalidate_graph_cache(self):
        self._topology_cache = None

    def __str__(self):
        """Return the name list of BaseTask.

        Returns:
            str: Name list of BaseTask.
        """
        return f"{[str(task) for task in self.task_set]}"

    def append_child_task(self, task: BaseTask):
        """
        Append target task to this workflow.

        .. deprecated:: Use add_task instead.

        Args:
            task (BaseTask): Target task.
        """
        warnings.warn(
            "append_child_task is deprecated, use add_child_task instead",
            DeprecationWarning,
        )
        self.add_task(task)

    def extend_child_task_list(self, task_set: set[BaseTask]):
        """
        Extend target task_set to this workflow.

        .. deprecated:: Use updated_task_set instead.

        Args:
            task_set (set[BaseTask]): Target task set.
        """
        warnings.warn(
            "extend_child_task_list is deprecated, use updated_task_set instead",
            DeprecationWarning,
        )
        for task in task_set:
            self.add_task(task)

    def add_task(self, task: BaseTask):
        """
        Add target task to this workflow.

        Args:
            task (BaseTask): Target task.
        """
        if not isinstance(task, BaseTask):
            raise TypeError(f"task must be BaseTask, but got {type(task)}")
        self.task_set.add(task)
        task.parent_workflow_id = self.ID

    def update_task_set(self, task_set: set[BaseTask]):
        """
        Update target task_set to this workflow.

        Args:
            task_set (set[BaseTask]): Target task set.
        """
        for task in task_set:
            self.add_task(task)

    def create_task(
        self,
        name: str = None,
        ID: str = None,
        default_work_amount: float = None,
        work_amount_progress_of_unit_step_time: float = None,
        input_task_id_dependency_set: set[tuple[str, BaseTaskDependency]] = None,
        allocated_team_id_set: set[str] = None,
        allocated_workplace_id_set: set[str] = None,
        workplace_priority_rule: WorkplacePriorityRuleMode = WorkplacePriorityRuleMode.FSS,
        worker_priority_rule: ResourcePriorityRuleMode = ResourcePriorityRuleMode.MW,
        facility_priority_rule: ResourcePriorityRuleMode = ResourcePriorityRuleMode.SSP,
        need_facility: bool = False,
        target_component_id: str = None,
        default_progress: float = None,
        due_time: float = None,
        auto_task: bool = False,
        fixing_allocating_worker_id_set: set[str] = None,
        fixing_allocating_facility_id_set: set[str] = None,
        # Basic variables
        est: float = 0.0,
        eft: float = 0.0,
        lst: float = -1.0,
        lft: float = -1.0,
        remaining_work_amount: float = None,
        remaining_work_amount_record_list: list[float] = None,
        state: BaseTaskState = BaseTaskState.NONE,
        state_record_list: list[BaseTaskState] = None,
        allocated_worker_facility_id_tuple_set: set[tuple[str, str]] = None,
        allocated_worker_facility_id_tuple_set_record_list: list[
            set[tuple[str, str]]
        ] = None,
        # Advanced parameters for customized simulation
        additional_work_amount: float = None,
        # Advanced variables for customized simulation
        additional_task_flag: bool = False,
        actual_work_amount: float = None,
    ):
        """
        Create a BaseTask instance and add it to this workflow.

        Args:
            name (str, optional): Name of this task. Defaults to None -> "New Task".
            ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
            default_work_amount (float, optional): Default workamount of this BaseTask. Defaults to None -> 10.0.
            work_amount_progress_of_unit_step_time (float, optional): Baseline of work amount progress of unit step time. Default to None -> 1.0.
            input_task_id_dependency_set (set(tuple(str, BaseTaskDependency)), optional): Set of input BaseTask id and type of dependency(FS, SS, SF, F/F) tuple. Defaults to None -> set().
            allocated_team_id_set (set[str], optional): Set of allocated BaseTeam id. Defaults to None -> set().
            allocated_workplace_id_set (set[str], optional): Set of allocated BaseWorkplace id. Defaults to None -> set().
            workplace_priority_rule (WorkplacePriorityRuleMode, optional): Workplace priority rule for simulation. Defaults to WorkplacePriorityRuleMode.FSS.
            worker_priority_rule (ResourcePriorityRule, optional): Worker priority rule for simulation. Defaults to ResourcePriorityRule.SSP.
            facility_priority_rule (ResourcePriorityRule, optional): Task priority rule for simulation. Defaults to TaskPriorityRule.TSLACK.
            need_facility (bool, optional): Whether one facility is needed for performing this task or not. Defaults to False.
            target_component_id (str, optional): Target BaseComponent id. Defaults to None.
            default_progress (float, optional): Progress before starting simulation (0.0 ~ 1.0). Defaults to None -> 0.0.
            due_time (int, optional): Due time. Defaults to None -> int(-1).
            auto_task (bool, optional): If True, this task is performed automatically even if there are no allocated workers. Defaults to False.
            fixing_allocating_worker_id_set (set[str], optional): Allocating worker ID set for fixing allocation in simulation. Defaults to None.
            fixing_allocating_facility_id_set (set[str], optional): Allocating facility ID set for fixing allocation in simulation. Defaults to None.
            est (float, optional): Earliest start time of CPM. This will be updated step by step. Defaults to 0.0.
            eft (float, optional): Earliest finish time of CPM. This will be updated step by step. Defaults to 0.0.
            lst (float, optional): Latest start time of CPM. This will be updated step by step. Defaults to -1.0.
            lft (float, optional): Latest finish time of CPM. This will be updated step by step. Defaults to -1.0.
            remaining_work_amount (float, optional): Remaining workamount in simulation. Defaults to None -> default_work_amount * (1.0 - default_progress).
            remaining_work_amount_record_list (List[float], optional): Record of remaining workamount in simulation. Defaults to None -> [].
            state (BaseTaskState, optional): State of this task in simulation. Defaults to BaseTaskState.NONE.
            state_record_list (List[BaseTaskState], optional): Record list of state. Defaults to None -> [].
            allocated_worker_facility_id_tuple_set (set(tuple(str, str)), optional): State of allocating worker and facility id tuple set in simulation. Defaults to None -> set().
            allocated_worker_facility_id_tuple_set_record_list (List[set[tuple(str, str)]], optional): State of allocating worker and facility id tuple set in simulation. Defaults to None -> [].
            additional_work_amount (float, optional): Advanced parameter. Defaults to None.
            additional_task_flag (bool, optional): Advanced variable. Defaults to False.
            actual_work_amount (float, optional): Advanced variable. Default to None -> default_work_amount*(1.0-default_progress)

        Returns:
            BaseTask: The created task.
        """
        task = BaseTask(
            name=name,
            ID=ID,
            default_work_amount=default_work_amount,
            work_amount_progress_of_unit_step_time=work_amount_progress_of_unit_step_time,
            input_task_id_dependency_set=input_task_id_dependency_set,
            allocated_team_id_set=allocated_team_id_set,
            allocated_workplace_id_set=allocated_workplace_id_set,
            workplace_priority_rule=workplace_priority_rule,
            worker_priority_rule=worker_priority_rule,
            facility_priority_rule=facility_priority_rule,
            need_facility=need_facility,
            target_component_id=target_component_id,
            default_progress=default_progress,
            due_time=due_time,
            auto_task=auto_task,
            fixing_allocating_worker_id_set=fixing_allocating_worker_id_set,
            fixing_allocating_facility_id_set=fixing_allocating_facility_id_set,
            # Basic variables
            est=est,
            eft=eft,
            lst=lst,
            lft=lft,
            remaining_work_amount=remaining_work_amount,
            remaining_work_amount_record_list=remaining_work_amount_record_list,
            state=state,
            state_record_list=state_record_list,
            allocated_worker_facility_id_tuple_set=allocated_worker_facility_id_tuple_set,
            allocated_worker_facility_id_tuple_set_record_list=allocated_worker_facility_id_tuple_set_record_list,
            # Advanced parameters for customized simulation
            additional_work_amount=additional_work_amount,
            # Advanced variables for customized simulation
            additional_task_flag=additional_task_flag,
            actual_work_amount=actual_work_amount,
        )
        self.add_task(task)
        return task

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
            task_set=[t.export_dict_json_data() for t in self.task_set],
            critical_path_length=self.critical_path_length,
        )
        return dict_json_data

    def read_json_data(self, json_data: dict):
        """
        Read the JSON data for creating BaseWorkflow instance.

        Args:
            json_data (dict): JSON data.
        """
        self.name = json_data["name"]
        self.ID = json_data["ID"]
        self.task_set = set()
        j_list = json_data["task_set"]
        for j in j_list:
            if j["type"] == "BaseTask":
                self.task_set.add(
                    BaseTask(
                        name=j["name"],
                        ID=j["ID"],
                        default_work_amount=j["default_work_amount"],
                        work_amount_progress_of_unit_step_time=j[
                            "work_amount_progress_of_unit_step_time"
                        ],
                        input_task_id_dependency_set=set(
                            (id, BaseTaskDependency(dependency))
                            for id, dependency in j["input_task_id_dependency_set"]
                        ),
                        allocated_team_id_set=set(j["allocated_team_id_set"]),
                        allocated_workplace_id_set=set(j["allocated_workplace_id_set"]),
                        need_facility=j["need_facility"],
                        target_component_id=j["target_component_id"],
                        default_progress=j["default_progress"],
                        due_time=j["due_time"],
                        auto_task=j["auto_task"],
                        fixing_allocating_worker_id_set=(
                            set(j["fixing_allocating_worker_id_set"])
                            if j["fixing_allocating_worker_id_set"] is not None
                            else None
                        ),
                        fixing_allocating_facility_id_set=(
                            set(j["fixing_allocating_facility_id_set"])
                            if j["fixing_allocating_facility_id_set"] is not None
                            else None
                        ),
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
                        allocated_worker_facility_id_tuple_set=j[
                            "allocated_worker_facility_id_tuple_set"
                        ],
                        allocated_worker_facility_id_tuple_set_record_list=j[
                            "allocated_worker_facility_id_tuple_set_record_list"
                        ],
                    )
                )
            elif j["type"] == "BaseSubProjectTask":
                self.task_set.add(
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
                        input_task_id_dependency_set=set(
                            j["input_task_id_dependency_set"]
                        ),
                        allocated_team_id_set=set(j["allocated_team_id_set"]),
                        allocated_workplace_id_set=set(j["allocated_workplace_id_set"]),
                        need_facility=j["need_facility"],
                        target_component_id=j["target_component_id"],
                        default_progress=j["default_progress"],
                        due_time=j["due_time"],
                        auto_task=j["auto_task"],
                        fixing_allocating_worker_id_set=set(
                            j["fixing_allocating_worker_id_set"]
                        ),
                        fixing_allocating_facility_id_set=set(
                            j["fixing_allocating_facility_id_set"]
                        ),
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
                        allocated_worker_facility_id_tuple_set=j[
                            "allocated_worker_facility_id_tuple_set"
                        ],
                        allocated_worker_facility_id_tuple_set_record_list=j[
                            "allocated_worker_facility_id_tuple_set_record_list"
                        ],
                    )
                )

        self.critical_path_length = json_data["critical_path_length"]

    def extract_none_task_set(self, target_time_list: list[int]):
        """
        Extract NONE task set from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract none task from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseTask]: List of BaseTask.
        """
        return self.__extract_state_task_set(target_time_list, BaseTaskState.NONE)

    def extract_ready_task_set(self, target_time_list: list[int]):
        """
        Extract READY task set from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract ready task from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseTask]: List of BaseTask.
        """
        return self.__extract_state_task_set(target_time_list, BaseTaskState.READY)

    def extract_working_task_set(self, target_time_list: list[int]):
        """
        Extract WORKING task list from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract working task from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseTask]: List of BaseTask.
        """
        return self.__extract_state_task_set(target_time_list, BaseTaskState.WORKING)

    def extract_finished_task_set(self, target_time_list: list[int]):
        """
        Extract FINISHED task list from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract finished task from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseTask]: List of BaseTask.
        """
        return self.__extract_state_task_set(target_time_list, BaseTaskState.FINISHED)

    def __extract_state_task_set(
        self, target_time_list: list[int], target_state: BaseTaskState
    ):
        """
        Extract state task list from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract target_state task from time 2 to time 4, you must set [2, 3, 4] to this argument.
            target_state (BaseTaskState): Target state.

        Returns:
            List[BaseTask]: List of BaseTask.
        """
        return {
            task
            for task in self.task_set
            if all(
                len(task.state_record_list) > time
                and task.state_record_list[time] == target_state
                for time in target_time_list
            )
        }

    def get_task_set(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        default_work_amount: float = None,
        input_task_id_dependency_set: set[tuple[str, BaseTaskDependency]] = None,
        allocated_team_id_set: set[str] = None,
        allocated_workplace_id_set: set[str] = None,
        need_facility: bool = None,
        target_component_id: str = None,
        default_progress: float = None,
        due_time: int = None,
        auto_task: bool = None,
        fixing_allocating_worker_id_set: set[str] = None,
        fixing_allocating_facility_id_set: set[str] = None,
        # search param
        est: float = None,
        eft: float = None,
        lst: float = None,
        lft: float = None,
        remaining_work_amount: float = None,
        state: BaseTaskState = None,
        allocated_worker_facility_id_tuple_set: set[tuple[str, str]] = None,
        allocated_worker_facility_id_tuple_set_record_list: list[
            set[tuple[str, str]]
        ] = None,
    ):
        """
        Get task list by using search conditions related to BaseTask parameter.

        If there is no searching condition, this function returns all `task_set`

        Args:
            name (str, optional): Target task name. Defaults to None.
            ID (str, optional): Target task ID. Defaults to None.
            default_work_amount (float, optional): Target task default_work_amount. Defaults to None.
            input_task_id_dependency_set (set(tuple(str, BaseTaskDependency)), optional): Target task input_task_id_dependency_set. Defaults to None.
            allocated_team_id_set (set[str], optional): Target task allocated_team_id_set. Defaults to None.
            allocated_workplace_id_set (set[str], optional): Target task allocated_workplace_id_set. Defaults to None.
            need_facility (bool, optional): Target task need_facility. Defaults to None.
            target_component_id (str, optional): Target task target_component_id. Defaults to None.
            default_progress (float, optional): Target task default_progress. Defaults to None.
            due_time (int, optional): Target task due_time. Defaults to None.
            auto_task (bool, optional): Target task auto_task. Defaults to None.
            fixing_allocating_worker_id_set (set[str], optional): Target task fixing_allocating_worker_id_set. Defaults to None.
            fixing_allocating_facility_id_set (set[str], optional): Target task fixing_allocating_facility_id_set. Defaults to None.
            est (float, optional): Target task est. Defaults to None.
            eft (float, optional): Target task eft. Defaults to None.
            lst (float, optional): Target task lst. Defaults to None.
            lft (float, optional): Target task lft. Defaults to None.
            remaining_work_amount (float, optional): Target task remaining_work_amount. Defaults to None.
            state (BaseTaskState, optional): Target task state. Defaults to None.
            allocated_worker_facility_id_tuple_set (set(tuple(str, str)), optional): Target task allocated_worker_facility_id_tuple_set. Defaults to None.
            allocated_worker_facility_id_tuple_set_record_list (List[set(tuple(str, str))], optional): Target task allocated_worker_facility_id_tuple_set_record_list. Defaults to None.

        Returns:
            List[BaseTask]: List of BaseTask.
        """
        task_set = self.task_set
        if name is not None:
            task_set = set(filter(lambda task: task.name == name, task_set))
        if ID is not None:
            task_set = set(filter(lambda task: task.ID == ID, task_set))
        if default_work_amount is not None:
            task_set = set(
                filter(
                    lambda task: task.default_work_amount == default_work_amount,
                    task_set,
                )
            )
        if input_task_id_dependency_set is not None:
            task_set = set(
                filter(
                    lambda task: task.input_task_id_dependency_set
                    == input_task_id_dependency_set,
                    task_set,
                )
            )
        if allocated_team_id_set is not None:
            task_set = set(
                filter(
                    lambda task: task.allocated_team_id_set == allocated_team_id_set,
                    task_set,
                )
            )
        if allocated_workplace_id_set is not None:
            task_set = set(
                filter(
                    lambda task: task.allocated_workplace_id_set
                    == allocated_workplace_id_set,
                    task_set,
                )
            )
        if need_facility is not None:
            task_set = set(
                filter(lambda task: task.need_facility == need_facility, task_set)
            )
        if target_component_id is not None:
            task_set = set(
                filter(
                    lambda task: task.target_component_id == target_component_id,
                    task_set,
                )
            )
        if default_progress is not None:
            task_set = set(
                filter(lambda task: task.default_progress == default_progress, task_set)
            )
        if due_time is not None:
            task_set = set(filter(lambda task: task.due_time == due_time, task_set))
        if auto_task is not None:
            task_set = set(filter(lambda task: task.auto_task == auto_task, task_set))
        if fixing_allocating_worker_id_set is not None:
            task_set = set(
                filter(
                    lambda task: task.fixing_allocating_worker_id_set
                    == fixing_allocating_worker_id_set,
                    task_set,
                )
            )
        if fixing_allocating_facility_id_set is not None:
            task_set = set(
                filter(
                    lambda task: task.fixing_allocating_facility_id_set
                    == fixing_allocating_facility_id_set,
                    task_set,
                )
            )
        if est is not None:
            task_set = set(filter(lambda task: task.est == est, task_set))
        if eft is not None:
            task_set = set(filter(lambda task: task.eft == eft, task_set))
        if lst is not None:
            task_set = set(filter(lambda task: task.lst == lst, task_set))
        if lft is not None:
            task_set = set(filter(lambda task: task.lft == lft, task_set))
        if remaining_work_amount is not None:
            task_set = set(
                filter(
                    lambda task: task.remaining_work_amount == remaining_work_amount,
                    task_set,
                )
            )
        if state is not None:
            task_set = set(filter(lambda task: task.state == state, task_set))
        if allocated_worker_facility_id_tuple_set is not None:
            task_set = set(
                filter(
                    lambda task: task.allocated_worker_facility_id_tuple_set
                    == allocated_worker_facility_id_tuple_set,
                    task_set,
                )
            )
        if allocated_worker_facility_id_tuple_set_record_list is not None:
            task_set = set(
                filter(
                    lambda task: task.allocated_worker_facility_id_tuple_set_record_list
                    == allocated_worker_facility_id_tuple_set_record_list,
                    task_set,
                )
            )
        return task_set

    def initialize(self, state_info: bool = True, log_info: bool = True):
        """
        Initialize the changeable variables of BaseWorkflow including PERT calculation.

        If `state_info` is True, the following attributes are initialized:
            - `critical_path_length`
            - PERT data
            - The state of each task after all tasks are initialized.

        BaseTask in `task_set` are also initialized by this function.

        Args:
            state_info (bool, optional): Whether to initialize state information. Defaults to True.
            log_info (bool, optional): Whether to initialize log information. Defaults to True.
        """
        for task in self.task_set:
            task.initialize(state_info=state_info, log_info=log_info)
            if task.parent_workflow_id is None:
                task.parent_workflow_id = self.ID
        if state_info:
            self.critical_path_length = 0.0
            self.update_pert_data(0)

    def reverse_log_information(self):
        """Reverse log information of all."""
        for t in self.task_set:
            t.reverse_log_information()

    def record(self, working: bool = True):
        """Record the state of all tasks in `task_set`.

        Args:
            working (bool, optional): Whether to record as working. Defaults to True.
        """
        if working:
            for task in self.task_set:
                alloc_append = (
                    task.allocated_worker_facility_id_tuple_set_record_list.append
                )
                state_append = task.state_record_list.append
                remain_append = task.remaining_work_amount_record_list.append

                alloc_append(task.allocated_worker_facility_id_tuple_set)
                state_append(task.state)
                remain_append(task.remaining_work_amount)
        else:
            READY = BaseTaskState.READY
            WORKING = BaseTaskState.WORKING
            for task in self.task_set:
                alloc_append = (
                    task.allocated_worker_facility_id_tuple_set_record_list.append
                )
                state_append = task.state_record_list.append
                remain_append = task.remaining_work_amount_record_list.append

                alloc_append(task.allocated_worker_facility_id_tuple_set)
                s = task.state
                state_append(READY if s is WORKING else s)
                remain_append(task.remaining_work_amount)

    def update_pert_data(self, time: int):
        """
        Update PERT data (est, eft, lst, lft) of each BaseTask in task_set.

        Args:
            time (int): Simulation time.
        """
        sorted_tasks, input_id_to_output_tasks = self.__topological_sort()
        self.__set_est_eft_data(time, sorted_tasks, input_id_to_output_tasks)
        self.__set_lst_lft_critical_path_data(sorted_tasks, input_id_to_output_tasks)

    def __get_topology(self):
        if self._topology_cache is not None:
            return self._topology_cache

        task_by_id = {task.ID: task for task in self.task_set}

        indegree = {task.ID: 0 for task in self.task_set}
        input_id_to_output_tasks: dict = {}

        for task in self.task_set:
            for input_task_id, dep in task.input_task_id_dependency_set:
                input_id_to_output_tasks.setdefault(input_task_id, []).append(
                    (task, dep)
                )
                indegree[task.ID] += 1

        queue = deque([task for task in self.task_set if indegree[task.ID] == 0])
        sorted_tasks: list = []

        while queue:
            cur = queue.popleft()
            sorted_tasks.append(cur)
            for nxt, _ in input_id_to_output_tasks.get(cur.ID, []):
                indegree[nxt.ID] -= 1
                if indegree[nxt.ID] == 0:
                    queue.append(nxt)

        if len(sorted_tasks) != len(self.task_set):
            remaining_ids = {tid for tid, deg in indegree.items() if deg > 0}

            adj: dict[str, list[str]] = {}
            for src_id, outs in input_id_to_output_tasks.items():
                if src_id in remaining_ids:
                    ids = [task.ID for (task, _) in outs if task.ID in remaining_ids]
                    if ids:
                        adj[src_id] = ids

            cycle = self._find_cycle_in_adj(adj, task_by_id)
            if cycle:
                cycle_str = " -> ".join(cycle + [cycle[0]])
                raise ValueError(
                    "Graph has a cycle. Topological sort failed. "
                    f"Example cycle: {cycle_str}"
                )
        self._topology_cache = (sorted_tasks, input_id_to_output_tasks)
        return self._topology_cache

    def _find_cycle_in_adj(
        self, adj: dict[str, list[str]], task_by_id: dict[str, object]
    ) -> list[str] | None:
        """Find and return one cycle as a list of formatted 'Name[ID]' strings."""
        visited: set[str] = set()
        stack: set[str] = set()
        parent: dict[str, str] = {}

        def fmt(tid: str) -> str:
            """Format as 'Name[ID]'."""
            task = task_by_id.get(tid)
            if task is None:
                return f"[{tid}]"
            name = (
                getattr(task, "name", None) or getattr(task, "Name", None) or "Unknown"
            )
            return f"{name}[{tid}]"

        def dfs(u: str) -> list[str] | None:
            visited.add(u)
            stack.add(u)
            for v in adj.get(u, []):
                if v not in visited:
                    parent[v] = u
                    found = dfs(v)
                    if found:
                        return found
                elif v in stack:
                    # Reconstruct cycle
                    cycle = [v]
                    cur = u
                    while cur != v:
                        cycle.append(cur)
                        cur = parent[cur]
                    cycle.reverse()
                    # Convert IDs to "Name[ID]" for readability
                    return [fmt(tid) for tid in cycle]
            stack.remove(u)
            return None

        for node in adj.keys():
            if node not in visited:
                found = dfs(node)
                if found:
                    return found
        return None

    def __topological_sort(self):
        """Return the set of tasks in topological order using Kahn's algorithm.

        Returns:
            tuple[list[BaseTask], dict]:
                - A list of tasks sorted in topological order.
                - A dictionary mapping input task IDs to lists of (task, dependency) tuples.
        Raises:
            ValueError: If the task graph contains a cycle and topological sort fails.
        """
        return self.__get_topology()

    def __set_est_eft_data(
        self, time: int, sorted_tasks: list[BaseTask], input_id_to_output_tasks: dict
    ):
        for task in self.task_set:
            task.est = time
            task.eft = time

        for task in sorted_tasks:
            if len(task.input_task_id_dependency_set) == 0:
                task.est = time
                task.eft = time + task.remaining_work_amount
            for next_task, dependency in input_id_to_output_tasks.get(task.ID, []):
                if dependency == BaseTaskDependency.FS:
                    est = task.eft
                    eft = est + next_task.remaining_work_amount
                elif dependency == BaseTaskDependency.SS:
                    est = task.est
                    eft = est + next_task.remaining_work_amount
                elif dependency == BaseTaskDependency.FF:
                    eft_candidate = max(next_task.eft, task.eft)
                    est = max(eft_candidate - next_task.remaining_work_amount, 0)
                    eft = est + next_task.remaining_work_amount
                elif dependency == BaseTaskDependency.SF:
                    eft_candidate = max(next_task.eft, task.est)
                    est = max(eft_candidate - next_task.remaining_work_amount, 0)
                    eft = est + next_task.remaining_work_amount
                else:
                    est = task.eft
                    eft = est + next_task.remaining_work_amount

                next_task.est = max(next_task.est, est)
                next_task.eft = max(next_task.eft, eft)

    def __set_lst_lft_critical_path_data(
        self, sorted_tasks: list[BaseTask], input_id_to_output_tasks: dict
    ):
        for task in self.task_set:
            task.lft = float("inf")
            task.lst = float("inf")

        task_id_map = {task.ID: task for task in self.task_set}
        tasks_with_outputs = {
            task_id_map[input_task_id]
            for task in self.task_set
            for (input_task_id, _) in task.input_task_id_dependency_set
            if input_task_id in task_id_map
        }
        output_task_set = set(self.task_set) - tasks_with_outputs

        self.critical_path_length = max(task.eft for task in output_task_set)

        for task in output_task_set:
            task.lft = self.critical_path_length
            task.lst = task.lft - task.remaining_work_amount

        for task in reversed(sorted_tasks):
            for prev_task_id, dependency in task.input_task_id_dependency_set:
                prev_task = task_id_map.get(prev_task_id)
                if prev_task is None:
                    continue

                # Update lft, lst according to dependency type
                if dependency == BaseTaskDependency.FS:
                    lft = task.lst
                    lst = lft - prev_task.remaining_work_amount
                elif dependency == BaseTaskDependency.SS:
                    lst = task.lst
                    lft = lst + prev_task.remaining_work_amount
                elif dependency == BaseTaskDependency.FF:
                    lst = task.lst
                    lft = min(task.lft, lst + prev_task.remaining_work_amount)
                elif dependency == BaseTaskDependency.SF:
                    lst = min(task.lft, task.lst)
                    lft = lst + prev_task.remaining_work_amount
                else:  # fallback
                    lft = task.lst
                    lst = lft - prev_task.remaining_work_amount

                prev_task.lst = min(prev_task.lst, lst)
                prev_task.lft = min(prev_task.lft, lft)

    def reverse_dependencies(self):
        """
        Reverse all task dependencies in task_set.

        Note:
            This method is developed only for backward simulation.
        """
        task_id_map = {task.ID: task for task in self.task_set}
        output_task_map = {task: set() for task in self.task_set}
        for task in self.task_set:
            for input_task_id, dependency in task.input_task_id_dependency_set:
                input_task = task_id_map.get(input_task_id)
                if input_task is not None:
                    output_task_map[input_task].add((task.ID, dependency))
        for task in self.task_set:
            task.dummy_output_task_id_dependency_set = task.input_task_id_dependency_set
            task.dummy_input_task_id_dependency_set = output_task_map[task]
        for task in self.task_set:
            task.input_task_id_dependency_set = task.dummy_input_task_id_dependency_set
            del (
                task.dummy_input_task_id_dependency_set,
                task.dummy_output_task_id_dependency_set,
            )

    def remove_absence_time_list(self, absence_time_list: list[int]):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]): List of absence step time in simulation.
        """
        for t in self.task_set:
            if not isinstance(t, BaseSubProjectTask):
                t.remove_absence_time_list(absence_time_list)

    def insert_absence_time_list(self, absence_time_list: list[int]):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]): List of absence step time in simulation.
        """
        for t in self.task_set:
            if not isinstance(t, BaseSubProjectTask):
                t.insert_absence_time_list(absence_time_list)

    def print_log(self, target_step_time: int):
        """
        Print log in `target_step_time`.

        Args:
            target_step_time (int): Target step time of printing log.
        """
        for task in self.task_set:
            task.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """
        Print all log in chronological order.

        Args:
            backward (bool, optional): If True, print logs in reverse order. Defaults to False.
        """
        if len(self.task_set) > 0:
            sample_task = next(iter(self.task_set))
            n = len(sample_task.state_record_list)
            if backward:
                for i in range(n):
                    t = n - 1 - i
                    print("TIME: ", t)
                    self.print_log(t)
            else:
                for t in range(n):
                    print("TIME: ", t)
                    self.print_log(t)

    def plot_simple_gantt(
        self,
        target_id_order_list: list[str] = None,
        finish_margin: float = 1.0,
        print_workflow_name: bool = True,
        view_auto_task: bool = False,
        view_ready: bool = False,
        task_color: str = "#00EE00",
        auto_task_color: str = "#005500",
        ready_color: str = "#C0C0C0",
        figsize: tuple[float, float] = None,
        dpi: float = 100.0,
        save_fig_path: str = None,
    ):
        """
        Plot Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_workflow_name (bool, optional): Print workflow name or not. Defaults to True.
            view_auto_task (bool, optional): View auto_task or not. Defaults to False.
            view_ready (bool, optional): View READY time or not. Defaults to False.
            task_color (str, optional): Task color setting information. Defaults to "#00EE00".
            auto_task_color (str, optional): Auto Task color setting information. Defaults to "#005500".
            ready_color (str, optional): Ready Task color setting information. Defaults to "#C0C0C0".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            fig: Figure in plt.subplots().
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig, gnt = self.create_simple_gantt(
            target_id_order_list=target_id_order_list,
            finish_margin=finish_margin,
            print_workflow_name=print_workflow_name,
            view_auto_task=view_auto_task,
            view_ready=view_ready,
            task_color=task_color,
            auto_task_color=auto_task_color,
            ready_color=ready_color,
            figsize=figsize,
            dpi=dpi,
            save_fig_path=save_fig_path,
        )
        _ = gnt  # Unused variable, but needed for compatibility
        return fig

    def create_simple_gantt(
        self,
        target_id_order_list: list[str] = None,
        finish_margin: float = 1.0,
        print_workflow_name: bool = True,
        view_auto_task: bool = False,
        view_ready: bool = False,
        task_color: str = "#00EE00",
        auto_task_color: str = "#005500",
        ready_color: str = "#C0C0C0",
        figsize: tuple[float, float] = None,
        dpi: float = 100.0,
        save_fig_path: str = None,
    ):
        """
        Create Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_workflow_name (bool, optional): Print workflow name or not. Defaults to True.
            view_auto_task (bool, optional): View auto_task or not. Defaults to False.
            view_ready (bool, optional): View READY time or not. Defaults to False.
            task_color (str, optional): Task color setting information. Defaults to "#00EE00".
            auto_task_color (str, optional): Auto Task color setting information. Defaults to "#005500".
            ready_color (str, optional): Ready Task color setting information. Defaults to "#C0C0C0".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            fig: Figure in plt.subplots().
            gnt: Axes in plt.subplots().
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig, gnt = plt.subplots()
        fig.figsize = figsize
        fig.dpi = dpi
        gnt.set_xlabel("step")
        gnt.grid(True)

        target_task_set = set(filter(lambda task: not task.auto_task, self.task_set))
        if view_auto_task:
            target_task_set = self.task_set

        target_instance_list = target_task_set
        if target_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in target_task_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_id_order_list
                if tid in id_to_instance
            ]
        target_instance_list = list(reversed(list(target_instance_list)))

        y_ticks = [10 * (n + 1) for n in range(len(target_instance_list))]
        y_tick_labels = [task.name for task in target_instance_list]
        if print_workflow_name:
            y_tick_labels = [
                f"{self.name}: {task.name}" for task in target_instance_list
            ]

        gnt.set_yticks(y_ticks)
        gnt.set_yticklabels(y_tick_labels)

        for time, task in enumerate(target_instance_list):
            (
                ready_time_list,
                working_time_list,
            ) = task.get_time_list_for_gantt_chart(finish_margin=finish_margin)

            if view_ready:
                gnt.broken_barh(
                    ready_time_list, (y_ticks[time] - 5, 9), facecolors=(ready_color)
                )
            if task.auto_task:
                gnt.broken_barh(
                    working_time_list,
                    (y_ticks[time] - 5, 9),
                    facecolors=(auto_task_color),
                )
            else:
                gnt.broken_barh(
                    working_time_list, (y_ticks[time] - 5, 9), facecolors=(task_color)
                )

        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig, gnt

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        target_id_order_list: list[str] = None,
        finish_margin: float = 1.0,
        print_workflow_name: bool = True,
        view_ready: bool = False,
    ):
        """
        Create data for gantt plotly from task_set.

        Args:
            init_datetime (datetime.datetime): Start datetime of project.
            unit_timedelta (datetime.timedelta): Unit time of simulation.
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_workflow_name (bool, optional): Print workflow name or not. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to False.

        Returns:
            list[dict]: Gantt plotly information of this BaseWorkflow.
        """
        df = []
        target_instance_list = self.task_set
        if target_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.task_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_id_order_list
                if tid in id_to_instance
            ]
        for task in target_instance_list:
            (
                ready_time_list,
                working_time_list,
            ) = task.get_time_list_for_gantt_chart(finish_margin=finish_margin)

            task_name = task.name
            if print_workflow_name:
                task_name = f"{self.name}: {task.name}"

            if view_ready:
                for from_time, length in ready_time_list:
                    to_time = from_time + length
                    df.append(
                        {
                            "Task": task_name,
                            "Start": (
                                init_datetime + from_time * unit_timedelta
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "Finish": (
                                init_datetime + to_time * unit_timedelta
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "State": "READY",
                            "Type": "Task",
                        }
                    )
            for from_time, length in working_time_list:
                to_time = from_time + length
                df.append(
                    {
                        "Task": task_name,
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

    def create_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        target_id_order_list: list[str] = None,
        title: str = "Gantt Chart",
        colors: dict[str, str] = None,
        index_col: str = None,
        showgrid_x: bool = True,
        showgrid_y: bool = True,
        group_tasks: bool = True,
        show_colorbar: bool = True,
        finish_margin: float = 1.0,
        print_workflow_name: bool = True,
        view_ready: bool = False,
        save_fig_path: str = None,
    ):
        """
        Create Gantt chart by plotly.

        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime): Start datetime of project.
            unit_timedelta (datetime.timedelta): Unit time of simulation.
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            title (str, optional): Title of Gantt chart. Defaults to "Gantt Chart".
            colors (Dict[str, str], optional): Color setting of plotly Gantt chart. Defaults to None -> dict(WORKING="rgb(146, 237, 5)", READY="rgb(107, 127, 135)").
            index_col (str, optional): index_col of plotly Gantt chart. Defaults to None -> "State".
            showgrid_x (bool, optional): showgrid_x of plotly Gantt chart. Defaults to True.
            showgrid_y (bool, optional): showgrid_y of plotly Gantt chart. Defaults to True.
            group_tasks (bool, optional): group_tasks of plotly Gantt chart. Defaults to True.
            show_colorbar (bool, optional): show_colorbar of plotly Gantt chart. Defaults to True.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_workflow_name (bool, optional): Print workflow name or not. Defaults to True.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            figure: Figure for a gantt chart.
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
            target_id_order_list=target_id_order_list,
            finish_margin=finish_margin,
            print_workflow_name=print_workflow_name,
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
            networkx.DiGraph: Directed graph of the workflow.
        """
        g = nx.DiGraph()

        # 1. add all nodes
        for task in self.task_set:
            g.add_node(task)

        task_id_map = {task.ID: task for task in self.task_set}

        # 2. add all edges
        for task in self.task_set:
            for input_task_id, _ in task.input_task_id_dependency_set:
                input_task = task_id_map.get(input_task_id)
                g.add_edge(input_task, task)

        return g

    def draw_networkx(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        arrows: bool = True,
        task_node_color: str = "#00EE00",
        auto_task_node_color: str = "#005500",
        figsize: tuple[float, float] = None,
        dpi: float = 100.0,
        save_fig_path: str = None,
        **kwargs,
    ):
        """
        Draw networkx.

        Args:
            g (networkx.Digraph, optional): The information of networkx graph. Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional): Layout of networkx. Defaults to None -> networkx.spring_layout(g).
            arrows (bool, optional): Digraph or Graph(no arrows). Defaults to True.
            task_node_color (str, optional): Node color setting information. Defaults to "#00EE00".
            auto_task_node_color (str, optional): Node color setting information. Defaults to "#005500".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.
            **kwargs: Other networkx settings.

        Returns:
            figure: Figure for a network.
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig = plt.figure(figsize=figsize, dpi=dpi)
        g = g if g is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(g)

        # normal task
        normal_task_set = {task for task in self.task_set if not task.auto_task}
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=normal_task_set,
            node_color=task_node_color,
            **kwargs,
        )

        # auto task
        auto_task_set = {task for task in self.task_set if task.auto_task}
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=auto_task_set,
            node_color=auto_task_node_color,
            **kwargs,
        )

        nx.draw_networkx_labels(g, pos, **kwargs)
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
        task_node_color: str = "#00EE00",
        auto_task_node_color: str = "#005500",
    ):
        """
        Get nodes and edges information of plotly network.

        Args:
            g (networkx.Digraph, optional): The information of networkx graph. Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional): Layout of networkx. Defaults to None -> networkx.spring_layout(g).
            node_size (int, optional): Node size setting information. Defaults to 20.
            task_node_color (str, optional): Node color setting information. Defaults to "#00EE00".
            auto_task_node_color (str, optional): Node color setting information. Defaults to "#005500".

        Returns:
            task_node_trace: Normal Task Node information of plotly network.
            auto_task_node_trace: Auto Task Node information of plotly network.
            edge_trace: Edge information of plotly network.
        """
        g = g if g is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(g)

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

        for node in g.nodes:
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

        for edge in g.edges:
            x = edge[0]
            y = edge[1]
            x_pos_x, x_pos_y = pos[x]
            y_pos_x, y_pos_y = pos[y]
            edge_trace["x"] += (x_pos_x, y_pos_x)
            edge_trace["y"] += (x_pos_y, y_pos_y)

        return task_node_trace, auto_task_node_trace, edge_trace

    def draw_plotly_network(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        title: str = "Workflow",
        node_size: int = 20,
        task_node_color: str = "#00EE00",
        auto_task_node_color: str = "#005500",
        save_fig_path=None,
    ):
        """
        Draw plotly network.

        Args:
            g (networkx.Digraph, optional): The information of networkx graph. Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional): Layout of networkx. Defaults to None -> networkx.spring_layout(g).
            title (str, optional): Figure title of this network. Defaults to "Workflow".
            node_size (int, optional): Node size setting information. Defaults to 20.
            task_node_color (str, optional): Node color setting information. Defaults to "#00EE00".
            auto_task_node_color (str, optional): Node color setting information. Defaults to "#005500".
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            figure: Figure for a network.
        """
        g = g if g is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(g)
        (
            task_node_trace,
            auto_task_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(
            g,
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

    def get_target_task_mermaid_diagram(
        self,
        target_task_set: set[BaseTask],
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        link_type_str: str = "-->",
        print_dependency_type: bool = False,
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of target task.

        Args:
            target_task_set (set[BaseTask]): Set of target tasks.
            shape_task (str, optional): Shape of mermaid diagram. Defaults to "rect".
            print_work_amount_info (bool, optional): Print work amount information or not. Defaults to True.
            link_type_str (str, optional): Link type string. Defaults to "-->".
            print_dependency_type (bool, optional): Print dependency type information or not. Defaults to False.
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for task in target_task_set:
            if task in self.task_set:
                list_of_lines.extend(
                    task.get_mermaid_diagram(
                        shape=shape_task,
                        print_work_amount_info=print_work_amount_info,
                    )
                )
        task_id_map = {task.ID: task for task in target_task_set}

        for task in target_task_set:
            if task in self.task_set:
                dependency_type_mark = ""
                for input_task_id, dependency in task.input_task_id_dependency_set:
                    input_task = task_id_map.get(input_task_id, None)
                    if input_task in target_task_set:
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
            shape_task (str, optional): Shape of mermaid diagram. Defaults to "rect".
            print_work_amount_info (bool, optional): Print work amount information or not. Defaults to True.
            link_type_str (str, optional): Link type string. Defaults to "-->".
            print_dependency_type (bool, optional): Print dependency type information or not. Defaults to False.
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        return self.get_target_task_mermaid_diagram(
            target_task_set=self.task_set,
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            link_type_str=link_type_str,
            print_dependency_type=print_dependency_type,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def print_target_task_mermaid_diagram(
        self,
        target_task_set: set[BaseTask],
        orientations: str = "LR",
        shape_task: str = "rect",
        print_work_amount_info: bool = True,
        link_type_str: str = "-->",
        print_dependency_type: bool = False,
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of target task.

        Args:
            target_task_set (set[BaseTask]): Set of target tasks.
            orientations (str, optional): Orientation of mermaid diagram. See: https://mermaid.js.org/syntax/flowchart.html#direction. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram. Defaults to "rect".
            print_work_amount_info (bool, optional): Print work amount information or not. Defaults to True.
            link_type_str (str, optional): Link type string. Defaults to "-->".
            print_dependency_type (bool, optional): Print dependency type information or not. Defaults to False.
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_task_mermaid_diagram(
            target_task_set=target_task_set,
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            link_type_str=link_type_str,
            print_dependency_type=print_dependency_type,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

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
            orientations (str, optional): Orientation of mermaid diagram. See: https://mermaid.js.org/syntax/flowchart.html#direction. Defaults to "LR".
            shape_task (str, optional): Shape of mermaid diagram. Defaults to "rect".
            print_work_amount_info (bool, optional): Print work amount information or not. Defaults to True.
            link_type_str (str, optional): Link type string. Defaults to "-->".
            print_dependency_type (bool, optional): Print dependency type information or not. Defaults to False.
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
        """
        self.print_target_task_mermaid_diagram(
            target_task_set=self.task_set,
            orientations=orientations,
            shape_task=shape_task,
            print_work_amount_info=print_work_amount_info,
            link_type_str=link_type_str,
            print_dependency_type=print_dependency_type,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def get_gantt_mermaid(
        self,
        target_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get mermaid diagram of Gantt chart.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            section (bool, optional): Section or not. Defaults to True.
            range_time (tuple[int, int], optional): Range of Gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): Detailed information or not. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for tasks. Defaults to None.

        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        target_instance_list = self.task_set
        if target_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.task_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_id_order_list
                if tid in id_to_instance
            ]

        list_of_lines = []
        if section:
            list_of_lines.append(f"section {self.name}")
        for task in target_instance_list:
            list_of_lines.extend(
                task.get_gantt_mermaid_data(
                    range_time=range_time,
                    view_ready=view_ready,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_gantt_mermaid(
        self,
        target_id_order_list: list[str] = None,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Print mermaid diagram of Gantt chart.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            date_format (str, optional): Date format of mermaid diagram. Defaults to "X".
            axis_format (str, optional): Axis format of mermaid diagram. Defaults to "%s".
            section (bool, optional): Section or not. Defaults to True.
            range_time (tuple[int, int], optional): Range of Gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): Detailed information or not. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for tasks. Defaults to None.
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_gantt_mermaid(
            target_id_order_list=target_id_order_list,
            section=section,
            range_time=range_time,
            view_ready=view_ready,
            detailed_info=detailed_info,
            id_name_dict=id_name_dict,
        )
        print(*list_of_lines, sep="\n")
