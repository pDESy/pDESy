#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_worker."""

import abc
import sys
import uuid
from enum import IntEnum

import numpy as np

from pDESy.model.mermaid_utils import (
    SingleNodeMermaidDiagramMixin,
    build_gantt_mermaid_steps_lines,
)
from pDESy.model.pdesy_utils import (
    AssignedPairsMixin,
    WorkerFacilityCommonMixin,
    build_json_base_dict,
    print_basic_log_fields,
    print_all_log_in_chronological_order,
)


class BaseWorkerState(IntEnum):
    """BaseWorkerState.

    Enum for representing the state of a worker.

    Attributes:
        FREE (int): Worker is free.
        WORKING (int): Worker is working.
        ABSENCE (int): Worker is absent.
    """

    FREE = 0
    WORKING = 1
    ABSENCE = -1


class BaseWorker(
    SingleNodeMermaidDiagramMixin,
    AssignedPairsMixin,
    WorkerFacilityCommonMixin,
    object,
    metaclass=abc.ABCMeta,
):
    _state_free_value = BaseWorkerState.FREE
    _state_working_value = BaseWorkerState.WORKING
    _state_absence_value = BaseWorkerState.ABSENCE
    _assigned_record_attr_name = "assigned_task_facility_id_tuple_set_record_list"
    """BaseWorker.

    BaseWorker class for expressing a worker. This class will be used as a template.

    Args:
        name (str, optional): Name of this worker. Defaults to None -> "New Worker".
        ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
        team_id (str, optional): Team ID. Defaults to None.
        main_workplace_id (str, optional): Main workplace ID. Defaults to None.
        cost_per_time (float, optional): Cost of this worker per unit time. Defaults to 0.0.
        solo_working (bool, optional): Flag whether this worker can work with other workers or not. Defaults to False.
        workamount_skill_mean_map (Dict[str, float], optional): Skill for expressing progress in unit time. Defaults to None -> {}.
        workamount_skill_sd_map (Dict[str, float], optional): Standard deviation of skill for expressing progress in unit time. Defaults to None -> {}.
        facility_skill_map (Dict[str, float], optional): Skill for operating facility in unit time. Defaults to None -> {}.
        absence_time_list (List[int], optional): List of absence time of simulation. Defaults to None -> [].
        state (BaseWorkerState, optional): State of this worker in simulation. Defaults to BaseWorkerState.FREE.
        state_record_list (List[BaseWorkerState], optional): Record list of state. Defaults to None -> [].
        cost_record_list (List[float], optional): History or record of cost in simulation. Defaults to None -> [].
        assigned_task_facility_id_tuple_set (set(tuple(str, str)), optional): State of assigned task and facility id tuple in simulation. Defaults to None -> set().
        assigned_task_facility_id_tuple_set_record_list (List[set(tuple(str, str))], optional): Record of assigned tasks' id in simulation. Defaults to None -> [].
        quality_skill_mean_map (Dict[str, float], optional): Skill for expressing quality in unit time. Defaults to None -> {}.
        quality_skill_sd_map (Dict[str, float], optional): Standard deviation of skill for expressing quality in unit time. Defaults to None -> {}.
    """

    def __init__(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        team_id: str = None,
        main_workplace_id: str = None,
        cost_per_time: float = 0.0,
        solo_working: bool = False,
        workamount_skill_mean_map: dict[str, float] = None,
        workamount_skill_sd_map: dict[str, float] = None,
        facility_skill_map: dict[str, float] = None,
        absence_time_list: list[int] = None,
        # Basic variables
        state: BaseWorkerState = BaseWorkerState.FREE,
        state_record_list: list[BaseWorkerState] = None,
        cost_record_list: list[float] = None,
        assigned_task_facility_id_tuple_set: set[tuple[str, str]] = None,
        assigned_task_facility_id_tuple_set_record_list: list[
            set[tuple[str, str]]
        ] = None,
        # Advanced parameters for customized simulation
        quality_skill_mean_map: dict[str, float] = None,
        quality_skill_sd_map: dict[str, float] = None,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Worker"
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.team_id = team_id
        self.main_workplace_id = main_workplace_id
        self.cost_per_time = cost_per_time
        self.solo_working = solo_working
        self.workamount_skill_mean_map = workamount_skill_mean_map or {}
        self.workamount_skill_sd_map = workamount_skill_sd_map or {}
        self.absence_time_list = absence_time_list or []
        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        self.state = state or BaseWorkerState.FREE
        self.state_record_list = state_record_list or []
        self.cost_record_list = cost_record_list or []
        self.assigned_task_facility_id_tuple_set = (
            frozenset(assigned_task_facility_id_tuple_set)
            if assigned_task_facility_id_tuple_set is not None
            else frozenset()
        )
        self.assigned_task_facility_id_tuple_set_record_list = (
            assigned_task_facility_id_tuple_set_record_list or []
        )
        self._assigned_pairs_attr_name = "assigned_task_facility_id_tuple_set"
        self.facility_skill_map = facility_skill_map or {}
        # --
        # Advanced parameter for customized simulation
        self.quality_skill_mean_map = quality_skill_mean_map or {}
        self.quality_skill_sd_map = quality_skill_sd_map or {}

    def has_facility_skill(self, facility_name: str, error_tol: float = 1e-10):
        """
        Check whether this worker has facility skill or not.

        By checking facility_skill_map.

        Args:
            facility_name (str): Facility name.
            error_tol (float, optional): Measures against numerical error. Defaults to 1e-10.

        Returns:
            bool: Whether this worker has facility skill of facility_name or not.
        """
        if facility_name in self.facility_skill_map:
            if self.facility_skill_map[facility_name] > 0.0 + error_tol:
                return True
        return False

    def has_quality_skill(self, task_name: str, error_tol: float = 1e-10):
        """
        Check whether this worker has quality skill or not.

        By checking quality_skill_mean_map.

        Args:
            task_name (str): Task name.
            error_tol (float, optional): Measures against numerical error. Defaults to 1e-10.

        Returns:
            bool: Whether this worker has quality skill of task_name or not.
        """
        if task_name in self.quality_skill_mean_map:
            if self.quality_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False

    def get_quality_skill_point(self, task_name: str, seed: int = None):
        """
        Get point of quality by this worker's contribution in this time.

        Args:
            task_name (str): Task name.
            seed (int, optional): Random seed for reproducibility. Defaults to None.

        Returns:
            float: Point of quality by this worker's contribution in this time.
        """
        if seed is not None:
            np.random.seed(seed=seed)
        if not self.has_quality_skill(task_name):
            return 0.0
        skill_mean = self.quality_skill_mean_map[task_name]

        if task_name not in self.quality_skill_sd_map:
            skill_sd = 0
        else:
            skill_sd = self.quality_skill_sd_map[task_name]
        base_quality = np.random.normal(skill_mean, skill_sd)
        return base_quality  # / float(sum_of_working_task_in_this_time)

    def _get_log_extra_fields(self, target_step_time: int) -> list:
        """Return class-specific log fields."""
        return [
            self.assigned_task_facility_id_tuple_set_record_list[target_step_time]
        ]

    def print_log(self, target_step_time: int):
        """Print log in `target_step_time`."""
        print_basic_log_fields(
            self.ID,
            self.name,
            self.state_record_list[target_step_time],
            *self._get_log_extra_fields(target_step_time),
        )

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """
        Print all log in chronological order.

        Args:
            backward (bool, optional): If True, print logs in reverse order. Defaults to False.
        """
        print_all_log_in_chronological_order(
            self.print_log, len(self.state_record_list), backward
        )

    def export_dict_json_data(self):
        """
        Export the information of this worker to JSON data.

        Returns:
            dict: JSON format data.
        """
        assigned_current = list(self.assigned_task_facility_id_tuple_set)
        assigned_history = []
        for rec in self.assigned_task_facility_id_tuple_set_record_list:
            if isinstance(rec, (set, frozenset)):
                assigned_history.append(list(rec))
            else:
                assigned_history.append(rec)

        return build_json_base_dict(
            self,
            team_id=self.team_id if self.team_id is not None else None,
            cost_per_time=self.cost_per_time,
            solo_working=self.solo_working,
            workamount_skill_mean_map=self.workamount_skill_mean_map,
            workamount_skill_sd_map=self.workamount_skill_sd_map,
            facility_skill_map=self.facility_skill_map,
            absence_time_list=self.absence_time_list,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            cost_record_list=self.cost_record_list,
            assigned_task_facility_id_tuple_set=assigned_current,
            assigned_task_facility_id_tuple_set_record_list=assigned_history,
        )

    def get_mermaid_diagram(
        self,
        shape: str = "stadium",
        subgraph: bool = False,
        subgraph_name: str = "Worker",
        subgraph_direction: str = "LR",
        print_extra_info: bool = False,
    ):
        """
        Get mermaid diagram of this worker.

        Args:
            shape (str, optional): Shape of this worker. Defaults to "stadium".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to False.
            subgraph_name (str, optional): Name of subgraph. Defaults to "Worker".
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
            print_extra_info (bool, optional): Print extra information or not. Defaults to False.
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
            label += ""
        return label

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        shape: str = "stadium",
        subgraph: bool = False,
        subgraph_name: str = "Worker",
        subgraph_direction: str = "LR",
        print_extra_info: bool = False,
    ):
        """
        Print mermaid diagram of this worker.

        Args:
            orientations (str, optional): Orientation of mermaid diagram. Defaults to "LR".
            shape (str, optional): Shape of mermaid diagram. Defaults to "stadium".
            subgraph (bool, optional): Subgraph or not. Defaults to False.
            subgraph_name (str, optional): Subgraph name. Defaults to "Worker".
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
            print_extra_info (bool, optional): Print extra information or not. Defaults to False.
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
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get gantt mermaid steps data of this worker.

        Args:
            range_time (tuple[int, int], optional): Range time of gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): Detailed information or not. Defaults to False.
            id_name_dict (dict[str, str], optional): ID to name dictionary. Defaults to None.

        Returns:
            list[str]: List of lines for gantt mermaid steps diagram.
        """
        ready_time_list, working_time_list = self.get_time_list_for_gantt_chart()[0:2]

        def get_task_name_list(clipped_start: int) -> list[str]:
            if (
                detailed_info is True
                and id_name_dict is not None
                and self.ID in id_name_dict
                and clipped_start
                < len(self.assigned_task_facility_id_tuple_set_record_list)
            ):
                task_id_list = self.assigned_task_facility_id_tuple_set_record_list[
                    clipped_start
                ]
                if task_id_list is None:
                    task_id_list = []
                task_name_list = [
                    id_name_dict.get(task_id, task_id)
                    for task_id in task_id_list
                    if task_id is not None
                ]
                task_name_list = [
                    str(task) if isinstance(task, tuple) else task
                    for task in task_name_list
                ]
                return task_name_list
            return []

        def ready_text_builder(clipped_start: int) -> str:
            text = self.name + "[READY]"
            task_name_list = get_task_name_list(clipped_start)
            if task_name_list:
                text = f"{self.name} * {'&'.join(task_name_list)} [READY]"
            return text

        def work_text_builder(clipped_start: int) -> str:
            text = self.name
            task_name_list = get_task_name_list(clipped_start)
            if task_name_list:
                text = f"{self.name} * {'&'.join(task_name_list)}"
            return text

        return build_gantt_mermaid_steps_lines(
            ready_time_list=ready_time_list,
            working_time_list=working_time_list,
            range_time=range_time,
            view_ready=view_ready,
            ready_text_builder=ready_text_builder,
            work_text_builder=work_text_builder,
        )
