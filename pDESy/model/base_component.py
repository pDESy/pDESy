#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_component."""

import abc
import datetime
import uuid
from enum import IntEnum

import numpy as np

from .base_task import BaseTaskState


class BaseComponentState(IntEnum):
    """BaseComponentState."""

    NONE = 0
    READY = 1
    WORKING = 2
    FINISHED = -1
    REMOVED = -2


class BaseComponent(object, metaclass=abc.ABCMeta):
    """BaseComponent.

    BaseComponent class for expressing target product.
    This class can be used as template.

    Args:
        name (str, optional):
            Basic parameter.
            Name of this component.
            Defaults to None -> "New Component"
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
        parent_product(BaseProduct, optional):
            Basic parameter.
            Parent product.
            Defaults to None.
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
            A workplace which this component is placed in simulation.
            Defaults to None.
        placed_workplace_id_record (List[str], optional):
            Basic variable.
            Record of placed workplace ID in simulation.
            Defaults to None -> [].
        error_tolerance (float, optional):
            Advanced parameter.
        error (float, optional):
            Advanced variables.
    """

    def __init__(
        self,
        # Basic parameters
        name=None,
        ID=None,
        parent_component_list=None,
        child_component_list=None,
        targeted_task_list=None,
        space_size=None,
        parent_product=None,
        # Basic variables
        state=BaseComponentState.NONE,
        state_record_list=None,
        placed_workplace=None,
        placed_workplace_id_record=None,
        # Advanced parameters for customized simulation
        error_tolerance=None,
        # Advanced variables for customized simulation
        error=None,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Component"
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

        self.parent_product = parent_product if parent_product is not None else None

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

        # --
        # Advanced parameter for customized simulation
        if error_tolerance is not None:
            self.error_tolerance = error_tolerance
        else:
            self.error_tolerance = 0.0
        # Advanced variables for customized simulation
        if error is not None:
            self.error = error
        else:
            self.error = 0.0

    def extend_child_component_list(self, child_component_list):
        """
        Extend the list of child components.

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
        child_component.parent_product = self.parent_product

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
          - `error`


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
            self.error = 0.0

            if check_task_state:
                self.check_state()

    def update_error_value(
        self, no_error_prob: float, error_increment: float, seed=None
    ):
        """
        Update error value randomly.

        If no_error_prob >=1.0, error = error + error_increment.

        Args:
            no_error_prob (float): Probability of no error (0.0~1.0)
            error_increment (float): Increment of error variables if error has occurred.
            seed (int, optional): seed of creating random.rand(). Defaults to None.
        Examples:
            >>> c = Component("c")
            >>> c.update_error_value(0.9, 1.0, seed=32)
            >>> print(c.error)
            0.0
            >>> c.update_error_value(0.4, 1.0, seed=32)
            >>> print(c.error) # Random 1.0 or 0.0
            1.0
        Note:
            This method is developed for customized simulation.
        """
        if seed is not None:
            np.random.seed(seed=seed)
        if np.random.rand() > no_error_prob:
            self.error = self.error + error_increment

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.state_record_list = self.state_record_list[::-1]
        self.placed_workplace_id_record = self.placed_workplace_id_record[::-1]

    def check_state(self):
        """Check and update the `state` of this component."""
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
        """Record workplace id in this time to `placed_workplace_id_record`."""
        record = None
        if self.placed_workplace is not None:
            record = self.placed_workplace.ID
        self.placed_workplace_id_record.append(record)

    def record_state(self, working=True):
        """Record current `state` in `state_record_list`."""
        if working:
            self.state_record_list.append(self.state)
        else:
            if self.state == BaseComponentState.WORKING:
                self.state_record_list.append(BaseComponentState.READY)
            else:
                self.state_record_list.append(self.state)

    def remove_absence_time_list(self, absence_time_list):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.state_record_list):
                self.placed_workplace_id_record.pop(step_time)
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
                    self.placed_workplace_id_record.insert(step_time, None)
                    self.state_record_list.insert(step_time, BaseComponentState.NONE)
                else:
                    self.placed_workplace_id_record.insert(
                        step_time, self.placed_workplace_id_record[step_time - 1]
                    )

                    insert_state_before = self.state_record_list[step_time - 1]
                    insert_state_after = self.state_record_list[step_time]
                    if insert_state_before == BaseComponentState.WORKING:
                        if insert_state_after == BaseComponentState.FINISHED:
                            insert_state = BaseComponentState.FINISHED
                        else:
                            insert_state = BaseComponentState.READY
                        self.state_record_list.insert(step_time, insert_state)
                    elif (
                        insert_state_before == BaseComponentState.NONE
                        and insert_state_after == BaseComponentState.WORKING
                    ):
                        self.state_record_list.insert(
                            step_time, BaseComponentState.READY
                        )
                    else:
                        self.state_record_list.insert(
                            step_time, self.state_record_list[step_time - 1]
                        )

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time` as follows:

        - ID
        - name
        - sum of default workamount in related tasks
        - sum of remaining workamount in related tasks.
        - state_record_list[target_step_time]
        - placed_workplace_id_record[target_step_time]

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        sum_of_default_workamount = sum(
            task.default_work_amount for task in self.targeted_task_list
        )
        sum_of_remaining_workamount = sum(
            task.remaining_work_amount_record_list[target_step_time]
            for task in self.targeted_task_list
        )

        print(
            self.ID,
            self.name,
            sum_of_default_workamount,
            max(sum_of_remaining_workamount, 0.0),
            self.state_record_list[target_step_time],
            self.placed_workplace_id_record[target_step_time],
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

    def __str__(self):
        """str.

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
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
            parent_component_list=[c.ID for c in self.parent_component_list],
            child_component_list=[c.ID for c in self.child_component_list],
            targeted_task_list=[t.ID for t in self.targeted_task_list],
            space_size=self.space_size,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            placed_workplace=(
                self.placed_workplace.ID if self.placed_workplace is not None else None
            ),
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

        # Suspended because of max time limitation
        if from_time > -1 and to_time == -1:
            if previous_state == BaseComponentState.WORKING:
                working_time_list.append((from_time, time - from_time + finish_margin))
            elif previous_state == BaseComponentState.READY:
                ready_time_list.append((from_time, time - from_time + finish_margin))

        return ready_time_list, working_time_list

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        view_ready=False,
    ):
        """
        Create data for gantt plotly.

        From start_time_list and finish_time_list of BaseTask in targeted_task_list.

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
            for from_time, length in ready_time_list:
                to_time = from_time + length
                df.append(
                    {
                        "Task": self.name,
                        "Start": (init_datetime + from_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Finish": (init_datetime + to_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "State": "READY",
                        "Type": "Component",
                    }
                )
        for from_time, length in working_time_list:
            to_time = from_time + length
            df.append(
                {
                    "Task": self.name,
                    "Start": (init_datetime + from_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Finish": (init_datetime + to_time * unit_timedelta).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "State": "WORKING",
                    "Type": "Component",
                }
            )
        return df

    def get_mermaid_diagram(
        self,
        shape: str = "odd",
        subgraph: bool = False,
        subgraph_name: str = "Component",
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this component.
        Args:
            shape (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Subgraph name.
                Defaults to "Component".
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
        shape: str = "odd",
        subgraph: bool = False,
        subgraph_name: str = "Component",
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this component.
        Args:
            orientations (str, optional):
                Orientation of mermaid diagram.
                    https://mermaid.js.org/syntax/flowchart.html#direction
                Defaults to "LR".
            shape (str, optional):
                Shape of mermaid diagram.
                Defaults to "odd".
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Subgraph name.
                Defaults to "Component".
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
