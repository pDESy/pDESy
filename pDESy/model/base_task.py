#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_task."""

from __future__ import annotations

import abc
import sys
import uuid
import warnings
from enum import IntEnum
from typing import TYPE_CHECKING

from pDESy.model.mermaid_utils import (
    SingleNodeMermaidDiagramMixin,
    build_gantt_mermaid_steps_lines,
)
from pDESy.model.pdesy_utils import (
    build_time_lists_from_state_record,
    ComponentTaskCommonMixin,
    SingleNodeCommonMixin,
    SingleNodeLogJsonMixin,
)

from .base_priority_rule import ResourcePriorityRuleMode, WorkplacePriorityRuleMode

if TYPE_CHECKING:
    from pDESy.model.base_component import BaseComponent


class BaseTaskState(IntEnum):
    """BaseTaskState.

    Enum for representing the state of a task.

    Attributes:
        NONE (int): No state.
        READY (int): Ready to start.
        WORKING (int): Currently working.
        WORKING_ADDITIONALLY (int): Working additionally.
        FINISHED (int): Finished.
    """

    NONE = 0
    READY = 1
    WORKING = 2
    WORKING_ADDITIONALLY = 3
    FINISHED = -1


class BaseTaskDependency(IntEnum):
    """BaseTaskDependency.

    Enum for representing task dependency types.

    Attributes:
        FS (int): Finish to Start.
        SS (int): Start to Start.
        FF (int): Finish to Finish.
        SF (int): Start to Finish.
    """

    FS = 0  # Finish to Start
    SS = 1  # Start to Start
    FF = 2  # Finish to Finish
    SF = 3  # Finish to Start


class BaseTask(
    SingleNodeMermaidDiagramMixin,
    ComponentTaskCommonMixin,
    SingleNodeLogJsonMixin,
    SingleNodeCommonMixin,
    object,
    metaclass=abc.ABCMeta,
):
    """BaseTask.

    BaseTask class for expressing target workflow. This class will be used as a template.

    Args:
        name (str, optional): Name of this task. Defaults to None -> "New Task".
        ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
        default_work_amount (float, optional): Default workamount of this BaseTask. Defaults to None -> 10.0.
        work_amount_progress_of_unit_step_time (float, optional): Baseline of work amount progress of unit step time. Default to None -> 1.0.
        input_task_id_dependency_set (set(tuple(str, BaseTaskDependency)), optional): Set of input BaseTask id and type of dependency(FS, SS, SF, F/F) tuple. Defaults to None -> set().
        allocated_team_id_set (set[str], optional): Set of allocated BaseTeam id. Defaults to None -> set().
        allocated_workplace_id_set (set[str], optional): Set of allocated BaseWorkplace id. Defaults to None -> set().
        parent_workflow_id (str, optional): Parent workflow id. Defaults to None.
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
    """

    def __init__(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        default_work_amount: float = 10.0,
        work_amount_progress_of_unit_step_time: float = 1.0,
        input_task_id_dependency_set: set[tuple[str, BaseTaskDependency]] = None,
        allocated_team_id_set: set[str] = None,
        allocated_workplace_id_set: set[str] = None,
        parent_workflow_id: str = None,
        workplace_priority_rule: WorkplacePriorityRuleMode = WorkplacePriorityRuleMode.FSS,
        worker_priority_rule: ResourcePriorityRuleMode = ResourcePriorityRuleMode.MW,
        facility_priority_rule: ResourcePriorityRuleMode = ResourcePriorityRuleMode.SSP,
        need_facility: bool = False,
        target_component_id: str = None,
        default_progress: float = 0.0,
        due_time: int = int(-1),
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
        self.input_task_id_dependency_set = (
            input_task_id_dependency_set
            if input_task_id_dependency_set is not None
            else set()
        )
        self.allocated_team_id_set = (
            allocated_team_id_set if allocated_team_id_set is not None else set()
        )
        self.allocated_workplace_id_set = (
            allocated_workplace_id_set
            if allocated_workplace_id_set is not None
            else set()
        )
        self.parent_workflow_id = (
            parent_workflow_id if parent_workflow_id is not None else None
        )
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
        self.target_component_id = (
            target_component_id if target_component_id is not None else None
        )
        self.default_progress = (
            default_progress if default_progress is not None else 0.0
        )
        self.due_time = due_time or int(-1)
        self.auto_task = auto_task if auto_task is not False else False
        self.fixing_allocating_worker_id_set = fixing_allocating_worker_id_set or None
        self.fixing_allocating_facility_id_set = (
            fixing_allocating_facility_id_set or None
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
        self.remaining_work_amount_record_list = remaining_work_amount_record_list or []
        self.state = state or BaseTaskState.NONE
        self.state_record_list = state_record_list or []
        self.allocated_worker_facility_id_tuple_set = (
            frozenset(allocated_worker_facility_id_tuple_set)
            if allocated_worker_facility_id_tuple_set is not None
            else frozenset()
        )
        self.allocated_worker_facility_id_tuple_set_record_list = (
            allocated_worker_facility_id_tuple_set_record_list or []
        )
        self._absence_state_record_attr_name = "state_record_list"
        self._absence_aux_record_attr_names = [
            "remaining_work_amount_record_list",
            "allocated_worker_facility_id_tuple_set_record_list",
        ]
        self._absence_initial_state_value = BaseTaskState.NONE
        self._absence_state_working_value = BaseTaskState.WORKING
        self._absence_state_ready_value = BaseTaskState.READY
        self._absence_state_finished_value = BaseTaskState.FINISHED
        self._absence_state_none_value = BaseTaskState.NONE
        # --
        # Advanced parameter for customized simulation
        self.additional_work_amount = additional_work_amount or 0.0
        # --
        # Advanced variables for customized simulation
        self.additional_task_flag = additional_task_flag or False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )

    def __str__(self):
        """Return the name of BaseTask.

        Returns:
            str: Name of BaseTask.
        """
        return f"{self.name}"

    def _get_export_dict_extra_fields(self) -> dict:
        return {
            "default_work_amount": float(self.default_work_amount),
            "work_amount_progress_of_unit_step_time": self.work_amount_progress_of_unit_step_time,
            "input_task_id_dependency_set": [
                [task_id, int(dependency)]
                for (task_id, dependency) in self.input_task_id_dependency_set
            ],
            "allocated_team_id_set": list(self.allocated_team_id_set),
            "allocated_workplace_id_set": list(self.allocated_workplace_id_set),
            "need_facility": self.need_facility,
            "target_component_id": (
                self.target_component_id
                if self.target_component_id is not None
                else None
            ),
            "default_progress": self.default_progress,
            "due_time": self.due_time,
            "auto_task": self.auto_task,
            "fixing_allocating_worker_id_set": (
                list(self.fixing_allocating_worker_id_set)
                if self.fixing_allocating_worker_id_set is not None
                else None
            ),
            "fixing_allocating_facility_id_set": (
                list(self.fixing_allocating_facility_id_set)
                if self.fixing_allocating_facility_id_set is not None
                else None
            ),
            "est": float(self.est),
            "eft": float(self.eft),
            "lst": float(self.lst),
            "lft": float(self.lft),
            "remaining_work_amount": float(self.remaining_work_amount),
            "remaining_work_amount_record_list": [
                float(rwa) for rwa in self.remaining_work_amount_record_list
            ],
            "state": int(self.state),
            "state_record_list": [int(state) for state in self.state_record_list],
            "allocated_worker_facility_id_tuple_set": [
                [worker_id, facility_id]
                for (
                    worker_id,
                    facility_id,
                ) in self.allocated_worker_facility_id_tuple_set
            ],
            "allocated_worker_facility_id_tuple_set_record_list": [
                [
                    [worker_id, facility_id]
                    for (
                        worker_id,
                        facility_id,
                    ) in allocated_worker_facility_id_tuple_set
                ]
                for allocated_worker_facility_id_tuple_set in self.allocated_worker_facility_id_tuple_set_record_list
            ],
        }

    def _get_read_json_field_specs(self):
        return [
            "default_work_amount",
            "work_amount_progress_of_unit_step_time",
            (
                "input_task_id_dependency_set",
                lambda values: set(
                    (task_id, BaseTaskDependency(dependency))
                    for task_id, dependency in values
                ),
            ),
            ("allocated_team_id_set", set),
            ("allocated_workplace_id_set", set),
            "need_facility",
            "target_component_id",
            "default_progress",
            "due_time",
            "auto_task",
            (
                "fixing_allocating_worker_id_set",
                lambda value: set(value) if value is not None else None,
            ),
            (
                "fixing_allocating_facility_id_set",
                lambda value: set(value) if value is not None else None,
            ),
            "est",
            "eft",
            "lst",
            "lft",
            "remaining_work_amount",
            "remaining_work_amount_record_list",
            ("state", BaseTaskState),
            (
                "state_record_list",
                lambda values: [BaseTaskState(num) for num in values],
            ),
            (
                "allocated_worker_facility_id_tuple_set",
                lambda values: frozenset(tuple(pair) for pair in values),
            ),
            (
                "allocated_worker_facility_id_tuple_set_record_list",
                lambda values: [
                    [tuple(pair) for pair in allocated]
                    if allocated is not None
                    else None
                    for allocated in values
                ],
            ),
        ]

    def add_target_component(self, target_component: BaseComponent):
        """
        Add target component to this task.

        Args:
            target_component (BaseComponent): Target BaseComponent.
        """
        self.target_component_id = target_component.ID
        target_component.targeted_task_id_set.add(self.ID)

    def append_input_task_dependency(
        self,
        input_task: BaseTask,
        task_dependency_mode: BaseTaskDependency = BaseTaskDependency.FS,
    ):
        """
        Append input task to `input_task_id_dependency_set`.

        .. deprecated:: Use add_input_task instead.

        Args:
            input_task (BaseTask): Input BaseTask.
            task_dependency_mode (BaseTaskDependency, optional): Task Dependency mode between input_task to this task. Default to BaseTaskDependency.FS.
        """
        warnings.warn(
            "append_input_task_dependency is deprecated, use add_input_task instead.",
            DeprecationWarning,
        )
        self.input_task_id_dependency_set.add((input_task.ID, task_dependency_mode))

    def extend_input_task_list(
        self,
        input_task_list: list[BaseTask],
        input_task_dependency_mode: BaseTaskDependency = BaseTaskDependency.FS,
    ):
        """
        Extend the set of input tasks and FS dependency to `input_task_id_dependency_set`.

        .. deprecated:: Use update_input_task_set instead.

        Args:
            input_task_id_dependency_set (set(tuple(str, BaseTask))): Set of input BaseTask and type of dependency(FS, SS, SF, F/F).
        """
        warnings.warn(
            "extend_input_task_list is deprecated, use update_input_task_set instead.",
            DeprecationWarning,
        )
        for input_task in input_task_list:
            self.input_task_id_dependency_set.add(
                (input_task.ID, input_task_dependency_mode)
            )

    def add_input_task(
        self,
        input_task: BaseTask,
        task_dependency_mode: BaseTaskDependency = BaseTaskDependency.FS,
    ):
        """
        Add input task to `input_task_id_dependency_set`.

        Args:
            input_task (BaseTask): Input BaseTask.
            task_dependency_mode (BaseTaskDependency, optional): Task Dependency mode between input_task to this task. Default to BaseTaskDependency.FS.
        """
        self.input_task_id_dependency_set.add((input_task.ID, task_dependency_mode))

    def update_input_task_set(
        self,
        input_task_set: set[BaseTask],
        input_task_dependency_mode: BaseTaskDependency = BaseTaskDependency.FS,
    ):
        """
        Update the set of input tasks and FS dependency to `input_task_id_dependency_set`.

        Args:
            input_task_id_dependency_set (set(tuple(str, BaseTask))): Set of input BaseTask and type of dependency(FS, SS, SF, F/F).
        """
        for input_task in input_task_set:
            self.add_input_task(input_task, input_task_dependency_mode)

    def initialize(
        self, error_tol: float = 1e-10, state_info: bool = True, log_info: bool = True
    ):
        """
        Initialize the changeable variables of BaseTask.

        If `state_info` is True, the following attributes are initialized:
            - `est`
            - `eft`
            - `lst`
            - `lft`
            - `remaining_work_amount`
            - `state`
            - `allocated_worker_facility_id_tuple_set`
            - `additional_task_flag`
            - `actual_work_amount`

        If `log_info` is True, the following attributes are initialized:
            - `remaining_work_amount_record_list`
            - `state_record_list`
            - `allocated_worker_facility_id_tuple_set_record_list`

        Args:
            error_tol (float, optional): Error toleration of work amount for checking the state of this task. Defaults to 1e-10.
            state_info (bool, optional): Whether to initialize state information. Defaults to True.
            log_info (bool, optional): Whether to initialize log information. Defaults to True.
        """
        super().initialize(state_info=state_info, log_info=log_info)
        if state_info and log_info:
            if self.default_progress >= (1.00 - error_tol):
                self.state = BaseTaskState.FINISHED

    def _initialize_state_info(self) -> None:
        self.est = 0.0  # Earliest start time
        self.eft = 0.0  # Earliest finish time
        self.lst = -1.0  # Latest start time
        self.lft = -1.0  # Latest finish time
        self.remaining_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )
        self.state = BaseTaskState.NONE
        self.allocated_worker_facility_id_tuple_set = frozenset()
        self.additional_task_flag = False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )

    def _initialize_log_info(self) -> None:
        self.remaining_work_amount_record_list = []
        self.state_record_list = []
        self.allocated_worker_facility_id_tuple_set_record_list = []

    def set_alloc_pairs(self, pairs_iterable):
        """
        Set allocated pairs (non-destructive).
        """
        self.allocated_worker_facility_id_tuple_set = frozenset(pairs_iterable)

    def add_alloc_pair(self, pair: tuple[str, str]):
        """
        Add one allocated pair (non-destructive).
        """
        cur = self.allocated_worker_facility_id_tuple_set
        if pair in cur:
            return
        self.allocated_worker_facility_id_tuple_set = frozenset((*cur, pair))

    def remove_alloc_pair(self, pair: tuple[str, str]):
        """Remove one allocated pair (non-destructive)."""
        cur = self.allocated_worker_facility_id_tuple_set
        if pair not in cur:
            return
        self.allocated_worker_facility_id_tuple_set = frozenset(
            x for x in cur if x != pair
        )

    def update_alloc_pairs(self, add=(), remove=()):
        """
        Update allocated pairs (non-destructive).
        """
        cur = self.allocated_worker_facility_id_tuple_set
        if not add and not remove:
            return
        # Create a mutable set from the current frozenset
        s = set(cur)
        if remove:
            s.difference_update(remove)
        if add:
            s.update(add)
        self.allocated_worker_facility_id_tuple_set = frozenset(s)

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.remaining_work_amount_record_list.reverse()
        self.state_record_list.reverse()
        self.allocated_worker_facility_id_tuple_set_record_list.reverse()

    def get_state_from_record(self, time: int):
        """
        Get the state information in time.

        Args:
            time (int): Target simulation time.

        Returns:
            BaseTaskState: Task State information.
        """
        return self.state_record_list[time]

    def _get_absence_aux_initial_value(self, attr_name: str):
        if attr_name == "remaining_work_amount_record_list":
            return self.default_work_amount * (1.0 - self.default_progress)
        return None

    def _get_log_extra_fields(self, target_step_time: int) -> list:
        """Return class-specific log fields."""
        return [
            self.default_work_amount,
            max(self.remaining_work_amount_record_list[target_step_time], 0.0),
            self.allocated_worker_facility_id_tuple_set_record_list[target_step_time],
        ]

    def get_time_list_for_gantt_chart(self, finish_margin: float = 1.0):
        """
        Get ready/working time_list for drawing Gantt chart.

        Args:
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.

        Returns:
            Tuple[List[tuple(int, int)], List[tuple(int, int)]]:
                - ready_time_list including start_time, length
                - working_time_list including start_time, length
        """
        state_to_bucket = {
            BaseTaskState.READY: "ready",
            BaseTaskState.WORKING: "working",
        }
        time_lists = build_time_lists_from_state_record(
            self.state_record_list,
            state_to_bucket=state_to_bucket,
            finish_margin=finish_margin,
            buckets=["ready", "working"],
            include_empty=True,
        )
        return time_lists["ready"], time_lists["working"]

    def get_mermaid_diagram(
        self,
        shape: str = "rect",
        subgraph: bool = False,
        subgraph_name: str = "Task",
        subgraph_direction: str = "LR",
        print_extra_info: bool = True,
    ):
        """
        Get mermaid diagram of this task.

        Args:
            shape (str, optional): Shape of mermaid diagram. Defaults to "rect".
            subgraph (bool, optional): Subgraph or not. Defaults to False.
            subgraph_name (str, optional): Subgraph name. Defaults to "Task".
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
            print_extra_info (bool, optional): Print extra information or not. Defaults to True.
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        return super().get_mermaid_diagram(
            shape=shape,
            subgraph=subgraph,
            subgraph_name=subgraph_name,
            subgraph_direction=subgraph_direction,
            print_extra_info=print_extra_info,
        )

    def _get_mermaid_label(self, print_extra_info: bool = False, **kwargs) -> str:
        label = self.name
        if print_extra_info:
            label += f"<br>{self.remaining_work_amount}"
        return label

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        shape: str = "rect",
        subgraph: bool = False,
        subgraph_name: str = "Task",
        subgraph_direction: str = "LR",
        print_extra_info: bool = True,
    ):
        """
        Print mermaid diagram of this task.

        Args:
            orientations (str, optional): Orientation of mermaid diagram. Defaults to "LR".
            shape (str, optional): Shape of mermaid diagram. Defaults to "rect".
            subgraph (bool, optional): Subgraph or not. Defaults to False.
            subgraph_name (str, optional): Subgraph name. Defaults to "Task".
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
            print_extra_info (bool, optional): Print extra information or not. Defaults to True.
        """
        super().print_mermaid_diagram(
            orientations=orientations,
            shape=shape,
            subgraph=subgraph,
            subgraph_name=subgraph_name,
            subgraph_direction=subgraph_direction,
            print_extra_info=print_extra_info,
        )

    def get_gantt_mermaid_steps_data(
        self,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
        view_ready: bool = False,
    ):
        """
        Get gantt mermaid steps data of this task.

        Args:
            range_time (tuple[int, int], optional): Range of gantt chart. Defaults to (0, sys.maxsize).
            detailed_info (bool, optional): If True, print detailed information. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary to map ID to name. Defaults to None.
            view_ready (bool, optional): If True, include ready time in Gantt chart. Defaults to False.

        Returns:
            list[str]: List of lines for gantt mermaid steps diagram.
        """
        ready_time_list, working_time_list = self.get_time_list_for_gantt_chart()

        def get_combined_name_list(clipped_start: int) -> list[str]:
            if (
                detailed_info is True
                and id_name_dict is not None
                and self.ID in id_name_dict
                and clipped_start
                < len(self.allocated_worker_facility_id_tuple_set_record_list)
            ):
                worker_facility_tuple_list = (
                    self.allocated_worker_facility_id_tuple_set_record_list[
                        clipped_start
                    ]
                )
                if worker_facility_tuple_list is None:
                    worker_facility_tuple_list = ()
                worker_id_list = [
                    worker_id
                    for worker_id, _ in worker_facility_tuple_list
                    if worker_id is not None
                ]
                worker_name_list = [
                    id_name_dict.get(worker_id, worker_id)
                    for worker_id in worker_id_list
                ]
                facility_id_list = [
                    facility_id
                    for _, facility_id in worker_facility_tuple_list
                    if facility_id is not None
                ]
                facility_name_list = [
                    id_name_dict.get(facility_id, facility_id)
                    for facility_id in facility_id_list
                ]

                combined_name_list = []
                max_length = max(len(worker_name_list), len(facility_name_list))
                for i in range(max_length):
                    worker_name = (
                        worker_name_list[i] if i < len(worker_name_list) else ""
                    )
                    facility_name = (
                        facility_name_list[i] if i < len(facility_name_list) else ""
                    )

                    if worker_name and facility_name:
                        combined_name_list.append(f"{worker_name}-{facility_name}")
                    elif worker_name:
                        combined_name_list.append(worker_name)
                    elif facility_name:
                        combined_name_list.append(facility_name)

                return combined_name_list
            return []

        def ready_text_builder(clipped_start: int) -> str:
            text = self.name + "[READY]"
            combined_name_list = get_combined_name_list(clipped_start)
            if combined_name_list:
                text = f"{self.name} * {'&'.join(combined_name_list)} [READY]"
            return text

        def work_text_builder(clipped_start: int) -> str:
            text = self.name
            combined_name_list = get_combined_name_list(clipped_start)
            if combined_name_list:
                text = f"{self.name} * {'&'.join(combined_name_list)}"
            return text

        return build_gantt_mermaid_steps_lines(
            ready_time_list=ready_time_list,
            working_time_list=working_time_list,
            range_time=range_time,
            view_ready=view_ready,
            ready_text_builder=ready_text_builder,
            work_text_builder=work_text_builder,
        )
