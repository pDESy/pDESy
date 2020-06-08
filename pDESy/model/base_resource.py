#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from enum import IntEnum
import numpy as np
from .base_task import BaseTaskState


class BaseResourceState(IntEnum):
    FREE = 0
    WORKING = 1


class BaseResource(object, metaclass=abc.ABCMeta):
    """BaseResource
    BaseResource class for expressing a team.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter. Name of this resource.
        team_id (str, optional):
            Basic parameter.
            Team ID will be defined automatically on adding team.
            Defaults to None.
        cost_per_time (float, optional):
            Basic parameter.
            Cost of this resource per unit time.
            Defaults to 0.0.
        workamount_skill_mean_map (Dict[str, float], optional):
            Basic parameter.
            Skill for expressing progress in unit time.
            Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional):
            Basic parameter.
            Standard deviation of skill for expressing progress in unit time.
            Defaults to {}.
        quality_skill_mean_map (Dict[str, float], optional):
            Advanced parameter.
            Skill for expressing quality in unit time.
            Defaults to {}.
        quality_skill_sd_map (Dict[str, float], optional):
            Advanced parameter.
            Standard deviation of skill for expressing quality in unit time.
            Defaults to {}.
        state (BaseResourceState, optional):
            Basic variable.
            State of this resource in simulation.
            Defaults to BaseResourceState.FREE.
        cost_list (List[float], optional):
            Basic variable.
            History or record of his or her cost in simumation.
            Defaults to None -> [].
        start_time_list (List[int], optional):
            Basic variable.
            History or record of his or her start time in simumation.
            Defaults to None -> [].
        finish_time_list (List[int], optional):
            Basic variable.
            History or record of his or her finish time in simumation.
            Defaults to None -> [].
        assigned_task_list (List[int], optional):
            Basic variable.
            State of his or her assigned tasks in simumation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        team_id=None,
        cost_per_time=0.0,
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        # Advanced parameters for customized simulation
        quality_skill_mean_map={},
        quality_skill_sd_map={},
        # Basic variables
        state=BaseResourceState.FREE,
        cost_list=None,
        start_time_list=None,
        finish_time_list=None,
        assigned_task_list=None,
        # Advanced parameters for customized simulation
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name
        self.team_id = team_id if team_id is not None else None
        self.cost_per_time = cost_per_time if cost_per_time != 0.0 else 0.0
        self.workamount_skill_mean_map = (
            workamount_skill_mean_map if workamount_skill_mean_map is not {} else {}
        )
        self.workamount_skill_sd_map = (
            workamount_skill_sd_map if workamount_skill_sd_map is not None else {}
        )
        # --
        # Advanced parameter for customized simulation
        self.quality_skill_mean_map = (
            quality_skill_mean_map if quality_skill_mean_map is not None else {}
        )
        self.quality_skill_sd_map = (
            quality_skill_sd_map if quality_skill_sd_map is not None else {}
        )

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if state is not BaseResourceState.FREE:
            self.state = state
        else:
            self.state = BaseResourceState.FREE

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

        # --
        # Advanced varriables for customized simulation

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

    def initialize(self, error_tol=1e-10):
        """
        Initialize the changeable variables of BaseResource

        - state
        - cost_list
        - start_time_list
        - finish_time_list
        - assigned_task_list
        """
        self.state = BaseResourceState.FREE
        self.cost_list = []
        self.start_time_list = []
        self.finish_time_list = []
        self.assigned_task_list = []

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

    def has_quality_skill(self, task_name, error_tol=1e-10):
        """
        Check whether he or she has quality skill or not
        by checking quality_skill_mean_map.

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
