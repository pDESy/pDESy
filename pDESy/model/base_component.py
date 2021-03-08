#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
import datetime
from enum import IntEnum
from .base_task import BaseTaskState


class BaseComponentState(IntEnum):
    """BaseComponentState"""

    NONE = 0
    READY = 1
    WORKING = 2
    FINISHED = -1
    REMOVED = -2


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
            Space size related to base_workplace's max_space_size.
            Default to None -> 1.0.
        state (BaseComponentState, optional):
            Basic variable.
            State of this task in simulation.
            Defaults to BaseComponentState.NONE.
        state_record_list (List[BaseComponentState], optional):
            Basic variable.
            Record list of state.
            Defaults to None -> [].
        placed_workplace (BaseWorkplace, optional):
            Basic variable.
            A workplace which this componetnt is placed in simulation.
            Defaults to None.
        placed_workplace_id_record (List[str], optional):
            Basic variable.
            Record of placed workplace ID in simulation.
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
        state=BaseComponentState.NONE,
        state_record_list=None,
        placed_workplace=None,
        placed_workplace_id_record=None,
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

        if state is not BaseComponentState.NONE:
            self.state = state
        else:
            self.state = BaseComponentState.NONE

        if state_record_list is not None:
            self.state_record_list = state_record_list
        else:
            self.state_record_list = []

        if placed_workplace is not None:
            self.placed_workplace = placed_workplace
        else:
            self.placed_workplace = None

        if placed_workplace_id_record is not None:
            self.placed_workplace_id_record = placed_workplace_id_record
        else:
            self.placed_workplace_id_record = []

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
        Append child component to `child_component_list`.

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

    def set_placed_workplace(self, placed_workplace, set_to_all_children=True):
        """
        Set the `placed_workplace`.

        Args:
            placed_workplace (BaseWorkplace):
                Workplace placed in this component
            set_to_all_children (bool):
                If True, set placed_workplace to all children components
                Default to True
        """
        self.placed_workplace = placed_workplace

        if set_to_all_children:
            for child_c in self.child_component_list:
                child_c.set_placed_workplace(
                    placed_workplace, set_to_all_children=set_to_all_children
                )

    def is_ready(self):
        """
        Check READY component or not.
        READY component is defined by satisfying the following conditions:

          - All tasks are not NONE.
          - There is no WORKING task in this component.
          - The states of append_targeted_task includes READY.

        Returns:
            bool: this component is READY or not.
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
        Extend the list of targeted tasks to `targeted_task_list`.

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
        Append targeted task to `targeted_task_list`.

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

    def initialize(self, state_info=True, log_info=True, check_task_state=True):
        """
        Initialize the following changeable basic variables of BaseComponent.
        If `state_info` is True, the following attributes are initialized.

          - `state`
          - `placed_workplace`

        If `log_info` is True, the following attributes are initialized.

          - `state_record_list`
          - `placed_workplace_id_record`

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
            check_task_state (bool):
                Check the state of each task in this component or not.
                Defaults to True.
        """
        if log_info:
            self.state_record_list = []
            self.placed_workplace_id_record = []

        if state_info:
            self.state = BaseComponentState.NONE
            self.placed_workplace = None

            if check_task_state:
                self.check_state()

    def reverse_log_information(self):
        """
        Reverse log information of all.
        """
        self.state_record_list = self.state_record_list[::-1]
        self.placed_workplace_id_record = self.placed_workplace_id_record[::-1]

    def check_state(self):
        """
        Check and update the `state` of this component.
        """
        self.__check_ready()
        self.__check_working()
        self.__check_finished()

    def __check_ready(self):
        if not all(
            map(lambda t: t.state == BaseTaskState.WORKING, self.targeted_task_list)
        ):
            if not all(
                map(
                    lambda t: t.state == BaseTaskState.FINISHED, self.targeted_task_list
                )
            ):
                if any(
                    map(
                        lambda t: t.state == BaseTaskState.READY,
                        self.targeted_task_list,
                    )
                ):
                    self.state = BaseComponentState.READY

    def __check_working(self):
        if any(
            map(lambda t: t.state == BaseTaskState.WORKING, self.targeted_task_list)
        ):
            self.state = BaseComponentState.WORKING

    def __check_finished(self):
        if all(
            map(lambda t: t.state == BaseTaskState.FINISHED, self.targeted_task_list)
        ):
            self.state = BaseComponentState.FINISHED

    def record_placed_workplace_id(self):
        """
        Record workplace id in this time to `placed_workplace_id_record`.
        """
        record = None
        if self.placed_workplace is not None:
            record = self.placed_workplace.ID
        self.placed_workplace_id_record.append(record)

    def record_state(self):
        """
        Record current `state` in `state_record_list`
        """
        self.state_record_list.append(self.state)

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

    def export_dict_json_data(self):
        """
        Export the information of this component to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type="BaseComponent",
            name=self.name,
            ID=self.ID,
            parent_component_list=[c.ID for c in self.parent_component_list],
            child_component_list=[c.ID for c in self.child_component_list],
            targeted_task_list=[t.ID for t in self.targeted_task_list],
            space_size=self.space_size,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            placed_workplace=self.placed_workplace.ID
            if self.placed_workplace is not None
            else None,
            placed_workplace_id_record=self.placed_workplace_id_record,
        )
        return dict_json_data

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
        previous_state = BaseComponentState.NONE
        from_time = -1
        to_time = -1
        for time, state in enumerate(self.state_record_list):
            if state != previous_state:
                if from_time == -1:
                    from_time = time
                elif to_time == -1:
                    to_time = time
                    if (
                        state == BaseComponentState.NONE
                        or state == BaseComponentState.FINISHED
                    ):
                        if previous_state == BaseComponentState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseComponentState.READY:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseComponentState.READY:
                        if previous_state == BaseComponentState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseComponentState.WORKING:
                        if previous_state == BaseComponentState.READY:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    from_time = time
                    to_time = -1
            previous_state = state

            if previous_state == BaseComponentState.WORKING:
                working_time_list.append(
                    (from_time, time - 1 - from_time + finish_margin)
                )
            elif previous_state == BaseComponentState.READY:
                ready_time_list.append(
                    (from_time, time - 1 - from_time + finish_margin)
                )
        return ready_time_list, working_time_list

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        view_ready=False,
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
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.

        Returns:
            list[dict]:
                Gantt plotly information of this BaseComponent
        """
        df = []
        (
            ready_time_list,
            working_time_list,
        ) = self.get_time_list_for_gannt_chart(finish_margin=finish_margin)

        if view_ready:
            for (from_time, length) in ready_time_list:
                to_time = from_time + length
                df.append(
                    dict(
                        Task=self.name,
                        Start=(init_datetime + from_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        Finish=(init_datetime + to_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        State="READY",
                        Type="Component",
                    )
                )
        for (from_time, length) in working_time_list:
            to_time = from_time + length
            df.append(
                dict(
                    Task=self.name,
                    Start=(init_datetime + from_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    Finish=(init_datetime + to_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    State="WORKING",
                    Type="Component",
                )
            )
        return df
