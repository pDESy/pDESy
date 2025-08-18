#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_component."""

import abc
import sys
import uuid
import warnings
from enum import IntEnum

import numpy as np

from pDESy.model.base_priority_rule import (
    ResourcePriorityRuleMode,
    WorkplacePriorityRuleMode,
)
from pDESy.model.base_task import BaseTask, BaseTaskState


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
        child_component_id_set (set(str), optional):
            Basic parameter.
            Child BaseComponents id set.
            Defaults to None -> set().
        targeted_task_id_set (set(str), optional):
            Basic parameter.
            Targeted tasks id set.
            Defaults to None -> set().
        space_size (float, optional):
            Basic parameter.
            Space size related to base_workplace's max_space_size.
            Default to None -> 1.0.
        parent_product_id(str, optional):
            Basic parameter.
            Parent product id.
            Defaults to None.
        state (BaseComponentState, optional):
            Basic variable.
            State of this task in simulation.
            Defaults to BaseComponentState.NONE.
        state_record_list (List[BaseComponentState], optional):
            Basic variable.
            Record list of state.
            Defaults to None -> [].
        placed_workplace_id (str, optional):
            Basic variable.
            A workplace which this component is placed in simulation.
            Defaults to None.
        placed_workplace_id_record_list (List[str], optional):
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
        child_component_id_set=None,
        targeted_task_id_set=None,
        space_size=None,
        parent_product_id=None,
        # Basic variables
        state=BaseComponentState.NONE,
        state_record_list=None,
        placed_workplace_id=None,
        placed_workplace_id_record_list=None,
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

        if child_component_id_set is not None:
            self.child_component_id_set = child_component_id_set
        else:
            self.child_component_id_set = set()

        if targeted_task_id_set is not None:
            self.targeted_task_id_set = targeted_task_id_set
        else:
            self.targeted_task_id_set = set()

        if space_size is not None:
            self.space_size = space_size
        else:
            self.space_size = 1.0

        self.parent_product_id = (
            parent_product_id if parent_product_id is not None else None
        )

        if state is not BaseComponentState.NONE:
            self.state = state
        else:
            self.state = BaseComponentState.NONE

        if state_record_list is not None:
            self.state_record_list = state_record_list
        else:
            self.state_record_list = []

        if placed_workplace_id is not None:
            self.placed_workplace_id = placed_workplace_id
        else:
            self.placed_workplace_id = None

        if placed_workplace_id_record_list is not None:
            self.placed_workplace_id_record_list = placed_workplace_id_record_list
        else:
            self.placed_workplace_id_record_list = []

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
        TODO: This method is deprecated. Use `update_child_component_set` instead.

        Args:
            child_component_list (List[BaseComponent]):
                List of BaseComponents which are children of this component.
        """
        warnings.warn(
            "extend_child_component_list is deprecated.Use update_child_component_id_set instead.",
            DeprecationWarning,
        )
        for child_c in child_component_list:
            self.append_child_component(child_c)

    def update_child_component_set(self, child_component_set):
        """
        Update the set of child components.

        Args:
            child_component_set (set[BaseComponent]):
                Set of BaseComponents which are children of this component.
        """
        for child_c in child_component_set:
            self.add_child_component(child_c)

    def append_child_component(self, child_component):
        """
        Append child component to `child_component_id_set`.
        TODO: This method is deprecated. Use `add_child_component` instead.

        Args:
            child_component (BaseComponent):
                BaseComponent which is child of this component.
        """
        warnings.warn(
            "append_child_component is deprecated. Use add_child_component instead.",
            DeprecationWarning,
        )
        self.child_component_id_set.add(child_component.ID)
        child_component.parent_product_id = self.parent_product_id

    def add_child_component(self, child_component):
        """
        Add child component to `child_component_id_set`.

        Args:
            child_component (BaseComponent):
                BaseComponent which is child of this component.
        """
        if not isinstance(child_component, BaseComponent):
            raise TypeError(
                f"child_component must be BaseComponent, but {type(child_component)}"
            )
        if child_component.ID in self.child_component_id_set:
            warnings.warn(
                f"Child component {child_component.ID} is already added to {self.ID}.",
                UserWarning,
            )
        else:
            self.child_component_id_set.add(child_component.ID)
            child_component.parent_product_id = self.parent_product_id

    def extend_targeted_task_list(self, targeted_task_list):
        """
        Extend the list of targeted tasks to `targeted_task_list`.

        Args:
            targeted_task_list (List[BaseTask]):
                List of targeted tasks
        """
        warnings.warn(
            "extend_targeted_task_list is deprecated. Use update_targeted_task_set instead.",
            DeprecationWarning,
        )
        for targeted_task in targeted_task_list:
            self.append_targeted_task(targeted_task)

    def update_targeted_task_set(self, targeted_task_set):
        """
        Extend the list of targeted tasks to `targeted_task_id_set`.

        Args:
            targeted_task_set (set(BaseTask)):
                Targeted tasks set.
        """
        for targeted_task in targeted_task_set:
            self.add_targeted_task(targeted_task)

    def append_targeted_task(self, targeted_task):
        """
        Append targeted task to `targeted_task_list`.
        TODO: This method is deprecated. Use `add_targeted_task` instead.

        Args:
            targeted_task (BaseTask):
                Targeted task of this component
        """
        warnings.warn(
            "append_targeted_task is deprecated. Use add_targeted_task instead.",
            DeprecationWarning,
        )
        self.targeted_task_id_set.add(targeted_task.ID)
        targeted_task.target_component_id = self.ID

    def add_targeted_task(self, targeted_task):
        """
        Add targeted task to `targeted_task_list`.

        Args:
            targeted_task (BaseTask):
                Targeted task of this component
        """
        if not isinstance(targeted_task, BaseTask):
            raise TypeError(
                f"child_component must be BaseTask, but {type(targeted_task)}"
            )
        if targeted_task.ID in self.targeted_task_id_set:
            warnings.warn(
                f"Targeted task {targeted_task.ID} is already added to {self.ID}.",
                UserWarning,
            )
        else:
            self.targeted_task_id_set.add(targeted_task.ID)
            targeted_task.target_component_id = self.ID

    def create_task(
        self,
        name=None,
        ID=None,
        default_work_amount=None,
        work_amount_progress_of_unit_step_time=None,
        input_task_id_dependency_set=None,
        allocated_team_id_set=None,
        allocated_workplace_id_set=None,
        parent_workflow_id=None,
        workplace_priority_rule=WorkplacePriorityRuleMode.FSS,
        worker_priority_rule=ResourcePriorityRuleMode.MW,
        facility_priority_rule=ResourcePriorityRuleMode.SSP,
        need_facility=False,
        target_component_id=None,
        default_progress=None,
        due_time=None,
        auto_task=False,
        fixing_allocating_worker_id_set=None,
        fixing_allocating_facility_id_set=None,
        # Basic variables
        est=0.0,
        eft=0.0,
        lst=-1.0,
        lft=-1.0,
        remaining_work_amount=None,
        remaining_work_amount_record_list=None,
        state=BaseTaskState.NONE,
        state_record_list=None,
        allocated_worker_facility_id_tuple_set=None,
        allocated_worker_facility_id_tuple_set_record_list=None,
        # Advanced parameters for customized simulation
        additional_work_amount=None,
        # Advanced variables for customized simulation
        additional_task_flag=False,
        actual_work_amount=None,
    ):
        """
        Create a new BaseTask instance and add it to the targeted tasks.
        Args:
            name (str, optional):
                Basic parameter.
                Name of this task.
                Defaults to None -> "New Task".
            ID (str, optional):
                Basic parameter.
                ID will be defined automatically.
                Defaults to None -> str(uuid.uuid4()).
            default_work_amount (float, optional):
                Basic parameter.
                Default workamount of this BaseTask.
                Defaults to None -> 10.0.
            work_amount_progress_of_unit_step_time (float, optional)
                Baseline of work amount progress of unit step time.
                Default to None -> 1.0.
            input_task_id_dependency_set (set(tuple(str, BaseTaskDependency)), optional):
                Basic parameter.
                Set of input BaseTask id and type of dependency(FS, SS, SF, F/F) tuple.
                Defaults to None -> set().
            allocated_team_id_set (set(str), optional):
                Basic parameter.
                Set of allocated BaseTeam id.
                Defaults to None -> set().
            allocated_workplace_id_set (set(str), optional):
                Basic parameter.
                Set of allocated BaseWorkplace id.
                Defaults to None -> set().
            parent_workflow_id (str, optional):
                Basic parameter.
                Parent workflow id.
                Defaults to None.
            workplace_priority_rule (WorkplacePriorityRuleMode, optional):
                Workplace priority rule for simulation.
                Defaults to WorkplacePriorityRuleMode.FSS.
            worker_priority_rule (ResourcePriorityRule, optional):
                Worker priority rule for simulation.
                Defaults to ResourcePriorityRule.SSP.
            facility_priority_rule (ResourcePriorityRule, optional):
                Task priority rule for simulation.
                Defaults to TaskPriorityRule.TSLACK.
            need_facility (bool, optional):
                Basic parameter.
                Whether one facility is needed for performing this task or not.
                Defaults to False
            target_component_id (str, optional):
                Basic parameter.
                Target BaseComponent id.
                Defaults to None.
            default_progress (float, optional):
                Basic parameter.
                Progress before starting simulation (0.0 ~ 1.0)
                Defaults to None -> 0.0.
            due_time (int, optional):
                Basic parameter.
                Defaults to None -> int(-1).
            auto_task (bool, optional):
                Basic parameter.
                If True, this task is performed automatically
                even if there are no allocated workers.
                Defaults to False.
            fixing_allocating_worker_id_set (set(str), optional):
                Basic parameter.
                Allocating worker ID set for fixing allocation in simulation.
                Defaults to None.
            fixing_allocating_facility_id_set (set(str), optional):
                Basic parameter.
                Allocating facility ID set for fixing allocation in simulation.
                Defaults to None.
            est (float, optional):
                Basic variable.
                Earliest start time of CPM. This will be updated step by step.
                Defaults to 0.0.
            eft (float, optional):
                Basic variable.
                Earliest finish time of CPM. This will be updated step by step.
                Defaults to 0.0.
            lst (float, optional):
                Basic variable.
                Latest start time of CPM. This will be updated step by step.
                Defaults to -1.0.
            lft (float, optional):
                Basic variable.
                Latest finish time of CPM. This will be updated step by step.
                Defaults to -1.0.
            remaining_work_amount (float, optional):
                Basic variable.
                Remaining workamount in simulation.
                Defaults to None -> default_work_amount * (1.0 - default_progress).
            remaining_work_amount_record_list (List[float], optional):
                Basic variable.
                Record of remaining workamount in simulation.
                Defaults to None -> [].
            state (BaseTaskState, optional):
                Basic variable.
                State of this task in simulation.
                Defaults to BaseTaskState.NONE.
            state_record_list (List[BaseTaskState], optional):
                Basic variable.
                Record list of state.
                Defaults to None -> [].
            allocated_worker_facility_id_tuple_set (set(tuple(str, str)), optional):
                Basic variable.
                State of allocating worker and facility id tuple set in simulation.
                Defaults to None -> set().
            allocated_worker_facility_id_tuple_set_record_list (List[set[tuple(str, str)]], optional):
                Basic variable.
                State of allocating worker and facility id tuple set in simulation.
                Defaults to None -> [].
            additional_work_amount (float, optional):
                Advanced parameter.
                Defaults to None.
            additional_task_flag (bool, optional):
                Advanced variable.
                Defaults to False.
            actual_work_amount (float, optional):
                Advanced variable.
                Default to None -> default_work_amount*(1.0-default_progress)
        """
        task = BaseTask(
            name=name,
            ID=ID,
            default_work_amount=default_work_amount,
            work_amount_progress_of_unit_step_time=work_amount_progress_of_unit_step_time,
            input_task_id_dependency_set=input_task_id_dependency_set,
            allocated_team_id_set=allocated_team_id_set,
            allocated_workplace_id_set=allocated_workplace_id_set,
            parent_workflow_id=parent_workflow_id,
            workplace_priority_rule=workplace_priority_rule,
            worker_priority_rule=worker_priority_rule,
            facility_priority_rule=facility_priority_rule,
            need_facility=need_facility,
            target_component_id=target_component_id if target_component_id else self.ID,
            default_progress=default_progress,
            due_time=due_time,
            auto_task=auto_task,
            fixing_allocating_worker_id_set=fixing_allocating_worker_id_set,
            fixing_allocating_facility_id_set=fixing_allocating_facility_id_set,
            # Basic variables
            est=est,
            eft=eft,
            lst=lst,
            lft=lft,
            remaining_work_amount=remaining_work_amount,
            remaining_work_amount_record_list=remaining_work_amount_record_list,
            state=state,
            state_record_list=state_record_list,
            allocated_worker_facility_id_tuple_set=allocated_worker_facility_id_tuple_set,
            allocated_worker_facility_id_tuple_set_record_list=allocated_worker_facility_id_tuple_set_record_list,
            # Advanced parameters for customized simulation
            additional_work_amount=additional_work_amount,
            # Advanced variables for customized simulation
            additional_task_flag=additional_task_flag,
            actual_work_amount=actual_work_amount,
        )
        self.add_targeted_task(task)
        return task

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable basic variables of BaseComponent.

        If `state_info` is True, the following attributes are initialized.

          - `state`
          - `placed_workplace`
          - `error`


        If `log_info` is True, the following attributes are initialized.

          - `state_record_list`
          - `placed_workplace_id_record_list`

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaults to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
            check_task_state (bool):
                Check the state of each task in this component or not.
                Defaults to True.
        """
        if log_info:
            self.state_record_list = []
            self.placed_workplace_id_record_list = []

        if state_info:
            self.state = BaseComponentState.NONE
            self.placed_workplace_id = None
            self.error = 0.0

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
        self.placed_workplace_id_record_list = self.placed_workplace_id_record_list[
            ::-1
        ]

    def record_placed_workplace_id(self):
        """Record workplace id in this time to `placed_workplace_id_record_list`."""
        record = None
        if self.placed_workplace_id is not None:
            record = self.placed_workplace_id
        self.placed_workplace_id_record_list.append(record)

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
                self.placed_workplace_id_record_list.pop(step_time)
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
                    self.placed_workplace_id_record_list.insert(step_time, None)
                    self.state_record_list.insert(step_time, BaseComponentState.NONE)
                else:
                    self.placed_workplace_id_record_list.insert(
                        step_time,
                        self.placed_workplace_id_record_list[step_time - 1],
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
        - state_record_list[target_step_time]
        - placed_workplace_id_record_list[target_step_time]

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        print(
            self.ID,
            self.name,
            self.state_record_list[target_step_time],
            self.placed_workplace_id_record_list[target_step_time],
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
        return f"{self.name}"

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
            child_component_id_set=list(self.child_component_id_set),
            targeted_task_id_set=list(self.targeted_task_id_set),
            space_size=self.space_size,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            placed_workplace_id=(
                self.placed_workplace_id
                if self.placed_workplace_id is not None
                else None
            ),
            placed_workplace_id_record_list=self.placed_workplace_id_record_list,
        )
        return dict_json_data

    def get_time_list_for_gantt_chart(self, finish_margin=1.0):
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
        time = -1  # Initialize before loop
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
                See: https://mermaid.js.org/syntax/flowchart.html#direction
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

    def get_gantt_mermaid_data(
        self,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get gantt mermaid data of this component.
        Args:
            range_time (tuple[int, int], optional):
                Range time of gantt chart.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                If True, detailed information is included in gantt chart.
                Defaults to False.
            id_name_dict (dict[str, str], optional):
                Dictionary of ID and name for detailed information.
                Defaults to None.
        Returns:
            list[str]: List of lines for gantt mermaid diagram.
        """
        list_of_lines = []
        working_time_list = self.get_time_list_for_gantt_chart()[1]
        for start, duration in working_time_list:
            end = start + duration - 1
            if end < range_time[0] or start > range_time[1]:
                continue
            clipped_start = max(start, range_time[0])
            clipped_end = min(end + 1, range_time[1])

            text = self.name
            if (
                detailed_info is True
                and id_name_dict is not None
                and self.ID in id_name_dict
            ):
                placed_workplace_id = self.placed_workplace_id_record_list[
                    max(clipped_start - 1, 0)
                ]
                text = (
                    self.name + " @ " + id_name_dict[placed_workplace_id]
                    if placed_workplace_id is not None
                    else self.name
                )

            list_of_lines.append(f"{text}:{int(clipped_start)},{int(clipped_end)}")
        return list_of_lines
