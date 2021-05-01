#!/usr/bin/env python
# -*- coding: utf-8 -*-

from debtcollector import removals
import abc
import uuid
from enum import IntEnum
import numpy as np
from .base_task import BaseTaskState


@removals.remove
class BaseResourceState(IntEnum):
    """
    Note:
        DEPRICATED from v1.3.
        Use BaseWorkerState or BaseFacilityState as instead.
    """

    FREE = 0
    WORKING = 1


@removals.remove
class BaseResource(object, metaclass=abc.ABCMeta):
    """BaseResource

    Note:
        DEPRICATED from v1.3.
        Use BaseWorkerState or BaseFacilityState as instead.


    BaseResource class for expressing a team.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter. Name of this resource.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        team_id (str, optional):
            Basic parameter.
            Team ID will be defined automatically on adding team.
            Defaults to None.
        cost_per_time (float, optional):
            Basic parameter.
            Cost of this resource per unit time.
            Defaults to 0.0.
        solo_working (bool, optional):
            Basic parameter.
            Flag whether this resource can work with other resources or not.
            Defaults to False.
        workamount_skill_mean_map (Dict[str, float], optional):
            Basic parameter.
            Skill for expressing progress in unit time.
            Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional):
            Basic parameter.
            Standard deviation of skill for expressing progress in unit time.
            Defaults to {}.
        state (BaseResourceState, optional):
            Basic variable.
            State of this resource in simulation.
            Defaults to BaseResourceState.FREE.
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
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        team_id=None,
        cost_per_time=0.0,
        solo_working=False,
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        # Basic variables
        state=BaseResourceState.FREE,
        state_record_list=None,
        cost_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.team_id = team_id if team_id is not None else None
        self.cost_per_time = cost_per_time if cost_per_time != 0.0 else 0.0
        self.solo_working = solo_working if solo_working is not None else False
        self.workamount_skill_mean_map = (
            workamount_skill_mean_map if workamount_skill_mean_map != {} else {}
        )
        self.workamount_skill_sd_map = (
            workamount_skill_sd_map if workamount_skill_sd_map is not None else {}
        )

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if state is not BaseResourceState.FREE:
            self.state = state
        else:
            self.state = BaseResourceState.FREE

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

    def __str__(self):
        """
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
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        if state_info:
            self.state = BaseResourceState.FREE
            self.assigned_task_list = []

        if log_info:
            self.state_record_list = []
            self.cost_list = []
            self.assigned_task_id_record = []

    def reverse_log_information(self):
        """
        Reverse log information of all.
        """
        self.state_record_list = self.state_record_list[::-1]
        self.cost_list = self.cost_list[::-1]
        self.assigned_task_id_record = self.assigned_task_id_record[::-1]

    def record_assigned_task_id(self):
        """
        Record assigned task id to `assigned_task_id_record`.
        """
        self.assigned_task_id_record.append(
            [task.ID for task in self.assigned_task_list]
        )

    def record_state(self):
        """
        Record current 'state' in 'state_record_list'
        """
        self.state_record_list.append(self.state)

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
        previous_state = None
        from_time = -1
        to_time = -1
        for time, state in enumerate(self.state_record_list):
            if state != previous_state:
                if from_time == -1:
                    from_time = time
                elif to_time == -1:
                    to_time = time
                    if state == BaseResourceState.FREE:
                        if previous_state == BaseResourceState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseResourceState.WORKING:
                        if previous_state == BaseResourceState.FREE:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    from_time = time
                    to_time = -1
            previous_state = state

            if previous_state == BaseResourceState.WORKING:
                working_time_list.append(
                    (from_time, time - 1 - from_time + finish_margin)
                )
            elif previous_state == BaseResourceState.FREE:
                ready_time_list.append(
                    (from_time, time - 1 - from_time + finish_margin)
                )
        return ready_time_list, working_time_list

    def has_workamount_skill(self, task_name, error_tol=1e-10):
        """
        Check whether he or she has workamount skill or not
        by checking workamount_skill_mean_map.

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

        If he or she has multipul tasks in this time,
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
