#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
import datetime
from .base_task import BaseTaskState


class BaseComponent(object, metaclass=abc.ABCMeta):
    """BaseComponent
    BaseComponent class for expressing target product.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter.
            Name of this component.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        parent_component_list(List[BaseComponent], optional):
            Basic parameter.
            List of parent BaseComponents. Defaults to None.
        child_component_list (List[BaseComponent], optional):
            Basic parameter.
            List of child BaseComponents.
            Defaults to None.
        targeted_task_list (List[BaseTask], optional):
            Basic parameter.
            List of targeted tasks.
            Defaults to None.
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        parent_component_list=None,
        child_component_list=None,
        targeted_task_list=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())

        if parent_component_list is not None:
            self.parent_component_list = parent_component_list
        else:
            self.parent_component_list = []

        if child_component_list is not None:
            self.child_component_list = child_component_list
        else:
            self.child_component_list = []

        if targeted_task_list is not None:
            self.targeted_task_list = targeted_task_list
        else:
            self.targeted_task_list = []

    def extend_child_component_list(self, child_component_list):
        """
        Extend the list of child components

        Args:
            child_component_list (List[BaseComponent]):
                List of child BaseComponents
        Examples:
            >>> c = BaseComponent('c')
            >>> print([child_c.name for child_c in c.child_component_list])
            []
            >>> c.extend_child_component_list([BaseComponent('c1'),BaseComponent('c2')])
            >>> print([child_c.name for child_c in c.child_component_list])
            ['c1', 'c2']
        """
        for child_c in child_component_list:
            self.append_child_component(child_c)

    def append_child_component(self, child_component):
        """
        Append child component

        Args:
            child_component (BaseComponent):
                Child BaseComponent
        Examples:
            >>> c = BaseComponent('c')
            >>> print([child_c.name for child_c in c.child_component_list])
            []
            >>> c1 = BaseComponent('c1')
            >>> c.append_child_component(c1)
            >>> print([child_c.name for child_c in c.child_component_list])
            ['c1']
            >>> print([parent_c.name for parent_c in c1.parent_component_list])
            ['c']
        """
        self.child_component_list.append(child_component)
        child_component.parent_component_list.append(self)

    def extend_targeted_task_list(self, targeted_task_list):
        """
        Extend the list of targeted tasks

        Args:
            targeted_task_list (List[BaseTask]):
                List of targeted tasks
        Examples:
            >>> c = BaseComponent('c')
            >>> print([targeted_t.name for targeted_t in c.targeted_task_list])
            []
            >>> c.extend_targeted_task_list([BaseTask('t1'),BaseTask('t2')])
            >>> print([targeted_t.name for targeted_t in c.targeted_task_list])
            ['t1', 't2']
        """
        for targeted_task in targeted_task_list:
            self.append_targeted_task(targeted_task)

    def append_targeted_task(self, targeted_task):
        """
        Append targeted task

        Args:
            targeted_task (BaseTask):
                Targeted task
        Examples:
            >>> c = BaseComponent('c')
            >>> print([targeted_t.name for targeted_t in c.targeted_task_list])
            []
            >>> t1 = BaseTask('t1')
            >>> c.append_targeted_task(t1)
            >>> print([targeted_t.name for targeted_t in c.targeted_task_list])
            ['t1']
            >>> print([target_c.name for target_c in t1.target_component_list])
            ['c']
        """
        self.targeted_task_list.append(targeted_task)
        targeted_task.target_component_list.append(self)

    def get_state_record_list(self, auto_task=False):
        """
        Get state record list of this component.

        Args:
            auto_task (bool, optional):
                Include auto_task or not.
                Defaults to False.

        Returns:
            List(BaseTaskState): state time list of this component.
        """
        target_task_list = self.targeted_task_list
        if not auto_task:
            target_task_list = list(
                filter(lambda task: not task.auto_task, self.targeted_task_list)
            )
        finish_time = max(map(lambda t: max(t.finish_time_list), target_task_list))

        state_record = []
        for time in range(finish_time + 1):
            task_state_list = list(
                map(lambda task: task.get_state_from_record(time), target_task_list)
            )

            print(time, task_state_list)

            if task_state_list.count(BaseTaskState.FINISHED) == len(task_state_list):
                # Only FINIHSED -> FINISHED
                state_record.append(BaseTaskState.FINISHED)
            elif task_state_list.count(BaseTaskState.NONE) + task_state_list.count(
                BaseTaskState.FINISHED
            ) == len(task_state_list):
                # Only NONE or FINISHIED -> NONE
                state_record.append(BaseTaskState.NONE)
            elif task_state_list.count(BaseTaskState.WORKING) > 0:
                # if one more WORKING are existed -> WOKRKING
                state_record.append(BaseTaskState.WORKING)
            elif task_state_list.count(BaseTaskState.READY) > 0:
                state_record.append(BaseTaskState.READY)
            else:
                state_record.append(None)

        return state_record

    def get_ready_start_finish_time_list(self, auto_task=False):

        ready_time_list = []
        start_time_list = []
        finish_time_list = []

        state_record = self.get_state_record_list(auto_task=auto_task)
        print(state_record)
        if state_record[0] == BaseTaskState.READY:
            ready_time_list.append(0)
        elif state_record[0] == BaseTaskState.WORKING:
            start_time_list.append(0)

        for time in range(len(state_record) - 1):
            if state_record[time + 1] != state_record[time]:
                if state_record[time + 1] == BaseTaskState.READY:
                    ready_time_list.append(time + 1)
                elif state_record[time + 1] == BaseTaskState.WORKING:
                    start_time_list.append(time + 1)
                elif state_record[time + 1] == BaseTaskState.FINISHED:
                    finish_time_list.append(time + 1)

        return ready_time_list, start_time_list, finish_time_list

    def initialize(self):
        """
        Initialize the changeable variables of BaseComponent
        However, there is no initializing variables
        """
        pass

    def __str__(self):
        """
        Returns:
            str: name of BaseComponent
        Examples:
            >>> c = BaseComponent("c")
            >>> print(c)
            'c'
        """
        return "{}".format(self.name)

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
    ):
        """
        Create data for gantt plotly from start_time_list and finish_time_list
        of BaseTask in targeted_task_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulattion
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
        Returns:
            list[dict]: Gantt plotly information of this BaseComponent
        """
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
                Finish=(
                    init_datetime + (finish_time + finish_margin) * unit_timedelta
                ).strftime("%Y-%m-%d %H:%M:%S"),
                Type="Component",
            )
        ]
        return df
