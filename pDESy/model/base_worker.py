#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_worker."""

import abc
import sys
import uuid
from enum import IntEnum
import numpy as np


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


class BaseWorker(object, metaclass=abc.ABCMeta):
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

    def check_update_state_from_absence_time_list(self, step_time: int):
        """
        Check and update state of all resources to ABSENCE, FREE, or WORKING.

        Args:
            step_time (int): Target step time of checking and updating state of workers and facilities.
        """
        if step_time in self.absence_time_list:
            self.state = BaseWorkerState.ABSENCE
            return
        assigned = self.assigned_task_facility_id_tuple_set
        self.state = BaseWorkerState.FREE if not assigned else BaseWorkerState.WORKING

    def __str__(self):
        """Return the name of BaseResource.

        Returns:
            str: Name of BaseResource.
        """
        return f"{self.name}"

    def initialize(self, state_info: bool = True, log_info: bool = True):
        """
        Initialize the changeable variables of BaseResource.

        If `state_info` is True, the following attributes are initialized:
            - `state`
            - `assigned_task_facility_id_tuple_set`

        If `log_info` is True, the following attributes are initialized:
            - `state_record_list`
            - `cost_record_list`
            - `assigned_task_facility_id_tuple_set_record_list`

        Args:
            state_info (bool, optional): Whether to initialize state information. Defaults to True.
            log_info (bool, optional): Whether to initialize log information. Defaults to True.
        """
        if state_info:
            self.state = BaseWorkerState.FREE
            self.assigned_task_facility_id_tuple_set = frozenset()

        if log_info:
            self.state_record_list = []
            self.cost_record_list = []
            self.assigned_task_facility_id_tuple_set_record_list = []

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.state_record_list.reverse()
        self.cost_record_list.reverse()
        self.assigned_task_facility_id_tuple_set_record_list.reverse()

    def record_assigned_task_id(self):
        """Record assigned task id to `assigned_task_facility_id_tuple_set_record_list`."""
        self.assigned_task_facility_id_tuple_set_record_list.append(
            self.assigned_task_facility_id_tuple_set
        )

    def record_state(self, working: bool = True):
        """Record current 'state' in 'state_record_list'.

        Args:
            working (bool, optional): Whether to record the current state as working. Defaults to True.
        """
        if working:
            self.state_record_list.append(self.state)
        else:
            # if self.state == BaseWorkerState.WORKING:
            #     self.state_record_list.append(BaseWorkerState.FREE)
            # else:
            #     self.state_record_list.append(self.state)
            self.state_record_list.append(BaseWorkerState.ABSENCE)

    def set_assigned_pairs(self, pairs_iterable):
        """Set assigned pairs (non-destructive)."""
        self.assigned_task_facility_id_tuple_set = frozenset(pairs_iterable)

    def add_assigned_pair(self, pair: tuple[str, str]):
        """Add one assigned pair (non-destructive)."""
        cur = self.assigned_task_facility_id_tuple_set
        if pair in cur:
            return
        self.assigned_task_facility_id_tuple_set = frozenset((*cur, pair))

    def remove_assigned_pair(self, pair: tuple[str, str]):
        """Remove one assigned pair (non-destructive)."""
        cur = self.assigned_task_facility_id_tuple_set
        if pair not in cur:
            return
        self.assigned_task_facility_id_tuple_set = frozenset(
            x for x in cur if x != pair
        )

    def update_assigned_pairs(self, add=(), remove=()):
        """Update assigned pairs (non-destructive)."""
        cur = self.assigned_task_facility_id_tuple_set
        if not add and not remove:
            return
        s = set(cur)
        if remove:
            s.difference_update(remove)
        if add:
            s.update(add)
        self.assigned_task_facility_id_tuple_set = frozenset(s)

    def remove_absence_time_list(self, absence_time_list: list[int]):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]): List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.state_record_list):
                self.assigned_task_facility_id_tuple_set_record_list.pop(step_time)
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
                    self.assigned_task_facility_id_tuple_set_record_list.insert(
                        step_time, None
                    )
                    self.cost_record_list.insert(step_time, 0.0)
                    self.state_record_list.insert(step_time, BaseWorkerState.FREE)
                else:
                    self.assigned_task_facility_id_tuple_set_record_list.insert(
                        step_time,
                        self.assigned_task_facility_id_tuple_set_record_list[
                            step_time - 1
                        ],
                    )
                    self.cost_record_list.insert(step_time, 0.0)
                    self.state_record_list.insert(step_time, BaseWorkerState.FREE)

    def print_log(self, target_step_time: int):
        """
        Print log in `target_step_time`.

        Prints:
            - ID
            - name
            - state_record_list[target_step_time]
            - assigned_task_facility_id_tuple_set_record_list[target_step_time]

        Args:
            target_step_time (int): Target step time of printing log.
        """
        print(
            self.ID,
            self.name,
            self.state_record_list[target_step_time],
            self.assigned_task_facility_id_tuple_set_record_list[target_step_time],
        )

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """
        Print all log in chronological order.

        Args:
            backward (bool, optional): If True, print logs in reverse order. Defaults to False.
        """
        n = len(self.state_record_list)
        if backward:
            for i in range(n):
                t = n - 1 - i
                print("TIME: ", t)
                self.print_log(t)
        else:
            for t in range(n):
                print("TIME: ", t)
                self.print_log(t)

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
        time = -1
        for time, state in enumerate(self.state_record_list):
            if state != previous_state:
                if from_time == -1:
                    from_time = time
                elif to_time == -1:
                    to_time = time
                    if state == BaseWorkerState.FREE:
                        if previous_state == BaseWorkerState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseWorkerState.ABSENCE:
                            absence_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseWorkerState.WORKING:
                        if previous_state == BaseWorkerState.FREE:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseWorkerState.ABSENCE:
                            absence_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseWorkerState.ABSENCE:
                        if previous_state == BaseWorkerState.FREE:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseWorkerState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    from_time = time
                    to_time = -1
            previous_state = state

        # Suspended because of max time limitation
        if from_time > -1 and to_time == -1:
            if previous_state == BaseWorkerState.WORKING:
                working_time_list.append((from_time, time - from_time + finish_margin))
            elif previous_state == BaseWorkerState.FREE:
                ready_time_list.append((from_time, time - from_time + finish_margin))
            elif previous_state == BaseWorkerState.ABSENCE:
                absence_time_list.append((from_time, time - from_time + finish_margin))

        return ready_time_list, working_time_list, absence_time_list

    def has_workamount_skill(self, task_name: str, error_tol: float = 1e-10):
        """
        Check whether this worker has workamount skill or not.

        By checking workamount_skill_mean_map.

        Args:
            task_name (str): Task name.
            error_tol (float, optional): Measures against numerical error. Defaults to 1e-10.

        Returns:
            bool: Whether this worker has workamount skill of task_name or not.
        """
        if task_name in self.workamount_skill_mean_map:
            if self.workamount_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False

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

        dict_json_data = {}
        dict_json_data.update(
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
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
        return dict_json_data

    def get_mermaid_diagram(
        self,
        shape: str = "stadium",
        subgraph: bool = False,
        subgraph_name: str = "Worker",
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this worker.

        Args:
            shape (str, optional): Shape of this worker. Defaults to "stadium".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to False.
            subgraph_name (str, optional): Name of subgraph. Defaults to "Worker".
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
        subgraph_name: str = "Worker",
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this worker.

        Args:
            orientations (str, optional): Orientation of mermaid diagram. Defaults to "LR".
            shape (str, optional): Shape of mermaid diagram. Defaults to "stadium".
            subgraph (bool, optional): Subgraph or not. Defaults to False.
            subgraph_name (str, optional): Subgraph name. Defaults to "Worker".
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
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get gantt mermaid data of this worker.

        Args:
            range_time (tuple[int, int], optional): Range time of gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): Detailed information or not. Defaults to False.
            id_name_dict (dict[str, str], optional): ID to name dictionary. Defaults to None.

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

                text = self.name + "[READY]"
                if (
                    detailed_info is True
                    and id_name_dict is not None
                    and self.ID in id_name_dict
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
                    # Ensure all items in task_name_list are strings (convert tuples to strings)
                    task_name_list = [
                        str(task) if isinstance(task, tuple) else task
                        for task in task_name_list
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

            text = self.name
            if (
                detailed_info is True
                and id_name_dict is not None
                and self.ID in id_name_dict
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
                # Ensure all items in task_name_list are strings (convert tuples to strings)
                task_name_list = [
                    str(task) if isinstance(task, tuple) else task
                    for task in task_name_list
                ]
                if task_name_list:
                    text = f"{self.name} * {'\u0026'.join(task_name_list)}"

            list_of_lines.append(f"{text}:{int(clipped_start)},{int(clipped_end)}")
        return list_of_lines
