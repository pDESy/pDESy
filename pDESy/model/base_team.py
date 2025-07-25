#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_team."""

import abc
import datetime
import sys
import uuid
import warnings

import matplotlib.pyplot as plt

import plotly.figure_factory as ff
import plotly.graph_objects as go

from .base_worker import BaseWorker, BaseWorkerState


class BaseTeam(object, metaclass=abc.ABCMeta):
    """BaseTeam.

    BaseTeam class for expressing team in a project.
    This class will be used as template.

    Args:
        name (str, optional):
            Basic parameter.
            Name of this team.
            Defaults to None -> "New Team"
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None -> str(uuid.uuid4()).
        worker_list (List[BaseWorker], optional):
            Basic parameter.
            List of BaseWorkers who belong to this team.
            Defaults to None -> [].
        targeted_task_list (List[BaseTask], optional):
            Basic parameter.
            List of targeted BaseTasks.
            Defaults to None -> [].
        parent_team (BaseTeam, optional):
            Basic parameter.
            Parent team of this team.
            Defaults to None.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this team's cost in simulation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name=None,
        ID=None,
        worker_list=None,
        targeted_task_list=None,
        parent_team=None,
        # Basic variables
        cost_list=None,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Team"
        self.ID = ID if ID is not None else str(uuid.uuid4())

        self.worker_list = worker_list if worker_list is not None else []
        for worker in self.worker_list:
            if worker.team_id is None:
                worker.team_id = self.ID

        self.targeted_task_list = (
            targeted_task_list if targeted_task_list is not None else []
        )
        self.parent_team = parent_team if parent_team is not None else None

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if cost_list is not None:
            self.cost_list = cost_list
        else:
            self.cost_list = []

    def set_parent_team(self, parent_team):
        """
        Set parent team.

        Args:
            parent_team (BaseTeam):
                Parent team
        Examples:
            >>> t = BaseTeam('t')
            >>> t1 = BaseTeam('t1')
            >>> t.set_parent_team(t1)
            >>> print(t.parent_team.name)
            't1'
        """
        self.parent_team = parent_team

    def extend_targeted_task_list(self, targeted_task_list):
        """
        Extend the list of targeted tasks.

        Args:
            targeted_task_list (list[BaseTask]):
                List of targeted tasks
        Examples:
            >>> team = BaseTeam('team')
            >>> print([targeted_t.name for targeted_t in team.targeted_task_list])
            []
            >>> team.extend_targeted_task_list([BaseTask('t1'),BaseTask('t2')])
            >>> print([targeted_t.name for targeted_t in team.targeted_task_list])
            ['t1', 't2']
        """
        for targeted_task in targeted_task_list:
            self.append_targeted_task(targeted_task)

    def append_targeted_task(self, targeted_task):
        """
        Append targeted task.

        Args:
            targeted_task (BaseTask):
                Targeted task
        Examples:
            >>> team = BaseTeam('team')
            >>> print([targeted_t.name for targeted_t in team.targeted_task_list])
            []
            >>> t1 = BaseTask('t1')
            >>> team.append_targeted_task(t1)
            >>> print([targeted_t.name for targeted_t in team.targeted_task_list])
            ['t1']
            >>> print([target_team.name for target_team in t1.allocated_team_list])
            ['team']
        """
        self.targeted_task_list.append(targeted_task)
        targeted_task.allocated_team_list.append(self)

    def add_worker(self, worker):
        """
        Add worker to `worker_list`.

        Args:
            worker (BaseWorker):
                Worker which is added to this workplace
        """
        worker.team_id = self.ID
        self.worker_list.append(worker)

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseTeam.

        If `log_info` is True, the following attributes are initialized.

          - cost_list

        BaseWorker in `worker_list` are also initialized by this function.

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        if log_info:
            self.cost_list = []
        for w in self.worker_list:
            w.initialize(state_info=state_info, log_info=log_info)

    def reverse_log_information(self):
        """Reverse log information of all."""
        self.cost_list = self.cost_list[::-1]
        for w in self.worker_list:
            w.reverse_log_information()

    def add_labor_cost(self, only_working=True, add_zero_to_all_workers=False):
        """
        Add labor cost to workers in this team.

        Args:
            only_working (bool, optional):
                If True, add labor cost to only WORKING workers in this team.
                If False, add labor cost to all workers in this team.
                Defaults to True.
            add_zero_to_all_workers (bool, optional):
                If True, add 0 labor cost to all workers in this team.
                If False, calculate labor cost normally.
                Defaults to False.

        Returns:
            float: Total labor cost of this team in this time.
        """
        cost_this_time = 0.0

        if add_zero_to_all_workers:
            for worker in self.worker_list:
                worker.cost_list.append(0.0)

        else:
            if only_working:
                for worker in self.worker_list:
                    if worker.state == BaseWorkerState.WORKING:
                        worker.cost_list.append(worker.cost_per_time)
                        cost_this_time += worker.cost_per_time
                    else:
                        worker.cost_list.append(0.0)

            else:
                for worker in self.worker_list:
                    worker.cost_list.append(worker.cost_per_time)
                    cost_this_time += worker.cost_per_time

        self.cost_list.append(cost_this_time)
        return cost_this_time

    def record_assigned_task_id(self):
        """Record assigned task id in this time."""
        for worker in self.worker_list:
            worker.record_assigned_task_id()

    def record_all_worker_state(self, working=True):
        """Record the state of all workers by using BaseWorker.record_state()."""
        for worker in self.worker_list:
            worker.record_state(working=working)

    def __str__(self):
        """str.

        Returns:
            str: name of BaseTeam
        Examples:
            >>> team = BaseTeam("team")
            >>> print(team)
            'team'
        """
        return "{}".format(self.name)

    def export_dict_json_data(self):
        """
        Export the information of this team to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
            worker_list=[w.export_dict_json_data() for w in self.worker_list],
            targeted_task_list=[t.ID for t in self.targeted_task_list],
            parent_team=self.parent_team.ID if self.parent_team is not None else None,
            # Basic variables
            cost_list=self.cost_list,
        )
        return dict_json_data

    def read_json_data(self, json_data):
        """
        Read the JSON data for creating BaseTeam instance.

        Args:
            json_data (dict): JSON data.
        """
        self.name = json_data["name"]
        self.ID = json_data["ID"]
        self.worker_list = []
        for w in json_data["worker_list"]:
            worker = BaseWorker(
                name=w["name"],
                ID=w["ID"],
                team_id=w["team_id"],
                cost_per_time=w["cost_per_time"],
                solo_working=w["solo_working"],
                workamount_skill_mean_map=w["workamount_skill_mean_map"],
                workamount_skill_sd_map=w["workamount_skill_sd_map"],
                facility_skill_map=w["facility_skill_map"],
                absence_time_list=w["absence_time_list"],
                state=BaseWorkerState(w["state"]),
                state_record_list=[
                    BaseWorkerState(state_num) for state_num in w["state_record_list"]
                ],
                cost_list=w["cost_list"],
                assigned_task_list=w["assigned_task_list"],
                assigned_task_id_record=w["assigned_task_id_record"],
            )
            self.worker_list.append(worker)
        self.targeted_task_list = json_data["targeted_task_list"]
        self.parent_team = json_data["parent_team"]
        # Basic variables
        self.cost_list = json_data["cost_list"]

    def extract_free_worker_list(self, target_time_list):
        """
        Extract FREE worker list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract free worker from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseWorker]: List of BaseWorker
        """
        return self.__extract_state_worker_list(target_time_list, BaseWorkerState.FREE)

    def extract_working_worker_list(self, target_time_list):
        """
        Extract WORKING worker list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract working worker from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseWorker]: List of BaseWorker
        """
        return self.__extract_state_worker_list(
            target_time_list, BaseWorkerState.WORKING
        )

    def __extract_state_worker_list(self, target_time_list, target_state):
        """
        Extract state worker list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract target_state worker from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
            target_state (BaseWorkerState):
                Target state.
        Returns:
            List[BaseWorker]: List of BaseWorker
        """
        worker_list = []
        for worker in self.worker_list:
            extract_flag = True
            for time in target_time_list:
                if len(worker.state_record_list) <= time:
                    extract_flag = False
                    break
                if worker.state_record_list[time] != target_state:
                    extract_flag = False
                    break
            if extract_flag:
                worker_list.append(worker)
        return worker_list

    def get_worker_list(
        self,
        name=None,
        ID=None,
        team_id=None,
        cost_per_time=None,
        solo_working=None,
        workamount_skill_mean_map=None,
        workamount_skill_sd_map=None,
        facility_skill_map=None,
        state=None,
        cost_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
    ):
        """
        Get worker list by using search conditions related to BaseWorker parameter.

        If there is no searching condition, this function returns all self.worker_list

        Args:
            name (str, optional):
                Target worker name.
                Defaults to None.
            ID (str, optional):
                Target worker ID.
                Defaults to None.
            workplace_id (str, optional):
                Target worker workplace_id.
                Defaults to None.
            cost_per_time (float, optional):
                Target worker cost_per_time.
                Defaults to None.
            solo_working (bool, optional):
                Target worker solo_working.
                Defaults to None.
            workamount_skill_mean_map (Dict[str, float], optional):
                Target worker workamount_skill_mean_map.
                Defaults to None.
            workamount_skill_sd_map (Dict[str, float], optional):
                Target worker workamount_skill_sd_map.
                Defaults to None.
            facility_skill_map (Dict[str, float], optional):
                Target worker facility_skill_map.
                Defaults to None.
            state (BaseWorkerState, optional):
                Target worker state.
                Defaults to None.
            cost_list (List[float], optional):
                Target worker cost_list.
                Defaults to None.
            assigned_task_list (List[BaseTask], optional):
                Target worker assigned_task_list.
                Defaults to None.
            assigned_task_id_record (List[List[str]], optional):
                Target worker assigned_task_id_record.
                Defaults to None.

        Returns:
            List[BaseWorker]: List of BaseWorker.
        """
        worker_list = self.worker_list
        if name is not None:
            worker_list = list(filter(lambda x: x.name == name, worker_list))
        if ID is not None:
            worker_list = list(filter(lambda x: x.ID == ID, worker_list))
        if team_id is not None:
            worker_list = list(filter(lambda x: x.team_id == team_id, worker_list))
        if cost_per_time is not None:
            worker_list = list(
                filter(lambda x: x.cost_per_time == cost_per_time, worker_list)
            )
        if solo_working is not None:
            worker_list = list(
                filter(lambda x: x.solo_working == solo_working, worker_list)
            )
        if workamount_skill_mean_map is not None:
            worker_list = list(
                filter(
                    lambda x: x.workamount_skill_mean_map == workamount_skill_mean_map,
                    worker_list,
                )
            )
        if workamount_skill_sd_map is not None:
            worker_list = list(
                filter(
                    lambda x: x.workamount_skill_sd_map == workamount_skill_sd_map,
                    worker_list,
                )
            )
        if facility_skill_map is not None:
            worker_list = list(
                filter(
                    lambda x: x.facility_skill_map == facility_skill_map, worker_list
                )
            )
        if state is not None:
            worker_list = list(filter(lambda x: x.state == state, worker_list))
        if cost_list is not None:
            worker_list = list(filter(lambda x: x.cost_list == cost_list, worker_list))
        if assigned_task_list is not None:
            worker_list = list(
                filter(
                    lambda x: x.assigned_task_list == assigned_task_list, worker_list
                )
            )
        if assigned_task_id_record is not None:
            worker_list = list(
                filter(
                    lambda x: x.assigned_task_id_record == assigned_task_id_record,
                    worker_list,
                )
            )
        return worker_list

    def remove_absence_time_list(self, absence_time_list):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for worker in self.worker_list:
            worker.remove_absence_time_list(absence_time_list)
        for step_time in sorted(absence_time_list, reverse=True):
            if step_time < len(self.cost_list):
                self.cost_list.pop(step_time)

    def insert_absence_time_list(self, absence_time_list):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]):
                List of absence step time in simulation.
        """
        for worker in self.worker_list:
            worker.insert_absence_time_list(absence_time_list)
        for step_time in sorted(absence_time_list):
            self.cost_list.insert(step_time, 0.0)

    def print_log(self, target_step_time):
        """
        Print log in `target_step_time`.

        Args:
            target_step_time (int):
                Target step time of printing log.
        """
        for worker in self.worker_list:
            worker.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward=False):
        """
        Print all log in chronological order.
        """
        if len(self.worker_list) > 0:
            for t in range(len(self.worker_list[0].state_record_list)):
                print("TIME: ", t)
                if backward:
                    t = len(self.worker_list[0].state_record_list) - 1 - t
                self.print_log(t)

    def check_update_state_from_absence_time_list(self, step_time):
        """
        Check and Update state of all resources to ABSENCE or FREE or WORKING.

        Args:
            step_time (int):
                Target step time of checking and updating state of workers.
        """
        for worker in self.worker_list:
            worker.check_update_state_from_absence_time_list(step_time)

    def set_absence_state_to_all_workers(self):
        """Set absence state to all workers and facilities."""
        for worker in self.worker_list:
            worker.state = BaseWorkerState.ABSENCE

    def plot_simple_gantt(
        self,
        finish_margin=1.0,
        print_team_name=True,
        view_ready=False,
        worker_color="#D9E5FF",
        ready_color="#C0C0C0",
        figsize=[6.4, 4.8],
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
            print_team_name (bool, optional):
                Print team name or not.
                Defaults to True.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to True.
            worker_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            ready_color (str, optional):
                Ready color setting information.
                Defaults to "#C0C0C0".
            figsize ((float, float), optional):
                Width, height in inches.
                Default to [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
        """
        fig, gnt = self.create_simple_gantt(
            finish_margin=finish_margin,
            print_team_name=print_team_name,
            view_ready=view_ready,
            worker_color=worker_color,
            ready_color=ready_color,
            figsize=figsize,
            dpi=dpi,
            save_fig_path=save_fig_path,
        )
        return fig

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        print_team_name=True,
        view_ready=False,
        view_absence=False,
        worker_color="#D9E5FF",
        ready_color="#DCDCDC",
        absence_color="#696969",
        figsize=[6.4, 4.8],
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
            print_team_name (bool, optional):
                Print team name or not.
                Defaults to True.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            view_absence (bool, optional):
                View ABSENCE time or not.
                Defaults to False.
            worker_color (str, optional):
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
                Default to [6.4, 4.8]
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
        fig, gnt = plt.subplots()
        fig.figsize = figsize
        fig.dpi = dpi
        gnt.set_xlabel("step")
        gnt.grid(True)

        yticks = [10 * (n + 1) for n in range(len(self.worker_list))]
        yticklabels = [worker.name for worker in self.worker_list]
        if print_team_name:
            yticklabels = [f"{self.name}: {worker.name}" for worker in self.worker_list]

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        for ttime in range(len(self.worker_list)):
            w = self.worker_list[ttime]
            (
                ready_time_list,
                working_time_list,
                absence_time_list,
            ) = w.get_time_list_for_gantt_chart(finish_margin=finish_margin)
            if view_ready:
                gnt.broken_barh(
                    ready_time_list,
                    (yticks[ttime] - 5, 9),
                    facecolors=(ready_color),
                )
            if view_absence:
                gnt.broken_barh(
                    absence_time_list,
                    (yticks[ttime] - 5, 9),
                    facecolors=(absence_color),
                )
            gnt.broken_barh(
                working_time_list,
                (yticks[ttime] - 5, 9),
                facecolors=(worker_color),
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
        print_team_name=True,
        view_ready=False,
        view_absence=False,
    ):
        """
        Create data for gantt plotly of BaseWorker in worker_list.

        Args:
            init_datetime (datetime.datetime):
              self.cost_list = self.cost_list[::-1]  Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            print_team_name (bool, optional):
                Print team name or not.
                Defaults to True.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            view_absence (bool, optional):
                View Absence time or not.
                Defaults to False.
        Returns:
            List[dict]: Gantt plotly information of this BaseTeam
        """
        df = []
        for worker in self.worker_list:
            (
                ready_time_list,
                working_time_list,
                absence_time_list,
            ) = worker.get_time_list_for_gantt_chart(finish_margin=finish_margin)

            task_name = worker.name
            if print_team_name:
                task_name = f"{self.name}: {worker.name}"

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
        print_team_name=True,
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
                {"WORKING": "rgb(46, 137, 205)", "READY": "rgb(220, 220, 220)", "ABSENCE": "rgb(105, 105, 105)"}
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
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            print_team_name (bool, optional):
                Print team name or not.
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
            init_datetime, unit_timedelta, print_team_name=print_team_name
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
        Create data for cost history plotly from cost_list of BaseWorker in worker_list.

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
            for time in range(len(self.cost_list))
        ]
        for worker in self.worker_list:
            data.append(go.Bar(name=worker.name, x=x, y=worker.cost_list))
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

    def get_target_worker_mermaid_diagram(
        self,
        target_worker_list: list[BaseWorker],
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of target worker.

        Args:
            target_worker_list (List[BaseWorker]):
                List of target workers.
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of workers in this team.
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

        if print_worker:
            for worker in target_worker_list:
                if worker in self.worker_list:
                    list_of_lines.extend(worker.get_mermaid_diagram(shape=shape_worker))

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def get_mermaid_diagram(
        self,
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this team.

        Args:
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of workers in this team.
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

        return self.get_target_worker_mermaid_diagram(
            target_worker_list=self.worker_list,
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def print_target_worker_mermaid_diagram(
        self,
        target_worker_list: list[BaseWorker],
        orientations: str = "LR",
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of target worker.

        Args:
            target_worker_list (List[BaseWorker]):
                List of target workers.
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of workers in this team.
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
        list_of_lines = self.get_target_worker_mermaid_diagram(
            target_worker_list=target_worker_list,
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this team.

        Args:
            orientations (str):
                Orientation of the flowchart.
                Defaults to "LR".
            print_worker (bool, optional):
                Print workers or not.
                Defaults to True.
            shape_worker (str, optional):
                Shape of workers in this team.
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
        self.print_target_worker_mermaid_diagram(
            target_worker_list=self.worker_list,
            orientations=orientations,
            print_worker=print_worker,
            shape_worker=shape_worker,
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
                Whether to include detailed information in the Gantt chart.
                Defaults to False.
            id_name_dict (dict[str, str], optional):
                Dictionary mapping worker IDs to names.
                Defaults to None.
        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        list_of_lines = []
        if section:
            list_of_lines.append(f"section {self.name}")
        for worker in self.worker_list:
            list_of_lines.extend(
                worker.get_gantt_mermaid_data(
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
                Whether to include detailed information in the Gantt chart.
                Defaults to False.
            id_name_dict (dict[str, str], optional):
                Dictionary mapping worker IDs to names.
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
