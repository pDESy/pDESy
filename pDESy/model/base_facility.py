#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_facility.

This module defines the BaseFacility class and related enums for expressing a workplace.
"""

import abc
import uuid
from enum import IntEnum


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


class BaseFacility(object, metaclass=abc.ABCMeta):
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

    def __str__(self):
        """Return the name of BaseFacility.

        Returns:
            str: Name of BaseFacility.
        """
        return self.name

    def export_dict_json_data(self):
        """
        Export the information of this facility to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {
            "type": self.__class__.__name__,
            "name": self.name,
            "ID": self.ID,
            "workplace_id": (
                self.workplace_id if self.workplace_id is not None else None
            ),
            "cost_per_time": self.cost_per_time,
            "solo_working": self.solo_working,
            "workamount_skill_mean_map": self.workamount_skill_mean_map,
            "workamount_skill_sd_map": self.workamount_skill_sd_map,
            "absence_time_list": self.absence_time_list,
            "state": int(self.state),
            "state_record_list": [int(state) for state in self.state_record_list],
            "cost_record_list": self.cost_record_list,
            "assigned_task_worker_id_tuple_set": list(
                self.assigned_task_worker_id_tuple_set
            ),
            "assigned_task_worker_id_tuple_set_record_list": [
                list(rec) if isinstance(rec, (set, frozenset)) else rec
                for rec in self.assigned_task_worker_id_tuple_set_record_list
            ],
        }
        return dict_json_data

    def initialize(self, state_info: bool = True, log_info: bool = True):
        """
        Initialize the changeable variables of BaseFacility.

        If `state_info` is True, the following attributes are initialized:
            - `state`
            - `assigned_task_worker_id_tuple_set`

        If `log_info` is True, the following attributes are initialized:
            - `state_record_list`
            - `cost_record_list`
            - `assigned_task_worker_id_tuple_set_record_list`

        Args:
            state_info (bool, optional): Whether to initialize state information. Defaults to True.
            log_info (bool, optional): Whether to initialize log information. Defaults to True.
        """
        if state_info:
            self.state = BaseFacilityState.FREE
            self.assigned_task_worker_id_tuple_set = frozenset()

        if log_info:
            self.state_record_list = []
            self.cost_record_list = []
            self.assigned_task_worker_id_tuple_set_record_list = []

    def reverse_log_information(self):
        """Reverse log information of all records."""
        self.state_record_list.reverse()
        self.cost_record_list.reverse()
        self.assigned_task_worker_id_tuple_set_record_list.reverse()

    def record_assigned_task_id(self):
        """Record assigned task id to 'assigned_task_worker_id_tuple_set_record_list'."""
        self.assigned_task_worker_id_tuple_set_record_list.append(
            self.assigned_task_worker_id_tuple_set
        )

    def record_state(self, working: bool = True):
        """Record current 'state' in 'state_record_list'.

        Args:
            working (bool, optional): Whether to record the current state as working. Defaults to True.
        """
        if working:
            self.state_record_list.append(self.state)
        else:
            # if self.state == BaseFacilityState.WORKING:
            #     self.state_record_list.append(BaseFacilityState.FREE)
            # else:
            #     self.state_record_list.append(self.state)
            self.state_record_list.append(BaseFacilityState.ABSENCE)

    def set_assigned_pairs(self, pairs_iterable):
        """
        Set assigned pairs (non-destructive).
        """
        self.assigned_task_worker_id_tuple_set = frozenset(pairs_iterable)

    def add_assigned_pair(self, pair: tuple[str, str]):
        """
        Add one assigned pair (non-destructive).
        """
        cur = self.assigned_task_worker_id_tuple_set
        if pair in cur:
            return
        self.assigned_task_worker_id_tuple_set = frozenset((*cur, pair))

    def remove_assigned_pair(self, pair: tuple[str, str]):
        """
        Remove one assigned pair (non-destructive).
        """
        cur = self.assigned_task_worker_id_tuple_set
        if pair not in cur:
            return
        self.assigned_task_worker_id_tuple_set = frozenset(x for x in cur if x != pair)

    def update_assigned_pairs(self, add=(), remove=()):
        """
        Update assigned pairs (non-destructive).
        """
        cur = self.assigned_task_worker_id_tuple_set
        if not add and not remove:
            return
        s = set(cur)
        if remove:
            s.difference_update(remove)
        if add:
            s.update(add)
        self.assigned_task_worker_id_tuple_set = frozenset(s)

    def remove_absence_time_list(self, absence_time_list: list[int]):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]): List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.state_record_list):
                self.assigned_task_worker_id_tuple_set_record_list.pop(step_time)
                self.cost_record_list.pop(step_time)
                self.state_record_list.pop(step_time)

    def insert_absence_time_list(self, absence_time_list: list[int]):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]): List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list):
            if step_time < len(self.state_record_list):
                if step_time == 0:
                    self.assigned_task_worker_id_tuple_set_record_list.insert(
                        step_time, None
                    )
                    self.cost_record_list.insert(step_time, 0.0)
                    self.state_record_list.insert(step_time, BaseFacilityState.FREE)
                else:
                    self.assigned_task_worker_id_tuple_set_record_list.insert(
                        step_time,
                        self.assigned_task_worker_id_tuple_set_record_list[
                            step_time - 1
                        ],
                    )
                    self.cost_record_list.insert(step_time, 0.0)
                    self.state_record_list.insert(step_time, BaseFacilityState.FREE)

    def print_log(self, target_step_time: int):
        """
        Print log in `target_step_time`.

        Prints:
            - ID
            - name
            - state_record_list[target_step_time]
            - assigned_task_worker_id_tuple_set_record_list[target_step_time]

        Args:
            target_step_time (int): Target step time of printing log.
        """
        print(
            self.ID,
            self.name,
            self.state_record_list[target_step_time],
            self.assigned_task_worker_id_tuple_set_record_list[target_step_time],
        )

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """
        Print all log in chronological order.

        Args:
            backward (bool, optional): If True, print logs in reverse order. Defaults to False.
        """
        for t in range(len(self.state_record_list)):
            print("TIME: ", t)
            if backward:
                t = len(self.state_record_list) - 1 - t
            self.print_log(t)

    def check_update_state_from_absence_time_list(self, step_time: int):
        """
        Check and update state of all resources to ABSENCE, FREE, or WORKING.

        Args:
            step_time (int): Target step time of checking and updating state of workers and facilities.
        """
        if step_time in self.absence_time_list:
            self.state = BaseFacilityState.ABSENCE
            return
        assigned = self.assigned_task_worker_id_tuple_set
        self.state = (
            BaseFacilityState.FREE if not assigned else BaseFacilityState.WORKING
        )

    def get_time_list_for_gantt_chart(self, finish_margin: float = 1.0):
        """
        Get ready/working/absence time_list for drawing Gantt chart.

        Args:
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.

        Returns:
            Tuple[List[tuple(int, int)], List[tuple(int, int)], List[tuple(int, int)]]:
                - ready_time_list including start_time, length
                - working_time_list including start_time, length
                - absence_time_list including start_time, length
        """
        ready_time_list = []
        working_time_list = []
        absence_time_list = []
        previous_state = None
        from_time = -1
        to_time = -1
        time = -1  # Initialize before loop
        for time, state in enumerate(self.state_record_list):
            if state != previous_state:
                if from_time == -1:
                    from_time = time
                elif to_time == -1:
                    to_time = time
                    if state == BaseFacilityState.FREE:
                        if previous_state == BaseFacilityState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseFacilityState.ABSENCE:
                            absence_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseFacilityState.WORKING:
                        if previous_state == BaseFacilityState.FREE:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseFacilityState.ABSENCE:
                            absence_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseFacilityState.ABSENCE:
                        if previous_state == BaseFacilityState.FREE:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseFacilityState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    from_time = time
                    to_time = -1
            previous_state = state

        # Suspended because of max time limitation
        if from_time > -1 and to_time == -1:
            if previous_state == BaseFacilityState.WORKING:
                working_time_list.append((from_time, time - from_time + finish_margin))
            elif previous_state == BaseFacilityState.FREE:
                ready_time_list.append((from_time, time - from_time + finish_margin))
            elif previous_state == BaseFacilityState.ABSENCE:
                absence_time_list.append((from_time, time - from_time + finish_margin))

        return ready_time_list, working_time_list, absence_time_list

    def has_workamount_skill(self, task_name: str, error_tol: float = 1e-10):
        """
        Check whether this facility has workamount skill for a given task.

        Args:
            task_name (str): Task name.
            error_tol (float, optional): Measures against numerical error. Defaults to 1e-10.

        Returns:
            bool: Whether this facility has workamount skill of task_name or not.
        """
        if task_name in self.workamount_skill_mean_map:
            if self.workamount_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False

    def get_mermaid_diagram(
        self,
        shape: str = "stadium",
        subgraph: bool = False,
        subgraph_name: str = "Facility",
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this facility.

        Args:
            shape (str, optional): Shape of this facility. Defaults to "stadium".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to False.
            subgraph_name (str, optional): Name of subgraph. Defaults to "Facility".
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {subgraph_name}")
            list_of_lines.append(f"direction {subgraph_direction}")
        list_of_lines.append(f"{self.ID}@{{shape: {shape}, label: '{self.name}'}}")

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        shape: str = "stadium",
        subgraph: bool = False,
        subgraph_name: str = "Facility",
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this facility.

        Args:
            orientations (str, optional): Orientation of mermaid diagram. Defaults to "LR".
            shape (str, optional): Shape of mermaid diagram. Defaults to "stadium".
            subgraph (bool, optional): Subgraph or not. Defaults to False.
            subgraph_name (str, optional): Subgraph name. Defaults to "Facility".
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_mermaid_diagram(
            shape=shape,
            subgraph=subgraph,
            subgraph_name=subgraph_name,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def get_gantt_mermaid_data(
        self,
        range_time: tuple[int, int] = (0, float("inf")),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get gantt mermaid data of this facility.

        Args:
            range_time (tuple[int, int], optional): Range time of gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): If True, detailed information is included in gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for detailed information. Defaults to None.

        Returns:
            list[str]: List of lines for gantt mermaid diagram.
        """
        list_of_lines = []
        ready_time_list, working_time_list = self.get_time_list_for_gantt_chart()[0:2]
        if view_ready:
            for start, duration in ready_time_list:
                end = start + duration - 1
                if end < range_time[0] or start > range_time[1]:
                    continue
                clipped_start = max(start, range_time[0])
                clipped_end = min(end + 1, range_time[1])
                if clipped_end == float("inf"):
                    clipped_end = end + 1
                text = self.name + "[READY]"
                if (
                    detailed_info is True
                    and id_name_dict is not None
                    and self.ID in id_name_dict
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
                    if task_name_list:
                        text = f"{self.name} * {'\u0026'.join(task_name_list)} [READY]"

                list_of_lines.append(f"{text}:{int(clipped_start)},{int(clipped_end)}")

        for start, duration in working_time_list:
            end = start + duration - 1
            if end < range_time[0] or start > range_time[1]:
                continue
            clipped_start = max(start, range_time[0])
            clipped_end = min(end + 1, range_time[1])
            if clipped_end == float("inf"):
                clipped_end = end + 1
            text = self.name
            if (
                detailed_info is True
                and id_name_dict is not None
                and self.ID in id_name_dict
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
                if task_name_list:
                    text = f"{self.name} * {'\u0026'.join(task_name_list)}"

            list_of_lines.append(f"{text}:{int(clipped_start)},{int(clipped_end)}")
        return list_of_lines
