#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_facility.

This module defines the BaseFacility class and related enums for expressing a workplace.
"""

import abc
import uuid
from enum import IntEnum

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


class BaseFacilityState(IntEnum):
    """BaseFacilityState.

    Enum for representing the state of a facility.

    Attributes:
        FREE (int): Facility is free.
        WORKING (int): Facility is working.
        ABSENCE (int): Facility is absent.
    """

    FREE = 0
    WORKING = 1
    ABSENCE = -1


class BaseFacility(
    SingleNodeMermaidDiagramMixin,
    AssignedPairsMixin,
    WorkerFacilityCommonMixin,
    object,
    metaclass=abc.ABCMeta,
):
    _state_free_value = BaseFacilityState.FREE
    _state_working_value = BaseFacilityState.WORKING
    _state_absence_value = BaseFacilityState.ABSENCE
    _assigned_record_attr_name = "assigned_task_worker_id_tuple_set_record_list"
    """BaseFacility.

    BaseFacility class for expressing a workplace. This class will be used as a template.

    Args:
        name (str, optional): Name of this facility. Defaults to None -> "New Facility".
        ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
        workplace_id (str, optional): ID of Workplace which this facility belongs to. Defaults to None.
        cost_per_time (float, optional): Cost of this facility per unit time. Defaults to 0.0.
        solo_working (bool, optional): Flag whether this facility can work any task with other facilities or not. Defaults to False.
        workamount_skill_mean_map (Dict[str, float], optional): Mean skill for expressing progress in unit time. Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional): Standard deviation of skill for expressing progress in unit time. Defaults to {}.
        absence_time_list (List[int], optional): List of absence time of simulation. Defaults to None -> [].
        state (BaseFacilityState, optional): State of this facility in simulation. Defaults to BaseFacilityState.FREE.
        state_record_list (List[BaseFacilityState], optional): Record list of state. Defaults to None -> [].
        cost_record_list (List[float], optional): History or record of cost in simulation. Defaults to None -> [].
        assigned_task_worker_id_tuple_set (set(tuple(str, str)), optional): State of assigned tasks id in simulation. Defaults to None -> set().
        assigned_task_worker_id_tuple_set_record_list (List[set(tuple(str, str))], optional): Record of assigned tasks' id in simulation. Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        workplace_id: str = None,
        cost_per_time: float = 0.0,
        solo_working: bool = False,
        workamount_skill_mean_map: dict = None,
        workamount_skill_sd_map: dict = None,
        absence_time_list: list[int] = None,
        # Basic variables
        state: BaseFacilityState = BaseFacilityState.FREE,
        state_record_list: list[BaseFacilityState] = None,
        cost_record_list: list[float] = None,
        assigned_task_worker_id_tuple_set: set[tuple[str, str]] = None,
        assigned_task_worker_id_tuple_set_record_list: list[
            set[tuple[str, str]]
        ] = None,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Facility"
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.workplace_id = workplace_id
        self.cost_per_time = cost_per_time
        self.solo_working = solo_working
        self.workamount_skill_mean_map = workamount_skill_mean_map or {}
        self.workamount_skill_sd_map = workamount_skill_sd_map or {}
        self.absence_time_list = absence_time_list or []
        # ----
        # Changeable variables on simulation
        # --
        # Basic variables
        self.state = state or BaseFacilityState.FREE
        self.state_record_list = state_record_list or []
        self.cost_record_list = cost_record_list or []
        self.assigned_task_worker_id_tuple_set = (
            frozenset(assigned_task_worker_id_tuple_set)
            if assigned_task_worker_id_tuple_set is not None
            else frozenset()
        )
        self.assigned_task_worker_id_tuple_set_record_list = (
            assigned_task_worker_id_tuple_set_record_list or []
        )
        self._assigned_pairs_attr_name = "assigned_task_worker_id_tuple_set"

    def export_dict_json_data(self):
        """
        Export the information of this facility to JSON data.

        Returns:
            dict: JSON format data.
        """
        return build_json_base_dict(
            self,
            workplace_id=self.workplace_id if self.workplace_id is not None else None,
            cost_per_time=self.cost_per_time,
            solo_working=self.solo_working,
            workamount_skill_mean_map=self.workamount_skill_mean_map,
            workamount_skill_sd_map=self.workamount_skill_sd_map,
            absence_time_list=self.absence_time_list,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            cost_record_list=self.cost_record_list,
            assigned_task_worker_id_tuple_set=list(
                self.assigned_task_worker_id_tuple_set
            ),
            assigned_task_worker_id_tuple_set_record_list=[
                list(rec) if isinstance(rec, (set, frozenset)) else rec
                for rec in self.assigned_task_worker_id_tuple_set_record_list
            ],
        )

    def _get_log_extra_fields(self, target_step_time: int) -> list:
        """Return class-specific log fields."""
        return [
            self.assigned_task_worker_id_tuple_set_record_list[target_step_time]
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

    def get_mermaid_diagram(
        self,
        shape: str = "stadium",
        subgraph: bool = False,
        subgraph_name: str = "Facility",
        subgraph_direction: str = "LR",
        print_extra_info: bool = False,
    ):
        """
        Get mermaid diagram of this facility.

        Args:
            shape (str, optional): Shape of this facility. Defaults to "stadium".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to False.
            subgraph_name (str, optional): Name of subgraph. Defaults to "Facility".
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
        subgraph_name: str = "Facility",
        subgraph_direction: str = "LR",
        print_extra_info: bool = False,
    ):
        """
        Print mermaid diagram of this facility.

        Args:
            orientations (str, optional): Orientation of mermaid diagram. Defaults to "LR".
            shape (str, optional): Shape of mermaid diagram. Defaults to "stadium".
            subgraph (bool, optional): Subgraph or not. Defaults to False.
            subgraph_name (str, optional): Subgraph name. Defaults to "Facility".
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
        range_time: tuple[int, int] = (0, float("inf")),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get gantt mermaid steps data of this facility.

        Args:
            range_time (tuple[int, int], optional): Range time of gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): If True, detailed information is included in gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for detailed information. Defaults to None.

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
                < len(self.assigned_task_worker_id_tuple_set_record_list)
            ):
                task_id_list = self.assigned_task_worker_id_tuple_set_record_list[
                    clipped_start
                ]
                if task_id_list is None:
                    task_id_list = []
                task_name_list = [
                    (
                        id_name_dict.get(task_id, task_id)
                        if isinstance(task_id, str)
                        else str(task_id)
                    )
                    for task_id in task_id_list
                    if task_id is not None
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
