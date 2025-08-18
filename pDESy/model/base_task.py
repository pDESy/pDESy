#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_task."""

import abc
import sys
import uuid
from enum import IntEnum

from .base_priority_rule import ResourcePriorityRuleMode, WorkplacePriorityRuleMode


class BaseTaskState(IntEnum):
    """BaseTaskState."""

    NONE = 0
    READY = 1
    WORKING = 2
    WORKING_ADDITIONALLY = 3
    FINISHED = -1


class BaseTaskDependency(IntEnum):
    """BaseTaskDependency."""

    FS = 0  # Finish to Start
    SS = 1  # Start to Start
    FF = 2  # Finish to Finish
    SF = 3  # Finish to Start


class BaseTask(object, metaclass=abc.ABCMeta):
    """BaseTask.

    BaseTask class for expressing target workflow.
    This class will be used as template.

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

    def __init__(
        self,
        # Basic parameters
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
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Task"
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.default_work_amount = (
            default_work_amount if default_work_amount is not None else 10.0
        )
        self.work_amount_progress_of_unit_step_time = (
            work_amount_progress_of_unit_step_time
            if work_amount_progress_of_unit_step_time is not None
            else 1.0
        )
        self.input_task_id_dependency_set = (
            input_task_id_dependency_set
            if input_task_id_dependency_set is not None
            else set()
        )
        self.allocated_team_id_set = (
            allocated_team_id_set if allocated_team_id_set is not None else set()
        )
        self.allocated_workplace_id_set = (
            allocated_workplace_id_set
            if allocated_workplace_id_set is not None
            else set()
        )
        self.parent_workflow_id = (
            parent_workflow_id if parent_workflow_id is not None else None
        )
        self.workplace_priority_rule = (
            workplace_priority_rule
            if workplace_priority_rule is not None
            else WorkplacePriorityRuleMode.FSS
        )
        self.worker_priority_rule = (
            worker_priority_rule
            if worker_priority_rule is not None
            else ResourcePriorityRuleMode.SSP
        )
        self.facility_priority_rule = (
            facility_priority_rule
            if facility_priority_rule is not None
            else ResourcePriorityRuleMode.SSP
        )
        self.need_facility = need_facility
        self.target_component_id = (
            target_component_id if target_component_id is not None else None
        )
        self.default_progress = (
            default_progress if default_progress is not None else 0.0
        )
        self.due_time = due_time if due_time is not None else int(-1)
        self.auto_task = auto_task if auto_task is not False else False
        self.fixing_allocating_worker_id_set = (
            fixing_allocating_worker_id_set
            if fixing_allocating_worker_id_set is not None
            else None
        )
        self.fixing_allocating_facility_id_set = (
            fixing_allocating_facility_id_set
            if fixing_allocating_facility_id_set is not None
            else None
        )
        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        self.est = est if est != 0.0 else 0.0  # Earliest start time
        self.eft = eft if eft != 0.0 else 0.0  # Earliest finish time
        self.lst = lst if lst != 0.0 else -1.0  # Latest start time
        self.lft = lft if lft != 0.0 else -1.0  # Latest finish time
        if remaining_work_amount is not None:
            self.remaining_work_amount = remaining_work_amount
        else:
            self.remaining_work_amount = self.default_work_amount * (
                1.0 - self.default_progress
            )

        if remaining_work_amount_record_list is not None:
            self.remaining_work_amount_record_list = remaining_work_amount_record_list
        else:
            self.remaining_work_amount_record_list = []

        if state is not BaseTaskState.NONE:
            self.state = state
        else:
            self.state = BaseTaskState.NONE

        if state_record_list is not None:
            self.state_record_list = state_record_list
        else:
            self.state_record_list = []

        if allocated_worker_facility_id_tuple_set is not None:
            self.allocated_worker_facility_id_tuple_set = (
                allocated_worker_facility_id_tuple_set
            )
        else:
            self.allocated_worker_facility_id_tuple_set = set()

        if allocated_worker_facility_id_tuple_set_record_list is not None:
            self.allocated_worker_facility_id_tuple_set_record_list = (
                allocated_worker_facility_id_tuple_set_record_list
            )
        else:
            self.allocated_worker_facility_id_tuple_set_record_list = []

        # --
        # Advanced parameter for customized simulation
        self.additional_work_amount = (
            additional_work_amount if additional_work_amount is not None else 0.0
        )
        # --
        # Advanced variables for customized simulation
        if additional_task_flag is not False:
            self.additional_task_flag = additional_task_flag
        else:
            self.additional_task_flag = False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )

    def __str__(self):
        """str.

        Returns:
            str: name of BaseTask
        Examples:
            >>> task = BaseTask("task1")
            >>> print(task)
            'task1'
        """
        return f"{self.name}"

    def export_dict_json_data(self):
        """
        Export the information of this task to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
            default_work_amount=self.default_work_amount,
            work_amount_progress_of_unit_step_time=self.work_amount_progress_of_unit_step_time,
            input_task_id_dependency_set=[
                [task_id, int(dependency)]
                for (task_id, dependency) in self.input_task_id_dependency_set
            ],
            allocated_team_id_set=list(self.allocated_team_id_set),
            allocated_workplace_id_set=list(self.allocated_workplace_id_set),
            need_facility=self.need_facility,
            target_component_id=(
                self.target_component_id
                if self.target_component_id is not None
                else None
            ),
            default_progress=self.default_progress,
            due_time=self.due_time,
            auto_task=self.auto_task,
            fixing_allocating_worker_id_set=(
                list(self.fixing_allocating_worker_id_set)
                if self.fixing_allocating_worker_id_set is not None
                else None
            ),
            fixing_allocating_facility_id_set=(
                list(self.fixing_allocating_facility_id_set)
                if self.fixing_allocating_facility_id_set is not None
                else None
            ),
            est=self.est,
            eft=self.eft,
            lst=self.lst,
            lft=self.lft,
            remaining_work_amount=self.remaining_work_amount,
            remaining_work_amount_record_list=[
                float(rwa) for rwa in self.remaining_work_amount_record_list
            ],
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            allocated_worker_facility_id_tuple_set=[
                [worker_id, facility_id]
                for (
                    worker_id,
                    facility_id,
                ) in self.allocated_worker_facility_id_tuple_set
            ],
            allocated_worker_facility_id_tuple_set_record_list=[
                [
                    [worker_id, facility_id]
                    for (
                        worker_id,
                        facility_id,
                    ) in allocated_worker_facility_id_tuple_set
                ]
                for allocated_worker_facility_id_tuple_set in self.allocated_worker_facility_id_tuple_set_record_list
            ],
        )
        return dict_json_data

    def append_input_task_dependency(
        self, input_task, task_dependency_mode=BaseTaskDependency.FS
    ):
        """
        Append input task to `input_task_id_dependency_set`.

        Args:
            input_task (BaseTask):
                Input BaseTask
            task_dependency_mode (BaseTaskDependency, optional):
                Task Dependency mode between input_task to this task.
                Default to BaseTaskDependency.FS
        """
        self.input_task_id_dependency_set.add((input_task.ID, task_dependency_mode))
        input_task.parent_workflow_id = self.parent_workflow_id

    def extend_input_task_list(
        self, input_task_list, input_task_dependency_mode=BaseTaskDependency.FS
    ):
        """
        Extend the set of input tasks and FS dependency to `input_task_id_dependency_set`.

        Args:
            input_task_id_dependency_set (set(tuple(str, BaseTask))):
                Set of input BaseTask and type of dependency(FS, SS, SF, F/F).
        """
        for input_task in input_task_list:
            self.input_task_id_dependency_set.add(
                (input_task.ID, input_task_dependency_mode)
            )
            input_task.parent_workflow_id = self.parent_workflow_id

    def initialize(self, error_tol=1e-10, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseTask.

        If `state_info` is True, the following attributes are initialized.

          - `est`
          - `eft`
          - `lst`
          - `lft`
          - `remaining_work_amount`
          - `state`
          - `allocated_worker_facility_id_tuple_set`
          - `additional_task_flag`
          - `actual_work_amount`

        If `log_info` is True the following attributes are initialized.

            - `remaining_work_amount_record_list`
            - `state_record_list`
            - `allocated_worker_facility_id_tuple_set_record_list`

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaults to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
            error_tol (float):
                error toleration of work amount for checking the state of this task.
                Defaults to 1e-10.
        """
        if state_info:
            self.est = 0.0  # Earliest start time
            self.eft = 0.0  # Earliest finish time
            self.lst = -1.0  # Latest start time
            self.lft = -1.0  # Latest finish time
            self.remaining_work_amount = self.default_work_amount * (
                1.0 - self.default_progress
            )
            self.state = BaseTaskState.NONE
            self.allocated_worker_facility_id_tuple_set = set()
            self.additional_task_flag = False
            self.actual_work_amount = self.default_work_amount * (
                1.0 - self.default_progress
            )
        if log_info:
            self.remaining_work_amount_record_list = []
            self.state_record_list = []
            self.allocated_worker_facility_id_tuple_set_record_list = []

        if state_info and log_info:
            if self.default_progress >= (1.00 - error_tol):
                self.state = BaseTaskState.FINISHED

    def record_allocated_workers_facilities_id(self):
        """
        Record allocated worker & facilities id.
        """
        self.allocated_worker_facility_id_tuple_set_record_list.append(
            self.allocated_worker_facility_id_tuple_set
        )

    def record_state(self, working=True):
        """Record current 'state' in 'state_record_list'."""
        if working:
            self.state_record_list.append(self.state)
        else:
            if self.state == BaseTaskState.WORKING:
                self.state_record_list.append(BaseTaskState.READY)
            else:
                self.state_record_list.append(self.state)

    def record_remaining_work_amount(self):
        """Record current `remaining_work_amount`."""
        self.remaining_work_amount_record_list.append(self.remaining_work_amount)

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.remaining_work_amount_record_list = self.remaining_work_amount_record_list[
            ::-1
        ]
        self.state_record_list = self.state_record_list[::-1]
        self.allocated_worker_facility_id_tuple_set_record_list = (
            self.allocated_worker_facility_id_tuple_set_record_list[::-1]
        )

    def get_state_from_record(self, time: int):
        """
        Get the state information in time.

        Args:
            time (int):
                target simulation time

        Returns:
            BaseTaskState: Task State information.
        """
        return self.state_record_list[time]

    def remove_absence_time_list(self, absence_time_list):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.state_record_list):
                self.remaining_work_amount_record_list.pop(step_time)
                self.allocated_worker_facility_id_tuple_set_record_list.pop(step_time)
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
                    self.remaining_work_amount_record_list.insert(
                        self.default_work_amount * (1.0 - self.default_progress)
                    )
                    self.allocated_worker_facility_id_tuple_set_record_list.insert(
                        step_time, None
                    )
                    self.state_record_list.insert(step_time, BaseTaskState.NONE)
                else:
                    self.remaining_work_amount_record_list.insert(
                        step_time, self.remaining_work_amount_record_list[step_time - 1]
                    )
                    self.allocated_worker_facility_id_tuple_set_record_list.insert(
                        step_time,
                        self.allocated_worker_facility_id_tuple_set_record_list[
                            step_time - 1
                        ],
                    )

                    insert_state_before = self.state_record_list[step_time - 1]
                    insert_state_after = self.state_record_list[step_time]
                    if insert_state_before == BaseTaskState.WORKING:
                        if insert_state_after == BaseTaskState.FINISHED:
                            insert_state = BaseTaskState.FINISHED
                        else:
                            insert_state = BaseTaskState.READY
                        self.state_record_list.insert(step_time, insert_state)
                    elif (
                        insert_state_before == BaseTaskState.NONE
                        and insert_state_after == BaseTaskState.WORKING
                    ):
                        self.state_record_list.insert(step_time, BaseTaskState.READY)
                    else:
                        self.state_record_list.insert(
                            step_time, self.state_record_list[step_time - 1]
                        )

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time` as follows:

        - ID
        - name
        - default_work_amount
        - remaining_work_amount_record_list
        - state_record_list[target_step_time]
        - allocated_worker_facility_id_tuple_set_record_list[target_step_time]

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        print(
            self.ID,
            self.name,
            self.default_work_amount,
            max(self.remaining_work_amount_record_list[target_step_time], 0.0),
            self.state_record_list[target_step_time],
            self.allocated_worker_facility_id_tuple_set_record_list[target_step_time],
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
        previous_state = BaseTaskState.NONE
        from_time = -1
        to_time = -1
        time = -1
        for time, state in enumerate(self.state_record_list):
            if state != previous_state:
                if from_time == -1:
                    from_time = time
                elif to_time == -1:
                    to_time = time
                    if state == BaseTaskState.NONE or state == BaseTaskState.FINISHED:
                        if previous_state == BaseTaskState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                        elif previous_state == BaseTaskState.READY:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseTaskState.READY:
                        if previous_state == BaseTaskState.WORKING:
                            working_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    if state == BaseTaskState.WORKING:
                        if previous_state == BaseTaskState.READY:
                            ready_time_list.append(
                                (from_time, (to_time - 1) - from_time + finish_margin)
                            )
                    from_time = time
                    to_time = -1
            previous_state = state

        # Suspended because of max time limitation
        if from_time > -1 and to_time == -1:
            if previous_state == BaseTaskState.WORKING:
                working_time_list.append((from_time, time - from_time + finish_margin))
            elif previous_state == BaseTaskState.READY:
                ready_time_list.append((from_time, time - from_time + finish_margin))

        # Append dummy values (0, 0) to the lists if they are empty.
        # This ensures that the Gantt chart generation process has valid data to work with,
        # even if no actual time intervals were recorded. Without this, downstream code
        # might encounter errors or render incomplete charts.
        if len(ready_time_list) == 0:
            ready_time_list.append((0, 0))
        if len(working_time_list) == 0:
            working_time_list.append((0, 0))

        return ready_time_list, working_time_list

    def get_mermaid_diagram(
        self,
        shape: str = "rect",
        print_work_amount_info: bool = True,
        subgraph: bool = False,
        subgraph_name: str = "Task",
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this task.

        Args:
            shape (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Subgraph name.
                Defaults to "Product".
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
        node_label = self.name
        if print_work_amount_info:
            node_label += f"<br>{self.remaining_work_amount}"
        list_of_lines.append(f"{self.ID}@{{shape: {shape}, label: '{node_label}'}}")

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        shape: str = "rect",
        print_work_amount_info: bool = True,
        subgraph: bool = False,
        subgraph_name: str = "Task",
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this task.

        Args:
            orientations (str, optional):
                Orientation of mermaid diagram.
                See: https://mermaid.js.org/syntax/flowchart.html#direction
                Defaults to "LR".
            shape (str, optional):
                Shape of mermaid diagram.
                Defaults to "rect".
            print_work_amount_info (bool, optional):
                Print work amount information or not.
                Defaults to True.
            subgraph (bool, optional):
                Subgraph or not.
                Defaults to False.
            subgraph_name (str, optional):
                Subgraph name.
                Defaults to "Task".
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_mermaid_diagram(
            shape=shape,
            print_work_amount_info=print_work_amount_info,
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
        Get gantt mermaid data of this task.
        Args:
            range_time (tuple[int, int], optional):
                Range of gantt chart.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                If True, print detailed information.
                Defaults to False.
            id_name_dict (dict[str, str], optional):
                Dictionary to map ID to name.
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
                worker_facility_tuple_list = (
                    self.allocated_worker_facility_id_tuple_set_record_list[
                        clipped_start
                    ]
                )
                worker_id_list = [
                    worker_id
                    for worker_id, _ in worker_facility_tuple_list
                    if worker_id is not None
                ]
                worker_name_list = [
                    id_name_dict.get(worker_id, worker_id)
                    for worker_id in worker_id_list
                ]
                facility_id_list = [
                    facility_id
                    for _, facility_id in worker_facility_tuple_list
                    if facility_id is not None
                ]
                facility_name_list = [
                    id_name_dict.get(facility_id, facility_id)
                    for facility_id in facility_id_list
                ]

                combined_name_list = []
                max_length = max(len(worker_name_list), len(facility_name_list))
                for i in range(max_length):
                    worker_name = (
                        worker_name_list[i] if i < len(worker_name_list) else ""
                    )
                    facility_name = (
                        facility_name_list[i] if i < len(facility_name_list) else ""
                    )

                    if worker_name and facility_name:
                        combined_name_list.append(f"{worker_name}-{facility_name}")
                    elif worker_name:
                        combined_name_list.append(worker_name)
                    elif facility_name:
                        combined_name_list.append(facility_name)

                if combined_name_list:
                    text = f"{self.name} * {'&'.join(combined_name_list)}"

            list_of_lines.append(f"{text}:{int(clipped_start)},{int(clipped_end)}")
        return list_of_lines
