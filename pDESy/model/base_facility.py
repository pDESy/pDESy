#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from enum import IntEnum
import numpy as np
from .base_task import BaseTaskState


class BaseFacilityState(IntEnum):
    FREE = 0
    WORKING = 1


class BaseFacility(object, metaclass=abc.ABCMeta):
    """BaseFacility
    BaseFacility class for expressing a factory.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter.
            Name of this facility.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None -> str(uuid.uuid4()).
        factory_id (str, optional):
            Basic parameter.
            ID of Factory which this facility is belonged.
            Defaults to None.
        cost_per_time (float, optional):
            Basic parameter.
            Cost of this facility per unit time.
            Defaults to 0.0.
        solo_working (bool, optional):
            Basic parameter.
            Flag whether this facility can work any task with other facilities or not.
            Defaults to False.
        workamount_skill_mean_map (Dict[str, float], optional):
            Basic parameter.
            Mean skill for expressing progress in unit time.
            Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional):
            Basic parameter.
            Standard deviation of skill for expressing progress in unit time.
            Defaults to {}.
        state (BaseFacilityState, optional):
            Basic variable.
            State of this facility in simulation.
            Defaults to BaseFacilityState.FREE.
        state_record_list (List[BaseFacilityState], optional):
            Basic variable.
            Record list of state.
            Defaults to None -> [].
        cost_list (List[float], optional):
            Basic variable.
            History or record of his or her cost in simulation.
            Defaults to None -> [].
        start_time_list (List[int], optional):
            Basic variable.
            History or record of his or her start time in simulation.
            Defaults to None -> [].
        finish_time_list (List[int], optional):
            Basic variable.
            History or record of his or her finish time in simulation.
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
        factory_id=None,
        cost_per_time=0.0,
        solo_working=False,
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        # Basic variables
        state=BaseFacilityState.FREE,
        state_record_list=None,
        cost_list=None,
        start_time_list=None,
        finish_time_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.factory_id = factory_id if factory_id is not None else None
        self.cost_per_time = cost_per_time if cost_per_time != 0.0 else 0.0
        self.solo_working = solo_working if solo_working is not None else False
        self.workamount_skill_mean_map = (
            workamount_skill_mean_map if workamount_skill_mean_map is not {} else {}
        )
        self.workamount_skill_sd_map = (
            workamount_skill_sd_map if workamount_skill_sd_map is not None else {}
        )

        # ----
        # Changeable variablng factory.e on simulation
        # --
        # Basic variables
        if state is not BaseFacilityState.FREE:
            self.state = state
        else:
            self.state = BaseFacilityState.FREE

        if state_record_list is not None:
            self.state_record_list = state_record_list
        else:
            self.state_record_list = []

        if cost_list is not None:
            self.cost_list = cost_list
        else:
            self.cost_list = []

        if start_time_list is not None:
            self.start_time_list = start_time_list
        else:
            self.start_time_list = []

        if finish_time_list is not None:
            self.finish_time_list = finish_time_list
        else:
            self.finish_time_list = []

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
            str: name of BaseFacility
        Examples:
            >>> r = BaseFacility("r")
            >>> print(r)
            'r'
        """
        return "{}".format(self.name)

    def export_dict_json_data(self):
        dict_json_data = {}
        dict_json_data.update(
            type="BaseFacility",
            name=self.name,
            ID=self.ID,
            factory_id=self.factory_id if self.factory_id is not None else None,
            cost_per_time=self.cost_per_time,
            solo_working=self.solo_working,
            workamount_skill_mean_map=self.workamount_skill_mean_map,
            workamount_skill_sd_map=self.workamount_skill_sd_map,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            cost_list=self.cost_list,
            start_time_list=self.start_time_list,
            finish_time_list=self.finish_time_list,
            assigned_task_list=[t.ID for t in self.assigned_task_list],
            assigned_task_id_record=self.assigned_task_id_record,
        )
        return dict_json_data

    def initialize(self):
        """
        Initialize the following basic variables of BaseFacility

        - state
        - state_record_list
        - cost_list
        - start_time_list
        - finish_time_list
        - assigned_task_list
        - assigned_task_id_record
        """
        self.state = BaseFacilityState.FREE
        self.state_record_list = []
        self.cost_list = []
        self.start_time_list = []
        self.finish_time_list = []
        self.assigned_task_list = []
        self.assigned_task_id_record = []

    def record_assigned_task_id(self):
        """
        Record assigned task id in this time.
        """
        self.assigned_task_id_record.append(
            [task.ID for task in self.assigned_task_list]
        )

    def record_state(self):
        """
        Record state
        """
        self.state_record_list.append(self.state)

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
