#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
import datetime
from .base_task import BaseTaskState


class BaseComponent(object, metaclass=abc.ABCMeta):
    """BaseComponent
    BaseComponent class for expressing target product.
    This class can be used as template.

    Args:
        name (str):
            Basic parameter.
            Name of this component.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.

        name (str):
            Basic p Defaults to None -> str(uuid.uuid4()).
        parent_component_list(List[BaseComponent], optional):
            Basic parameter.
            List of parent BaseComponents.
            Defaults to None -> [].
        child_component_list (List[BaseComponent], optional):
            Basic parameter.
            List of child BaseComponents.
            Defaults to None -> [].
        targeted_task_list (List[BaseTask], optional):
            Basic parameter.
            List of targeted tasks.
            Defaults to None -> [].
        space_size (float, optional):
            Basic parameter.
            Space size related to base_factory's max_space_size.
            Default to None -> 1.0.
        placed_factory (BaseFactory, optional):
            Basic variable.
            A factory which this componetnt is placed in simulation.
            Defaults to None.
        placed_factory_id_record (List[str], optional):
            Basic variable.
            Record of placed factory ID in simulation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        parent_component_list=None,
        child_component_list=None,
        targeted_task_list=None,
        space_size=None,
        # Basic variables
        placed_factory=None,
        placed_factory_id_record=None,
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

        if space_size is not None:
            self.space_size = space_size
        else:
            self.space_size = 1.0

        if placed_factory is not None:
            self.placed_factory = placed_factory
        else:
            self.placed_factory = None

        if placed_factory_id_record is not None:
            self.placed_factory_id_record = placed_factory_id_record
        else:
            self.placed_factory_id_record = []

    def extend_child_component_list(self, child_component_list):
        """
        Extend the list of child components

        Args:
            child_component_list (List[BaseComponent]):
                List of BaseComponents which are children of this component.
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
                BaseComponent which is child of this component.
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

    def set_placed_factory(self, placed_factory, set_to_all_children=True):
        """
        Set the placed_factory

        Args:
            placed_factory (BaseFactory):
                Factory placed in this component
            set_to_all_children (bool):
                If True, set placed_factory to all children components
                Default to True
        """
        self.placed_factory = placed_factory

        if set_to_all_children:
            for child_c in self.child_component_list:
                child_c.set_placed_factory(
                    placed_factory, set_to_all_children=set_to_all_children
                )

    def is_ready(self):
        """
        Check READY component or not.
        READY component is defined by satisfying the following conditions:

        - All tasks are not NONE.
        - There is no WORKING task in this component.
        - The states of append_targeted_task includes READY.
        """
        all_none_flag = all(
            [task.state == BaseTaskState.NONE for task in self.targeted_task_list]
        )

        any_working_flag = any(
            [task.state == BaseTaskState.WORKING for task in self.targeted_task_list]
        )

        any_ready_flag = any(
            [task.state == BaseTaskState.READY for task in self.targeted_task_list]
        )

        all_finished_flag = all(
            [task.state == BaseTaskState.FINISHED for task in self.targeted_task_list]
        )

        if all_finished_flag:
            return False

        if not all_none_flag and (not any_working_flag) and any_ready_flag:
            return True

        return False

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
                Targeted task of this component
        Examples:
            >>> c = BaseComponent('c')
            >>> print([targeted_t.name for targeted_t in c.targeted_task_list])
            []
            >>> t1 = BaseTask('t1')
            >>> c.append_targeted_task(t1)
            >>> print([targeted_t.name for targeted_t in c.targeted_task_list])
            ['t1']
            >>> print(t1.target_component.name)
            'c'
        """
        self.targeted_task_list.append(targeted_task)
        targeted_task.target_component = self

    def initialize(self):
        """
        Initialize the following changeable basic variables of BaseComponent.

        - placed_factory
        - placed_factory_id_record
        """
        self.placed_factory = None
        self.placed_factory_id_record = []

    def record_placed_factory_id(self):
        """
        Record factory id in this time to placed_factory_id_record.
        """
        record = None
        if self.placed_factory is not None:
            record = self.placed_factory.ID
        self.placed_factory_id_record.append(record)

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
                Unit time of simulation
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
        Returns:
            list[dict]:
                Gantt plotly information of this BaseComponent
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
