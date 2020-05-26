#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from enum import IntEnum
from numpy.random import normal
from .base_task import BaseTaskState


class BaseResourceState(IntEnum):
    FREE = 0
    WORKING = 1


class BaseResource(object, metaclass=abc.ABCMeta):
    def __init__(
        self,
        name: str,
        team_id: str,
        cost_per_time=None,
        workamount_skill_mean_map=None,
        workamount_skill_sd_map=None,
        quality_skill_mean_map=None,
    ):

        # Constraint variables on simulation
        self.name = name
        self.team_id = team_id
        self.cost_per_time = cost_per_time if cost_per_time is not None else 0.0
        self.workamount_skill_mean_map = (
            workamount_skill_mean_map if workamount_skill_mean_map is not None else {}
        )
        self.workamount_skill_sd_map = (
            workamount_skill_sd_map if workamount_skill_sd_map is not None else {}
        )
        self.quality_skill_mean_map = (
            quality_skill_mean_map if quality_skill_mean_map is not None else {}
        )

        # Changeable variable on simulation
        self.state = BaseResourceState.FREE
        self.cost_list = []
        self.start_time_list = []
        self.finish_time_list = []
        self.assigned_task_list = []

    def __str__(self):
        return "{}".format(self.name)

    def initialize(self, error_tol=1e-10):
        self.state = BaseResourceState.FREE
        self.cost_list = []
        self.start_time_list = []
        self.finish_time_list = []
        self.assigned_task_list = []

    def set_workamount_skill_mean_map(
        self, workamount_skill_mean_map, update_other_skill_info=False
    ):
        self.workamount_skill_mean_map = workamount_skill_mean_map
        if update_other_skill_info:
            self.workamount_skill_sd_map = {}
            self.quality_skill_mean_map = {}
            keys = self.workamount_skill_mean_map.keys()
            for key in keys:
                self.workamount_skill_sd_map[key] = 0.0
                self.quality_skill_mean_map[key] = 0.0

    def has_skill(self, task_name, error_tol=1e-10):
        if task_name in self.workamount_skill_mean_map:
            if self.workamount_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False

    def get_work_amount_skill_point(self, task_name):
        if not self.has_skill(task_name):
            return 0.0
        skill_mean = self.workamount_skill_mean_map[task_name]
        skill_sd = self.workamount_skill_sd_map[task_name]
        base_progress = normal(skill_mean, skill_sd)
        sum_of_working_task_in_this_time = sum(
            map(
                lambda task: task.state == BaseTaskState.WORKING,
                self.assigned_task_list,
            )
        )
        return base_progress / float(sum_of_working_task_in_this_time)

    def get_quality_skill_point(self, task_name):
        if not self.has_skill(task_name):
            return 0.0
        return self.quality_skill_mean_map[task_name]
