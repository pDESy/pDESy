#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
import numpy as np


class BaseComponent(object, metaclass=abc.ABCMeta):
    def __init__(
        self,
        name: str,
        ID=None,
        error_tolerance=None,
        depending_component_list=None,
        depended_component_list=None,
        targeted_task_list=None,
    ):
        # ----
        # Constraint variables on simulation
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())

        if error_tolerance is not None:
            self.error_tolerance = error_tolerance
        else:
            self.error_tolerance = 0.0

        if depending_component_list is not None:
            self.depending_component_list = depending_component_list
        else:
            self.depending_component_list = []

        if depended_component_list is not None:
            self.depended_component_list = depended_component_list
        else:
            self.depended_component_list = []

        if targeted_task_list is not None:
            self.targeted_task_list = targeted_task_list
        else:
            self.targeted_task_list = []

        # ----
        # Changeable variable on simulation
        self.error = int(0)

    def extend_child_component_list(self, child_component_list):
        self.depended_component_list.extend(child_component_list)
        for child_c in child_component_list:
            child_c.depending_component_list.append(self)

    def append_child_component(self, child_component):
        self.depended_component_list.append(child_component)
        child_component.depending_component_list.append(self)

    def extend_targeted_task_list(self, targeted_task_list):
        self.targeted_task_list.extend(targeted_task_list)
        for child_t in targeted_task_list:
            child_t.target_component_list.append(self)

    def append_targeted_task(self, targeted_task):
        self.targeted_task_list.append(targeted_task)
        targeted_task.target_component_list.append(self)

    def initialize(self):
        self.error = int(0)

    def update_error_value(self, no_error_prob, error_increment, seed=None):
        if seed is not None:
            np.random.seed(seed=seed)
        if np.random.rand() >= no_error_prob:
            self.error = self.error + error_increment

    def __str__(self):
        return "{}".format(self.name)

    def create_data_for_gantt_plotly(self, init_datetime, unit_timedelta):
        start_time = min(map(lambda t: min(t.start_time_list), self.targeted_task_list))
        finish_time = max(
            map(lambda t: max(t.finish_time_list), self.targeted_task_list)
        )
        df = [
            dict(
                Task=self.name,
                Start=(init_datetime + start_time * unit_timedelta).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                Finish=(init_datetime + finish_time * unit_timedelta).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                Type="Component",
            )
        ]
        return df
