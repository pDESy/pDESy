#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_worker."""

import abc
import uuid
from enum import IntEnum
import numpy as np

from .base_task import BaseTaskState


class BaseWorkerState(IntEnum):
    """BaseWorkerState."""

    FREE = 0
    WORKING = 1
    ABSENCE = -1


class BaseWorker(object, metaclass=abc.ABCMeta):
    """BaseWorker.

    BaseWorker class for expressing a worker.
    This class will be used as template.

    Args:
        name (str, optional):
            Basic parameter.
            Name of this worker.
            Defaults to None -> "New Worker"
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None -> str(uuid.uuid4()).
        team_id (str, optional):
            Basic parameter.
            Defaults to None.
        main_workplace_id (str, optional):
            Basic parameter.
            Defaults to None.
        cost_per_time (float, optional):
            Basic parameter.
            Cost of this worker per unit time.
            Defaults to 0.0.
        solo_working (bool, optional):
            Basic parameter.
            Flag whether this worker can work with other workers or not.
            Defaults to False.
        workamount_skill_mean_map (Dict[str, float], optional):
            Basic parameter.
            Skill for expressing progress in unit time.
            Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional):
            Basic parameter.
            Standard deviation of skill for expressing progress in unit time.
            Defaults to {}.
        facility_skill_map (Dict[str, float], optional):
            Basic parameter.
            Skill for operating facility in unit time.
            Defaults to {}.
        absence_time_list (List[int], optional):
            List of absence time of simulation.
            Defaults to None -> [].
        state (BaseWorkerState, optional):
            Basic variable.
            State of this worker in simulation.
            Defaults to BaseWorkerState.FREE.
        state_record_list (List[BaseWorkerState], optional):
            Basic variable.
            Record list of state.
            Defaults to None -> [].
        cost_list (List[float], optional):
            Basic variable.
            History or record of his or her cost in simulation.
            Defaults to None -> [].
        assigned_task_list (List[BaseTask], optional):
            Basic variable.
            State of his or her assigned tasks in simulation.
            Defaults to None -> [].
        assigned_task_id_record (List[List[str]], optional):
            Basic variable.
            Record of his or her assigned tasks' id in simulation.
            Defaults to None -> [].
        quality_skill_mean_map (Dict[str, float], optional):
            Advanced parameter.
            Skill for expressing quality in unit time.
            Defaults to {}.
        quality_skill_sd_map (Dict[str, float], optional):
            Advanced parameter.
            Standard deviation of skill for expressing quality in unit time.
            Defaults to {}.
    """

    def __init__(
        self,
        # Basic parameters
        name=None,
        ID=None,
        team_id=None,
        main_workplace_id=None,
        cost_per_time=0.0,
        solo_working=False,
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        facility_skill_map={},
        absence_time_list=None,
        # Basic variables
        state=BaseWorkerState.FREE,
        state_record_list=None,
        cost_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
        # Advanced parameters for customized simulation
        quality_skill_mean_map={},
        quality_skill_sd_map={},
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Worker"
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.team_id = team_id if team_id is not None else None
        self.main_workplace_id = (
            main_workplace_id if main_workplace_id is not None else None
        )
        self.cost_per_time = cost_per_time if cost_per_time != 0.0 else 0.0
        self.solo_working = solo_working if solo_working is not None else False
        self.workamount_skill_mean_map = (
            workamount_skill_mean_map if workamount_skill_mean_map != {} else {}
        )
        self.workamount_skill_sd_map = (
            workamount_skill_sd_map if workamount_skill_sd_map is not None else {}
        )
        self.absence_time_list = (
            absence_time_list if absence_time_list is not None else []
        )

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if state is not BaseWorkerState.FREE:
            self.state = state
        else:
            self.state = BaseWorkerState.FREE

        if state_record_list is not None:
            self.state_record_list = state_record_list
        else:
            self.state_record_list = []

        if cost_list is not None:
            self.cost_list = cost_list
        else:
            self.cost_list = []

        if assigned_task_list is not None:
            self.assigned_task_list = assigned_task_list
        else:
            self.assigned_task_list = []

        if assigned_task_id_record is not None:
            self.assigned_task_id_record = assigned_task_id_record
        else:
            self.assigned_task_id_record = []

        self.facility_skill_map = (
            facility_skill_map if facility_skill_map is not None else {}
        )

        # --
        # Advanced parameter for customized simulation
        self.quality_skill_mean_map = (
            quality_skill_mean_map if quality_skill_mean_map is not None else {}
        )
        self.quality_skill_sd_map = (
            quality_skill_sd_map if quality_skill_sd_map is not None else {}
        )

    def has_facility_skill(self, facility_name, error_tol=1e-10):
        """
        Check whether he or she has facility skill or not.

        By checking facility_skill_map.

        Args:
            facility_name (str):
                Facility name
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.

        Returns:
            bool: whether he or she has workamount skill of task_name or not
        """
        if facility_name in self.facility_skill_map:
            if self.facility_skill_map[facility_name] > 0.0 + error_tol:
                return True
        return False

    def has_quality_skill(self, task_name, error_tol=1e-10):
        """
        Check whether he or she has quality skill or not.

        By checking quality_skill_mean_map.

        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.

        Returns:
            bool: whether he or she has quality skill of task_name or not
        """
        if task_name in self.quality_skill_mean_map:
            if self.quality_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False

    def get_quality_skill_point(self, task_name, seed=None):
        """
        Get point of quality by his or her contribution in this time.

        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Countermeasures against numerical error.
                Defaults to 1e-10.

        Returns:
            float: Point of quality by his or her contribution in this time
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

    def check_update_state_from_absence_time_list(self, step_time):
        """
        Check and Update state of all resources to ABSENCE or FREE or WORKING.

        Args:
            step_time (int):
                Target step time of checking and updating state of workers and facilities.
        """
        if step_time in self.absence_time_list:
            self.state = BaseWorkerState.ABSENCE
        else:
            if len(self.assigned_task_list) == 0:
                self.state = BaseWorkerState.FREE
            else:
                self.state = BaseWorkerState.WORKING

    def __str__(self):
        """str.

        Returns:
            str: name of BaseResource
        Examples:
            >>> r = BaseResource("r")
            >>> print(r)
            'r'
        """
        return "{}".format(self.name)

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseResource.

        If `state_info` is True, the following attributes are initialized.

          - `state`
          - `assigned_task_list`

        If log_info is True, the following attributes are initialized.

          - `state_record_list`
          - `cost_list`
          - `assigned_task_id_record`

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaults to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        if state_info:
            self.state = BaseWorkerState.FREE
            self.assigned_task_list = []

        if log_info:
            self.state_record_list = []
            self.cost_list = []
            self.assigned_task_id_record = []

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.state_record_list = self.state_record_list[::-1]
        self.cost_list = self.cost_list[::-1]
        self.assigned_task_id_record = self.assigned_task_id_record[::-1]

    def record_assigned_task_id(self):
        """Record assigned task id to `assigned_task_id_record`."""
        self.assigned_task_id_record.append(
            [task.ID for task in self.assigned_task_list]
        )

    def record_state(self, working=True):
        """Record current 'state' in 'state_record_list'."""
        if working:
            self.state_record_list.append(self.state)
        else:
            # if self.state == BaseWorkerState.WORKING:
            #     self.state_record_list.append(BaseWorkerState.FREE)
            # else:
            #     self.state_record_list.append(self.state)
            self.state_record_list.append(BaseWorkerState.ABSENCE)

    def remove_absence_time_list(self, absence_time_list):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.state_record_list):
                self.assigned_task_id_record.pop(step_time)
                self.cost_list.pop(step_time)
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
                    self.assigned_task_id_record.insert(step_time, None)
                    self.cost_list.insert(step_time, 0.0)
                    self.state_record_list.insert(step_time, BaseWorkerState.FREE)
                else:
                    self.assigned_task_id_record.insert(
                        step_time, self.assigned_task_id_record[step_time - 1]
                    )
                    self.cost_list.insert(step_time, 0.0)
                    self.state_record_list.insert(step_time, BaseWorkerState.FREE)

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time` as follows:

        - ID
        - name
        - state_record_list[target_step_time]
        - assigned_task_id_record[target_step_time]

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        print(
            self.ID,
            self.name,
            self.state_record_list[target_step_time],
            self.assigned_task_id_record[target_step_time],
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
        absence_time_list = []
        previous_state = None
        from_time = -1
        to_time = -1
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

    def has_workamount_skill(self, task_name, error_tol=1e-10):
        """
        Check whether he or she has workamount skill or not.

        By checking workamount_skill_mean_map.

        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.

        Returns:
            bool: whether he or she has workamount skill of task_name or not
        """
        if task_name in self.workamount_skill_mean_map:
            if self.workamount_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False

    def get_work_amount_skill_progress(self, task_name, seed=None):
        """
        Get progress of workamount by his or her contribution in this time.

        If he or she has multiple tasks in this time,
        progress `p_r(t)` is defined as follows:

        p_r(t)={ps_r(t)}/{N_r(t)}

        - `ps_r(t)`: progress if he or she has only this task in this time
        - `N_r(t)`: Number of allocated tasks to him or her in this time


        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Countermeasures against numerical error.
                Defaults to 1e-10.

        Returns:
            float: Progress of workamount by his or her contribution in this time
        """
        if seed is not None:
            np.random.seed(seed=seed)
        if not self.has_workamount_skill(task_name):
            return 0.0
        if self.state == BaseWorkerState.ABSENCE:
            return 0.0
        skill_mean = self.workamount_skill_mean_map[task_name]
        if task_name not in self.workamount_skill_sd_map:
            skill_sd = 0
        else:
            skill_sd = self.workamount_skill_sd_map[task_name]
        base_progress = np.random.normal(skill_mean, skill_sd)
        sum_of_working_task_in_this_time = sum(
            map(
                lambda task: task.state == BaseTaskState.WORKING
                or task.state == BaseTaskState.WORKING_ADDITIONALLY,
                self.assigned_task_list,
            )
        )
        return base_progress / float(sum_of_working_task_in_this_time)

    def export_dict_json_data(self):
        """
        Export the information of this worker to JSON data.

        Returns:
            dict: JSON format data.
        """
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
            cost_list=self.cost_list,
            assigned_task_list=[t.ID for t in self.assigned_task_list],
            assigned_task_id_record=self.assigned_task_id_record,
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
            shape (str, optional):
                Shape of this worker.
                Defaults to "stadium".
            subgraph (bool, optional):
                Whether to use subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Name of subgraph.
                Defaults to "Worker".
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
            orientations (str, optional):
                Orientation of mermaid diagram.
                    https://mermaid.js.org/syntax/flowchart.html#direction
                Defaults to "LR".
            shape (str, optional):
                Shape of mermaid diagram.
                Defaults to "stadium".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Subgraph name.
                Defaults to "Worker".
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_mermaid_diagram(
            shape=shape,
            subgraph=subgraph,
            subgraph_name=subgraph_name,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")
