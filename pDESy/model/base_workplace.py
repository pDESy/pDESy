#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_workplace."""

import abc
import datetime
import sys
import uuid
import warnings

import numpy as np
import matplotlib.pyplot as plt

import plotly.figure_factory as ff
import plotly.graph_objects as go

from pDESy.model.base_task import BaseTask

from .base_facility import BaseFacility, BaseFacilityState


class BaseWorkplace(object, metaclass=abc.ABCMeta):
    """BaseWorkplace.

    BaseWorkplace class for expressing workplace including facilities in a project.
    This class will be used as template.

    Args:
        name (str, optional):
            Basic parameter.
            Name of this workplace.
            Defaults to None -> "New Workplace"
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None -> str(uuid.uuid4()).
        facility_set (set[BaseFacility], optional):
            Basic parameter.
            List of BaseFacility who belong to this workplace.
            Defaults to None -> set().
        targeted_task_id_set (set(str), optional):
            Basic parameter.
            Targeted BaseTasks id set.
            Defaults to None -> set().
        parent_workplace_id (str, optional):
            Basic parameter.
            Parent workplace id of this workplace.
            Defaults to None.
        max_space_size (float, optional):
            Basic parameter
            Max size of space for placing components
            Default to None -> 1.0
        input_workplace_id_set (set(str), optional):
            Basic parameter.
            Input BaseWorkplace id set.
            Defaults to None -> set().
        available_space_size (float, optional):
            Basic variable.
            Available space size in this workplace.
            Defaults to None -> max_space_size.
        placed_component_id_set (set(str), optional):
            Basic variable.
            Components id which places to this workplace in simulation.
            Defaults to None -> set().
        placed_component_id_set_record_list(List[List[str]], optional):
            Basic variable.
            Record of placed components ID in simulation.
            Defaults to None -> [].
        cost_record_list (List[float], optional):
            Basic variable.
            History or record of this workplace's cost in simulation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name=None,
        ID=None,
        facility_set=None,
        targeted_task_id_set=None,
        parent_workplace_id=None,
        max_space_size=None,
        input_workplace_id_set=None,
        # Basic variables
        available_space_size=None,
        cost_record_list=None,
        placed_component_id_set=None,
        placed_component_id_set_record_list=None,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Workplace"
        self.ID = ID if ID is not None else str(uuid.uuid4())

        self.facility_set = facility_set if facility_set is not None else set()
        for facility in self.facility_set:
            if facility.workplace_id is None:
                facility.workplace_id = self.ID

        self.targeted_task_id_set = (
            targeted_task_id_set if targeted_task_id_set is not None else set()
        )
        self.parent_workplace_id = (
            parent_workplace_id if parent_workplace_id is not None else None
        )
        self.max_space_size = max_space_size if max_space_size is not None else np.inf

        self.input_workplace_id_set = (
            input_workplace_id_set if input_workplace_id_set is not None else set()
        )

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if cost_record_list is not None:
            self.cost_record_list = cost_record_list
        else:
            self.cost_record_list = []

        if available_space_size is not None:
            self.available_space_size = available_space_size
        else:
            self.available_space_size = self.max_space_size

        if placed_component_id_set is not None:
            self.placed_component_id_set = placed_component_id_set
        else:
            self.placed_component_id_set = set()

        if placed_component_id_set_record_list is not None:
            self.placed_component_id_set_record_list = (
                placed_component_id_set_record_list
            )
        else:
            self.placed_component_id_set_record_list = []

    def set_parent_workplace(self, parent_workplace):
        """
        Set `parent_workplace`.

        Args:
            parent_workplace (BaseWorkplace):
                Parent workplace
        Examples:
            >>> t = BaseWorkplace('t')
            >>> t1 = BaseWorkplace('t1')
            >>> t.set_parent_workplace(t1)
            >>> print(t.parent_workplace.name)
            't1'
        """
        self.parent_workplace_id = parent_workplace.ID

    def add_facility(self, facility):
        """
        Add facility to `facility_set`.

        Args:
            facility (BaseFacility):
                Facility which is added to this workplace
        """
        facility.workplace_id = self.ID
        self.facility_set.add(facility)

    def get_total_workamount_skill(self, task_name, error_tol=1e-10):
        """
        Get total number of workamount skill of all facilities.

        By checking workamount_skill_mean_map.

        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.

        Returns:
            float: total workamount skill of target task name
        """
        sum_skill_point = 0.0
        for facility in self.facility_set:
            if facility.has_workamount_skill(task_name, error_tol=error_tol):
                sum_skill_point += facility.workamount_skill_mean_map[task_name]
        return sum_skill_point

    def extend_targeted_task_list(self, targeted_task_list):
        """
        Extend the list of targeted tasks to `targeted_task_list`.

        Args:
            targeted_task_list (list[BaseTask]):
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
        Extend the set of targeted tasks to `targeted_task_id_set`.

        Args:
            targeted_task_set (Set(BaseTask)):
                Set of targeted tasks
        """
        for targeted_task in targeted_task_set:
            self.add_targeted_task(targeted_task)

    def append_targeted_task(self, targeted_task):
        """
        Append targeted task to `targeted_task_list`.
        TODO: This method is deprecated. Use `add_targeted_task` instead.

        Args:
            targeted_task (BaseTask):
                Targeted task
        """
        warnings.warn(
            "append_targeted_task is deprecated. Use add_targeted_task instead.",
            DeprecationWarning,
        )
        self.targeted_task_id_set.add(targeted_task.ID)
        targeted_task.allocated_workplace_id_set.add(self.ID)

    def add_targeted_task(self, targeted_task):
        """
        Add targeted task to `targeted_task_id_set`.

        Args:
            targeted_task (BaseTask):
                Targeted task
        """
        if not isinstance(targeted_task, BaseTask):
            raise TypeError(
                f"targeted_task must be BaseTask, but {type(targeted_task)}"
            )
        if targeted_task.ID in self.targeted_task_id_set:
            warnings.warn(
                f"Targeted task {targeted_task.ID} is already added to {self.ID}.",
                UserWarning,
            )
        else:
            self.targeted_task_id_set.add(targeted_task.ID)
            targeted_task.allocated_workplace_id_set.add(self.ID)

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseWorkplace.

        If `state_info` is True, the following attributes are initialized.

          - `placed_component_id_set`

        If `log_info` is True, the following attributes are initialized.
          - `cost_record_list`
          - `placed_component_id_set_record_list`

        BaseFacility in `facility_set` are also initialized by this function.

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaults to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        if state_info:
            self.placed_component_id_set = set()
            self.available_space_size = self.max_space_size
        if log_info:
            self.cost_record_list = []
            self.placed_component_id_set_record_list = []
        for w in self.facility_set:
            w.initialize(state_info=state_info, log_info=log_info)

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.cost_record_list = self.cost_record_list[::-1]
        self.placed_component_id_set_record_list = (
            self.placed_component_id_set_record_list[::-1]
        )
        for facility in self.facility_set:
            facility.reverse_log_information()

    def add_labor_cost(self, only_working=True, add_zero_to_all_facilities=False):
        """
        Add labor cost to facilities in this workplace.

        Args:
            only_working (bool, optional):
                If True, add labor cost to only WORKING facilities in this workplace.
                If False, add labor cost to all facilities in this workplace.
                Defaults to True.
            add_zero_to_all_facilities (bool, optional):
                If True, add 0 labor cost to all facilities in this workplace.
                If False, calculate labor cost normally.
                Defaults to False.

        Returns:
            float: Total labor cost of this workplace in this time.
        """
        cost_this_time = 0.0

        if add_zero_to_all_facilities:
            for facility in self.facility_set:
                facility.cost_record_list.append(0.0)

        else:
            if only_working:
                for facility in self.facility_set:
                    if facility.state == BaseFacilityState.WORKING:
                        facility.cost_record_list.append(facility.cost_per_time)
                        cost_this_time += facility.cost_per_time
                    else:
                        facility.cost_record_list.append(0.0)

            else:
                for facility in self.facility_set:
                    facility.cost_record_list.append(facility.cost_per_time)
                    cost_this_time += facility.cost_per_time

        self.cost_record_list.append(cost_this_time)
        return cost_this_time

    def record_assigned_task_id(self):
        """Record assigned task id."""
        for f in self.facility_set:
            f.record_assigned_task_id()

    def record_placed_component_id(self):
        """Record component id list to `placed_component_id_set_record_list`."""
        record = {}
        if len(self.placed_component_id_set) > 0:
            record = self.placed_component_id_set

        self.placed_component_id_set_record_list.append(record)

    def record_all_facility_state(self, working=True):
        """Record state of all facilities."""
        for facility in self.facility_set:
            facility.record_state(working=working)

    def __str__(self):
        """str.

        Returns:
            str: name of BaseWorkplace
        Examples:
            >>> workplace = BaseWorkplace("workplace")
            >>> print(workplace)
            'workplace'
        """
        return f"{self.name}"

    def export_dict_json_data(self):
        """
        Export the information of this workplace to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
            facility_set=[f.export_dict_json_data() for f in self.facility_set],
            targeted_task_id_set=list(self.targeted_task_id_set),
            parent_workplace_id=(
                self.parent_workplace_id
                if self.parent_workplace_id is not None
                else None
            ),
            max_space_size=self.max_space_size,
            input_workplace_id_set=list(self.input_workplace_id_set),
            cost_record_list=self.cost_record_list,
            placed_component_id_set=list(self.placed_component_id_set),
            placed_component_id_set_record_list=[
                list(record) for record in self.placed_component_id_set_record_list
            ],
        )
        return dict_json_data

    def read_json_data(self, json_data):
        """
        Read the JSON data to populate the attributes of a BaseWorkplace instance.

        Args:
            json_data (dict): JSON data containing the attributes of the workplace.
        """
        self.name = json_data["name"]
        self.ID = json_data["ID"]
        self.facility_set = set()
        for w in json_data["facility_set"]:
            facility = BaseFacility(
                name=w["name"],
                ID=w["ID"],
                workplace_id=w["workplace_id"],
                cost_per_time=w["cost_per_time"],
                solo_working=w["solo_working"],
                workamount_skill_mean_map=w["workamount_skill_mean_map"],
                workamount_skill_sd_map=w["workamount_skill_sd_map"],
                absence_time_list=w["absence_time_list"],
                state=BaseFacilityState(w["state"]),
                state_record_list=[
                    BaseFacilityState(state_num) for state_num in w["state_record_list"]
                ],
                cost_record_list=w["cost_record_list"],
                assigned_task_worker_id_tuple_set=set(
                    w["assigned_task_worker_id_tuple_set"]
                ),
                assigned_task_worker_id_tuple_set_record_list=w[
                    "assigned_task_worker_id_tuple_set_record_list"
                ],
            )
            self.facility_set.add(facility)
        self.targeted_task_id_set = set(json_data["targeted_task_id_set"])
        self.parent_workplace_id = json_data["parent_workplace_id"]
        self.max_space_size = json_data["max_space_size"]
        self.input_workplace_id_set = json_data["input_workplace_id_set"]
        # Basic variables
        self.cost_record_list = json_data["cost_record_list"]
        self.placed_component_id_set = json_data["placed_component_id_set"]
        self.placed_component_id_set_record_list = json_data[
            "placed_component_id_set_record_list"
        ]

    def extract_free_facility_set(self, target_time_list):
        """
        Extract FREE facility list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract free facility from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseFacility]: List of BaseFacility
        """
        return self.__extract_state_facility_set(
            target_time_list, BaseFacilityState.FREE
        )

    def extract_working_facility_set(self, target_time_list):
        """
        Extract WORKING facility list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract working facility from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseFacility]: List of BaseFacility
        """
        return self.__extract_state_facility_set(
            target_time_list, BaseFacilityState.WORKING
        )

    def __extract_state_facility_set(self, target_time_list, target_state):
        """
        Extract state facility list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract target_state facility from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
            target_state (BaseFacilityState):
                Target state.
        Returns:
            List[BaseFacility]: List of BaseFacility
        """
        facility_set = set()
        for facility in self.facility_set:
            extract_flag = True
            for time in target_time_list:
                if len(facility.state_record_list) <= time:
                    extract_flag = False
                    break
                if facility.state_record_list[time] != target_state:
                    extract_flag = False
                    break
            if extract_flag:
                facility_set.add(facility)
        return facility_set

    def get_facility_set(
        self,
        name=None,
        ID=None,
        workplace_id=None,
        cost_per_time=None,
        solo_working=None,
        workamount_skill_mean_map=None,
        workamount_skill_sd_map=None,
        state=None,
        cost_record_list=None,
        assigned_task_worker_id_tuple_set=None,
        assigned_task_worker_id_tuple_set_record_list=None,
    ):
        """
        Get facility list by using search conditions related to BaseFacility parameter.

        If there is no searching condition, this function returns all self.facility_set.

        Args:
            name (str, optional):
                Target facility name.
                Defaults to None.
            ID (str, optional):
                Target facility ID.
                Defaults to None.
            workplace_id (str, optional):
                Target facility workplace_id.
                Defaults to None.
            cost_per_time (float, optional):
                Target facility cost_per_time.
                Defaults to None.
            solo_working (bool, optional):
                Target facility solo_working.
                Defaults to None.
            workamount_skill_mean_map (Dict[str, float], optional):
                Target facility workamount_skill_mean_map.
                Defaults to None.
            workamount_skill_sd_map (Dict[str, float], optional):
                Target facility workamount_skill_sd_map.
                Defaults to None.
            state (BaseFacilityState, optional):
                Target facility state.
                Defaults to None.
            cost_record_list (List[float], optional):
                Target facility cost_record_list.
                Defaults to None.
            assigned_task_worker_id_tuple_set (set[str], optional):
                Target facility assigned_task_worker_id_tuple_set.
                Defaults to None.
            assigned_task_worker_id_tuple_set_record_list (List[List[str]], optional):
                Target facility assigned_task_worker_id_tuple_set_record_list.
                Defaults to None.

        Returns:
            List[BaseFacility]: List of BaseFacility.
        """
        facility_set = self.facility_set
        if name is not None:
            facility_set = {x for x in facility_set if x.name == name}
        if ID is not None:
            facility_set = {x for x in facility_set if x.ID == ID}
        if workplace_id is not None:
            facility_set = {x for x in facility_set if x.workplace_id == workplace_id}
        if cost_per_time is not None:
            facility_set = {x for x in facility_set if x.cost_per_time == cost_per_time}
        if solo_working is not None:
            facility_set = {x for x in facility_set if x.solo_working == solo_working}
        if workamount_skill_mean_map is not None:
            facility_set = {
                x
                for x in facility_set
                if x.workamount_skill_mean_map == workamount_skill_mean_map
            }
        if workamount_skill_sd_map is not None:
            facility_set = {
                x
                for x in facility_set
                if x.workamount_skill_sd_map == workamount_skill_sd_map
            }
        if state is not None:
            facility_set = {x for x in facility_set if x.state == state}
        if cost_record_list is not None:
            facility_set = {
                x for x in facility_set if x.cost_record_list == cost_record_list
            }
        if assigned_task_worker_id_tuple_set is not None:
            facility_set = {
                x
                for x in facility_set
                if x.assigned_task_worker_id_tuple_set
                == assigned_task_worker_id_tuple_set
            }
        if assigned_task_worker_id_tuple_set_record_list is not None:
            facility_set = {
                x
                for x in facility_set
                if x.assigned_task_worker_id_tuple_set_record_list
                == assigned_task_worker_id_tuple_set_record_list
            }
        return facility_set

    def remove_absence_time_list(self, absence_time_list):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for facility in self.facility_set:
            facility.remove_absence_time_list(absence_time_list)
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.cost_record_list):
                self.cost_record_list.pop(step_time)

    def insert_absence_time_list(self, absence_time_list):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for facility in self.facility_set:
            facility.insert_absence_time_list(absence_time_list)
        for step_time in sorted(absence_time_list):
            self.cost_record_list.insert(step_time, 0.0)

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time`.

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        for facility in self.facility_set:
            facility.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward=False):
        """
        Print all log in chronological order.
        """
        if len(self.facility_set) > 0:
            sample_facility = next(iter(self.facility_set))
            for t in range(len(sample_facility.state_record_list)):
                print("TIME: ", t)
                if backward:
                    t = len(sample_facility.state_record_list) - 1 - t
                self.print_log(t)

    def check_update_state_from_absence_time_list(self, step_time):
        """
        Check and Update state of all resources to ABSENCE or FREE or WORKING.

        Args:
            step_time (int):
                Target step time of checking and updating state of facilities.
        """
        for facility in self.facility_set:
            facility.check_update_state_from_absence_time_list(step_time)

    def set_absence_state_to_all_facilities(self):
        """Set absence state to all facilities."""
        for facility in self.facility_set:
            facility.state = BaseFacilityState.ABSENCE

    def plot_simple_gantt(
        self,
        finish_margin=1.0,
        print_workplace_name=True,
        view_ready=False,
        facility_color="#D9E5FF",
        ready_color="#C0C0C0",
        figsize=None,
        dpi=100.0,
        save_fig_path=None,
    ):
        """
        Plot Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            print_workplace_name (bool, optional):
                Print workplace name or not.
                Defaults to True.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to True.
            facility_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            ready_color (str, optional):
                Ready color setting information.
                Defaults to "#C0C0C0".
            figsize ((float, float), optional):
                Width, height in inches.
                Default to None -> [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig, gnt = self.create_simple_gantt(
            finish_margin=finish_margin,
            print_workplace_name=print_workplace_name,
            view_ready=view_ready,
            facility_color=facility_color,
            ready_color=ready_color,
            figsize=figsize,
            dpi=dpi,
            save_fig_path=save_fig_path,
        )
        _ = gnt  # Unused variable, but needed for compatibility
        return fig

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        print_workplace_name=True,
        view_ready=False,
        view_absence=False,
        facility_color="#D9E5FF",
        ready_color="#DCDCDC",
        absence_color="#696969",
        figsize=None,
        dpi=100.0,
        save_fig_path=None,
    ):
        """
        Create Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            print_workplace_name (bool, optional):
                Print workplace name or not.
                Defaults to True.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            view_absence (bool, optional):
                View Absence time or not.
                Defaults to False.
            facility_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            ready_color (str, optional):
                Ready color setting information.
                Defaults to "#DCDCDC".
            absence_color (str, optional):
                Absence color setting information.
                Defaults to "#696969".
            figsize ((float, float), optional):
                Width, height in inches.
                Default to None -> [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
            gnt: ax in plt.subplots()
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig, gnt = plt.subplots()
        fig.figsize = figsize
        fig.dpi = dpi
        gnt.set_xlabel("step")
        gnt.grid(True)

        y_ticks = [10 * (n + 1) for n in range(len(self.facility_set))]
        y_tick_labels = [facility.name for facility in self.facility_set]
        if print_workplace_name:
            y_tick_labels = [
                f"{self.name}: {facility.name}" for facility in self.facility_set
            ]

        gnt.set_yticks(y_ticks)
        gnt.set_yticklabels(y_tick_labels)

        for time, w in enumerate(self.facility_set):
            (
                ready_time_list,
                working_time_list,
                absence_time_list,
            ) = w.get_time_list_for_gantt_chart(finish_margin=finish_margin)
            if view_ready:
                gnt.broken_barh(
                    ready_time_list,
                    (y_ticks[time] - 5, 9),
                    facecolors=(ready_color),
                )
            if view_absence:
                gnt.broken_barh(
                    absence_time_list,
                    (y_ticks[time] - 5, 9),
                    facecolors=(absence_color),
                )
            gnt.broken_barh(
                working_time_list,
                (y_ticks[time] - 5, 9),
                facecolors=(facility_color),
            )
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig, gnt

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        print_workplace_name=True,
        view_ready=False,
        view_absence=False,
    ):
        """
        Create data for gantt plotly of BaseFacility in facility_set.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            print_workplace_name (bool, optional):
                Print workplace name or not.
                Defaults to True.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            view_absence (bool, optional):
                View ABSENCE time or not.
                Defaults to False.
        Returns:
            List[dict]: Gantt plotly information of this BaseWorkplace
        """
        df = []
        for facility in self.facility_set:
            (
                ready_time_list,
                working_time_list,
                absence_time_list,
            ) = facility.get_time_list_for_gantt_chart(finish_margin=finish_margin)

            task_name = facility.name
            if print_workplace_name:
                task_name = f"{self.name}: {facility.name}"

            if view_ready:
                for from_time, length in ready_time_list:
                    to_time = from_time + length
                    df.append(
                        {
                            "Task": task_name,
                            "Start": (
                                init_datetime + from_time * unit_timedelta
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "Finish": (
                                init_datetime + to_time * unit_timedelta
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "State": "READY",
                            "Type": "Facility",
                        }
                    )
            if view_absence:
                for from_time, length in absence_time_list:
                    to_time = from_time + length
                    df.append(
                        {
                            "Task": task_name,
                            "Start": (
                                init_datetime + from_time * unit_timedelta
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "Finish": (
                                init_datetime + to_time * unit_timedelta
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "State": "ABSENCE",
                            "Type": "Facility",
                        }
                    )
            for from_time, length in working_time_list:
                to_time = from_time + length
                df.append(
                    {
                        "Task": task_name,
                        "Start": (init_datetime + from_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Finish": (init_datetime + to_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "State": "WORKING",
                        "Type": "Facility",
                    }
                )
        return df

    def create_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        title="Gantt Chart",
        colors=None,
        index_col=None,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=True,
        show_colorbar=True,
        print_workplace_name=True,
        save_fig_path=None,
    ):
        """
        Create Gantt chart by plotly.

        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            title (str, optional):
                Title of Gantt chart.
                Defaults to "Gantt Chart".
            colors (Dict[str, str], optional):
                Color setting of plotly Gantt chart.
                Defaults to None.
                If None, default color setting will be used:
                {
                    "WORKING": "rgb(46, 137, 205)",
                    "READY": "rgb(220, 220, 220)",
                    "ABSENCE": "rgb(105, 105, 105)"
                }
            index_col (str, optional):
                index_col of plotly Gantt chart.
                Defaults to None -> "Type".
            showgrid_x (bool, optional):
                showgrid_x of plotly Gantt chart.
                Defaults to True.
            showgrid_y (bool, optional):
                showgrid_y of plotly Gantt chart.
                Defaults to True.
            group_tasks (bool, optional):
                group_tasks of plotly Gantt chart.
                Defaults to True.
            show_colorbar (bool, optional):
                show_colorbar of plotly Gantt chart.
                Defaults to True.
            print_workplace_name (bool, optional):
                Print workplace name or not.
                Defaults to True.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a gantt chart
        """
        colors = (
            colors
            if colors is not None
            else {
                "WORKING": "rgb(46, 137, 205)",
                "READY": "rgb(220, 220, 220)",
                "ABSENCE": "rgb(105, 105, 105)",
            }
        )
        index_col = index_col if index_col is not None else "State"
        df = self.create_data_for_gantt_plotly(
            init_datetime,
            unit_timedelta,
            print_workplace_name=print_workplace_name,
            view_ready=True,
            view_absence=True,
        )
        fig = ff.create_gantt(
            df,
            title=title,
            colors=colors,
            index_col=index_col,
            showgrid_x=showgrid_x,
            showgrid_y=showgrid_y,
            show_colorbar=show_colorbar,
            group_tasks=group_tasks,
        )
        if save_fig_path is not None:
            dot_point = save_fig_path.rfind(".")
            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            else:
                fig.write_image(save_fig_path)

        return fig

    def create_data_for_cost_history_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
    ):
        """
        Create data for cost history plotly from cost_record_list in facility_set.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation

        Returns:
            data (List[go.Bar(name, x, y)]: Information of cost history chart.
        """
        data = []
        x = [
            (init_datetime + time * unit_timedelta).strftime("%Y-%m-%d %H:%M:%S")
            for time in range(len(self.cost_record_list))
        ]
        for facility in self.facility_set:
            data.append(go.Bar(name=facility.name, x=x, y=facility.cost_record_list))
        return data

    def create_cost_history_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        title="Cost Chart",
        save_fig_path=None,
    ):
        """
        Create cost chart by plotly.

        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            title (str, optional):
                Title of cost chart.
                Defaults to "Cost Chart".
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a gantt chart
        """
        data = self.create_data_for_cost_history_plotly(init_datetime, unit_timedelta)
        fig = go.Figure(data)
        fig.update_layout(barmode="stack", title=title)
        if save_fig_path is not None:
            dot_point = save_fig_path.rfind(".")
            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            else:
                fig.write_image(save_fig_path)

        return fig

    def append_input_workplace(self, input_workplace):
        """
        Append input workplace to `input_workplace_id_set`.
        TODO: This method is deprecated. Use `add_input_workplace` instead.

        Args:
            input_workplace (BaseWorkplace):
                input workplace
        """
        warnings.warn(
            "append_input_workplace is deprecated. Use add_input_workplace instead.",
            DeprecationWarning,
        )
        self.input_workplace_id_set.add(input_workplace.ID)

    def add_input_workplace(self, input_workplace):
        """
        Add input workplace to `input_workplace_id_set`.

        Args:
            input_workplace (BaseWorkplace):
                input workplace
        """
        if not isinstance(input_workplace, BaseWorkplace):
            raise TypeError(
                f"input_workplace must be BaseWorkplace, but {type(input_workplace)}"
            )
        if input_workplace.ID in self.input_workplace_id_set:
            warnings.warn(
                f"Input workplace {input_workplace.ID} is already added to {self.ID}.",
                UserWarning,
            )
        else:
            self.input_workplace_id_set.add(input_workplace.ID)

    def extend_input_workplace_list(self, input_workplace_list):
        """
        Extend the list of input workplaces to `input_workplace_id_set`.
        TODO: This method is deprecated. Use `update_input_workplace_set` instead.
        Args:
            input_workplace_list (list[BaseWorkplace]):
                 List of input workplaces
        """
        warnings.warn(
            "extend_input_workplace_list is deprecated. Use update_input_workplace_set instead.",
            DeprecationWarning,
        )
        for input_workplace in input_workplace_list:
            self.append_input_workplace(input_workplace)

    def update_input_workplace_set(self, input_workplace_set):
        """
        Update the set of input workplaces to `input_workplace_id_set`.

        Args:
            input_workplace_set (set(BaseWorkplace)):
                 Set of input workplaces
        """
        for input_workplace in input_workplace_set:
            self.add_input_workplace(input_workplace)

    def get_target_facility_mermaid_diagram(
        self,
        target_facility_set: set[BaseFacility],
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of target facility.

        Args:
            target_facility_set (set[BaseFacility]):
                Set of target facilities.
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of facilities in this workplace.
                Defaults to "stadium".
            link_type_str (str, optional):
                Link type string.
                Defaults to "-->".
            subgraph (bool, optional):
                Whether to use subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        if print_facility:
            for facility in target_facility_set:
                if facility in self.facility_set:
                    list_of_lines.extend(
                        facility.get_mermaid_diagram(shape=shape_facility)
                    )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def get_mermaid_diagram(
        self,
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this workplace.

        Args:
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of facilities in this workplace.
                Defaults to "stadium".
            link_type_str (str, optional):
                Link type string.
                Defaults to "-->".
            subgraph (bool, optional):
                Whether to use subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        return self.get_target_facility_mermaid_diagram(
            target_facility_set=self.facility_set,
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def print_target_facility_mermaid_diagram(
        self,
        target_facility_set: set[BaseFacility],
        orientations: str = "LR",
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this workplace.

        Args:
            target_facility_set (set[BaseFacility]):
                Set of target facilities.
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of facilities in this workplace.
                Defaults to "stadium".
            link_type_str (str, optional):
                Link type string.
                Defaults to "-->".
            subgraph (bool, optional):
                Whether to use subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_facility_mermaid_diagram(
            target_facility_set=target_facility_set,
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        print_facility: bool = True,
        shape_facility: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this workplace.

        Args:
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            print_facility (bool, optional):
                Print facilities or not.
                Defaults to True.
            shape_facility (str, optional):
                Shape of facilities in this workplace.
                Defaults to "stadium".
            link_type_str (str, optional):
                Link type string.
                Defaults to "-->".
            subgraph (bool, optional):
                Whether to use subgraph or not.
                Defaults to True.
            subgraph_direction (str, optional):
                Direction of subgraph.
                Defaults to "LR".
        """
        self.print_target_facility_mermaid_diagram(
            target_facility_set=self.facility_set,
            orientations=orientations,
            print_facility=print_facility,
            shape_facility=shape_facility,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def get_gantt_mermaid(
        self,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get mermaid diagram of Gantt chart.
        Args:
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range of Gantt chart.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                If True, detailed information is included in gantt chart.
                Defaults to False.
            id_name_dict (dict[str, str], optional):
                Dictionary of ID and name for detailed information.
                Defaults to None.
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        if section:
            list_of_lines.append(f"section {self.name}")
        for facility in self.facility_set:
            list_of_lines.extend(
                facility.get_gantt_mermaid_data(
                    range_time=range_time,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_gantt_mermaid(
        self,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Print mermaid diagram of Gantt chart.
        Args:
            date_format (str, optional):
                Date format of mermaid diagram.
                Defaults to "X".
            axis_format (str, optional):
                Axis format of mermaid diagram.
                Defaults to "%s".
            section (bool, optional):
                Section or not.
                Defaults to True.
            range_time (tuple[int, int], optional):
                Range of Gantt chart.
                Defaults to (0, sys.maxsize).
            detailed_info (bool, optional):
                If True, detailed information is included in gantt chart.
                Defaults to False.
            id_name_dict (dict[str, str], optional):
                Dictionary of ID and name for detailed information.
                Defaults to None.
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_gantt_mermaid(
            section=section,
            range_time=range_time,
            detailed_info=detailed_info,
            id_name_dict=id_name_dict,
        )
        print(*list_of_lines, sep="\n")
