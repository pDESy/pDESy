#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_team import BaseTeam
from .base_workplace import BaseWorkplace
from .base_worker import BaseWorker, BaseWorkerState
from .base_facility import BaseFacility, BaseFacilityState
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
import datetime
import matplotlib.pyplot as plt
import warnings


class BaseOrganization(object, metaclass=abc.ABCMeta):
    """BaseOrganization
    BaseOrganization class for expressing organization in target project.
    BaseOrganization is consist of multiple BaseTeam and BaseWorkplace.
    This class will be used as template.

    Args:
        team_list (List[BaseTeam]):
            Basic parameter.
            List of BaseTeam in this organization.
        workplace_list (List[BaseWorkplace], optional):
            Basic parameter.
            List of BaseWorkplace in this organization.
            Default to None -> []
        cost_list (List[float], optional):
            Basic variable.
            History or record of this organization's cost in simulation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        team_list: List[BaseTeam],
        workplace_list=None,
        # Basic variables
        cost_list=None,
    ):
        # ----
        # Constraint parameters on simulation
        # --
        # Basic parameter
        self.team_list = team_list
        self.workplace_list = workplace_list if workplace_list is not None else []
        # --
        # Advanced parameter for customized simulation

        # ----
        # Changeable variables on simulation
        # --
        # Basic variables
        self.cost_list = []
        # --
        # Advanced variables for customized simulation

    def __str__(self):
        """
        Returns:
            str: name list of BaseTeam
        Examples:
            >>> o = BaseOrganization([BaseTeam('t1')])
            >>> print([t.name for t in o.team_list])
            ['t1']
        """
        return "{}".format(list(map(lambda team: str(team), self.team_list)))

    def export_dict_json_data(self):
        """
        Export the information of this organization to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type="BaseOrganization",
            team_list=[t.export_dict_json_data() for t in self.team_list],
            workplace_list=[t.export_dict_json_data() for t in self.workplace_list],
            cost_list=self.cost_list,
        )
        return dict_json_data

    def read_json_data(self, json_data):
        """
        Read the JSON data for creating BaseOrganization instance.

        Args:
            json_data (dict): JSON data.
        """
        self.team_list = []
        j_list = json_data["team_list"]
        for j in j_list:
            worker_list = []
            for w in j["worker_list"]:
                worker = BaseWorker(
                    name=w["name"],
                    ID=w["ID"],
                    team_id=w["team_id"],
                    cost_per_time=w["cost_per_time"],
                    solo_working=w["solo_working"],
                    workamount_skill_mean_map=w["workamount_skill_mean_map"],
                    workamount_skill_sd_map=w["workamount_skill_sd_map"],
                    facility_skill_map=w["facility_skill_map"],
                    state=BaseWorkerState(w["state"]),
                    state_record_list=[
                        BaseWorkerState(state_num)
                        for state_num in w["state_record_list"]
                    ],
                    cost_list=w["cost_list"],
                    assigned_task_list=w["assigned_task_list"],
                    assigned_task_id_record=w["assigned_task_id_record"],
                )
                worker_list.append(worker)
            self.team_list.append(
                BaseTeam(
                    name=j["name"],
                    ID=j["ID"],
                    worker_list=worker_list,
                    targeted_task_list=j["targeted_task_list"],
                    parent_team=j["parent_team"],
                    cost_list=j["cost_list"],
                )
            )

        self.workplace_list = []
        j_list = json_data["workplace_list"]
        for j in j_list:
            facility_list = []
            for w in j["facility_list"]:
                facility = BaseFacility(
                    name=w["name"],
                    ID=w["ID"],
                    workplace_id=w["workplace_id"],
                    cost_per_time=w["cost_per_time"],
                    solo_working=w["solo_working"],
                    workamount_skill_mean_map=w["workamount_skill_mean_map"],
                    workamount_skill_sd_map=w["workamount_skill_sd_map"],
                    state=BaseFacilityState(w["state"]),
                    state_record_list=[
                        BaseFacilityState(state_num)
                        for state_num in w["state_record_list"]
                    ],
                    cost_list=w["cost_list"],
                    assigned_task_list=w["assigned_task_list"],
                    assigned_task_id_record=w["assigned_task_id_record"],
                )
                facility_list.append(facility)
            self.workplace_list.append(
                BaseWorkplace(
                    name=j["name"],
                    ID=j["ID"],
                    facility_list=facility_list,
                    targeted_task_list=j["targeted_task_list"],
                    parent_workplace=j["parent_workplace"],
                    max_space_size=j["max_space_size"],
                    cost_list=j["cost_list"],
                    placed_component_list=j["placed_component_list"],
                    placed_component_id_record=j["placed_component_id_record"],
                )
            )

        self.cost_list = json_data["cost_list"]

    def get_team_list(
        self,
        name=None,
        ID=None,
        worker_list=None,
        targeted_task_list=None,
        parent_team=None,
        cost_list=None,
    ):
        """
        Get team list by using search conditions related to BaseTeam parameter.
        If there is no searching condition, this function returns all self.team_list

        Args:
            name (str, optional):
                Target team name.
                Defaults to None.
            ID (str, optional):
                Target team ID.
                Defaults to None.
            worker_list (List[BaseWorker], optional):
                Target team worker_list.
                Defaults to None.
            targeted_task_list (List[BaseTask], optional):
                Target team targeted_task_list.
                Defaults to None.
            parent_team (BaseTeam, optional):
                Target team parent_team.
                Defaults to None.
            cost_list (List[float], optional):
                Target team cost_list.
                Defaults to None.

        Returns:
            List[BaseTeam]: List of BaseTeam.
        """
        team_list = self.team_list
        if name is not None:
            team_list = list(filter(lambda x: x.name == name, team_list))
        if ID is not None:
            team_list = list(filter(lambda x: x.ID == ID, team_list))
        if worker_list is not None:
            team_list = list(filter(lambda x: x.worker_list == worker_list, team_list))
        if targeted_task_list is not None:
            team_list = list(
                filter(lambda x: x.targeted_task_list == targeted_task_list, team_list)
            )
        if parent_team is not None:
            team_list = list(filter(lambda x: x.parent_team == parent_team, team_list))
        if cost_list is not None:
            team_list = list(filter(lambda x: x.cost_list == cost_list, team_list))
        return team_list

    def get_workplace_list(
        self,
        name=None,
        ID=None,
        facility_list=None,
        targeted_task_list=None,
        parent_workplace=None,
        max_space_size=None,
        cost_list=None,
        placed_component_list=None,
        placed_component_id_record=None,
    ):
        """
        Get workplace list by using search conditions related to BaseTeam parameter.
        If there is no searching condition, this function returns all self.workplace_list

        Args:
            name (str, optional):
                Target workplace name.
                Defaults to None.
            ID (str, optional):
                Target workplace ID.
                Defaults to None.
            facility_list (List[BaseFacility], optional):
                Target workplace facility_list.
                Defaults to None.
            targeted_task_list (List[BaseTask], optional):
                Target workplace targeted_task_list.
                Defaults to None.
            parent_workplace (BaseWorkplace, optional):
                Target workplace parent_workplace.
                Defaults to None.
            max_space_size (float, optional):
                Target workplace max_space_size.
                Defaults to None.
            placed_component_list (List[BaseComponent], optional):
                Target workplace placed_component_list.
                Defaults to None.
            placed_component_id_record(List[List[str]], optional):
                Target workplace placed_component_id_record.
                Defaults to None.
            cost_list (List[float], optional):
                Target workplace cost_list.
                Defaults to None.

        Returns:
            List[BaseWorkplace]: List of BaseWorkplace.
        """
        workplace_list = self.workplace_list
        if name is not None:
            workplace_list = list(filter(lambda x: x.name == name, workplace_list))
        if ID is not None:
            workplace_list = list(filter(lambda x: x.ID == ID, workplace_list))
        if facility_list is not None:
            workplace_list = list(
                filter(lambda x: x.facility_list == facility_list, workplace_list)
            )
        if targeted_task_list is not None:
            workplace_list = list(
                filter(
                    lambda x: x.targeted_task_list == targeted_task_list, workplace_list
                )
            )
        if parent_workplace is not None:
            workplace_list = list(
                filter(lambda x: x.parent_workplace == parent_workplace, workplace_list)
            )
        if max_space_size is not None:
            workplace_list = list(
                filter(lambda x: x.max_space_size == max_space_size, workplace_list)
            )
        if placed_component_list is not None:
            workplace_list = list(
                filter(
                    lambda x: x.placed_component_list == placed_component_list,
                    workplace_list,
                )
            )
        if placed_component_id_record is not None:
            workplace_list = list(
                filter(
                    lambda x: x.placed_component_id_record
                    == placed_component_id_record,
                    workplace_list,
                )
            )
        if cost_list is not None:
            workplace_list = list(
                filter(lambda x: x.cost_list == cost_list, workplace_list)
            )
        return workplace_list

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
        This method just executes BaseTeam.get_worker_list() in self.team_list.

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
        worker_list = []
        for team in self.team_list:
            worker_list = worker_list + team.get_worker_list(
                name=name,
                ID=ID,
                team_id=team_id,
                cost_per_time=cost_per_time,
                solo_working=solo_working,
                workamount_skill_mean_map=workamount_skill_mean_map,
                workamount_skill_sd_map=workamount_skill_sd_map,
                facility_skill_map=facility_skill_map,
                state=state,
                cost_list=cost_list,
                assigned_task_list=assigned_task_list,
                assigned_task_id_record=assigned_task_id_record,
            )
        return worker_list

    def get_facility_list(
        self,
        name=None,
        ID=None,
        workplace_id=None,
        cost_per_time=None,
        solo_working=None,
        workamount_skill_mean_map=None,
        workamount_skill_sd_map=None,
        state=None,
        cost_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
    ):
        """
        Get facility list by using search conditions related to BaseFacility parameter.
        This method just executes BaseTeam.get_facility_list() in self.workplace_list.

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
            cost_list (List[float], optional):
                Target facility cost_list.
                Defaults to None.
            assigned_task_list (List[BaseTask], optional):
                Target facility assigned_task_list.
                Defaults to None.
            assigned_task_id_record (List[List[str]], optional):
                Target facility assigned_task_id_record.
                Defaults to None.

        Returns:
            List[BaseFacility]: List of BaseFacility.
        """
        facility_list = []
        for workplace in self.workplace_list:
            facility_list = facility_list + workplace.get_facility_list(
                name=name,
                ID=ID,
                workplace_id=workplace_id,
                cost_per_time=cost_per_time,
                solo_working=solo_working,
                workamount_skill_mean_map=workamount_skill_mean_map,
                workamount_skill_sd_map=workamount_skill_sd_map,
                state=state,
                cost_list=cost_list,
                assigned_task_list=assigned_task_list,
                assigned_task_id_record=assigned_task_id_record,
            )
        return facility_list

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the changeable variables of BaseOrganization

        If `log_info` is True, the following attributes are initialized.
          - cost_list

        BaseTeam in `team_list` and BaseWorkplace in `workplace_list` are also initialized by this function.

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
        for team in self.team_list:
            team.initialize(state_info=state_info, log_info=log_info)
        for workplace in self.workplace_list:
            workplace.initialize(state_info=state_info, log_info=log_info)

    def reverse_log_information(self):
        """
        Reverse log information of all.
        """
        self.cost_list = self.cost_list[::-1]
        for team in self.team_list:
            team.reverse_log_information()
        for workplace in self.workplace_list:
            workplace.reverse_log_information()

    def add_labor_cost(
        self,
        only_working=True,
        add_zero_to_all_workers=False,
        add_zero_to_all_facilities=False,
    ):
        """
        Add labor cost to teams and workers in this organization.

        Args:
            only_working (bool, optional):
                If True, add labor cost to only WORKING workers in this organization.
                If False, add labor cost to all workers in this organization.
                Defaults to True.
            add_zero_to_all_workers (bool, optional):
                If True, add 0 labor cost to all workers in this team.
                If False, calculate labor cost normally.
                Defaults to False.
            add_zero_to_all_facilities (bool, optional):
                If True, add 0 labor cost to all facilities in this team.
                If False, calculate labor cost normally.
                Defaults to False.

        Returns:
            float: Total labor cost of this team in this time.
        """
        cost_this_time = 0.0
        for team in self.team_list:
            cost_this_time += team.add_labor_cost(
                only_working=only_working,
                add_zero_to_all_workers=add_zero_to_all_workers,
            )
        for workplace in self.workplace_list:
            cost_this_time += workplace.add_labor_cost(
                only_working=only_working,
                add_zero_to_all_facilities=add_zero_to_all_facilities,
            )
        self.cost_list.append(cost_this_time)
        return cost_this_time

    def record(self):
        """
        Record assigned task id and component.
        """
        for team in self.team_list:
            team.record_assigned_task_id()
            team.record_all_worker_state()
        for workplace in self.workplace_list:
            workplace.record_assigned_task_id()
            workplace.record_placed_component_id()
            workplace.record_all_facility_state()

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        view_ready=False,
        view_workers=True,
        view_facilities=True,
        team_color="#0099FF",
        worker_color="#D9E5FF",
        workplace_color="#0099FF",
        facility_color="#D9E5FF",
        ready_color="#C0C0C0",
        figsize=[6.4, 4.8],
        dpi=100.0,
        save_fig_path=None,
    ):
        """

        Method for creating Gantt chart by matplotlib.
        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to Trstate = w.state_record_list[time]ue.
            team_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            workplace_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            ready_color (str, optional):
                Ready Worker/Facility color setting information.
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
            gnt: gnt in plt.subplots()
        """
        fig, gnt = plt.subplots()
        fig.figsize = figsize
        fig.dpi = dpi
        gnt.set_xlabel("step")
        gnt.grid(True)

        target_worker_list = []
        target_facility_list = []
        yticklabels = []
        if view_workers:
            for team in self.team_list:
                for worker in team.worker_list:
                    target_worker_list.append(worker)
                    yticklabels.append(team.name + ":" + worker.name)
        if view_facilities:
            for workplace in self.workplace_list:
                for facility in workplace.facility_list:
                    target_facility_list.append(facility)
                    yticklabels.append(workplace.name + ":" + facility.name)
        yticks = [
            10 * (n + 1)
            for n in range(len(target_worker_list) + len(target_facility_list))
        ]

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        for ttime in range(len(target_worker_list)):
            w = target_worker_list[ttime]
            (
                ready_time_list,
                working_time_list,
            ) = w.get_time_list_for_gannt_chart(finish_margin=finish_margin)
            if view_ready:
                gnt.broken_barh(
                    ready_time_list,
                    (yticks[ttime] - 5, 9),
                    facecolors=(ready_color),
                )
            gnt.broken_barh(
                working_time_list,
                (yticks[ttime] - 5, 9),
                facecolors=(worker_color),
            )

        for ttime in range(len(target_facility_list)):
            w = target_facility_list[ttime]
            (
                ready_time_list,
                working_time_list,
            ) = w.get_time_list_for_gannt_chart(finish_margin)
            if view_ready:
                gnt.broken_barh(
                    ready_time_list,
                    (yticks[ttime + len(target_worker_list)] - 5, 9),
                    facecolors=(ready_color),
                )
            gnt.broken_barh(
                working_time_list,
                (yticks[ttime + len(target_worker_list)] - 5, 9),
                facecolors=(facility_color),
            )

        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        view_ready=False,
    ):
        """
        Create data for gantt plotly from team_list.

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
            List[dict]: Gantt plotly information of this BaseOrganization.
        """
        df = []
        for team in self.team_list:
            df.extend(
                team.create_data_for_gantt_plotly(
                    init_datetime,
                    unit_timedelta,
                    finish_margin=finish_margin,
                    view_ready=view_ready,
                )
            )
        for workplace in self.workplace_list:
            df.extend(
                workplace.create_data_for_gantt_plotly(
                    init_datetime,
                    unit_timedelta,
                    finish_margin=finish_margin,
                    view_ready=view_ready,
                )
            )
        return df

    def create_gantt_plotly(
        self,
        init_datetime,
        unit_timedelta,
        title="Gantt Chart",
        colors=None,
        index_col=None,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=True,
        show_colorbar=True,
        finish_margin=1.0,
        view_ready=False,
        save_fig_path=None,
    ):
        """
        Method for creating Gantt chart by plotly.
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
                Defaults to None -> dict(WORKING="rgb(46, 137, 205)", READY="rgb(107, 127, 135)").
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
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a gantt chart

        TODO:
            Now, save_fig_path can be utilized only json and html format.
            Saving figure png, jpg, svg file is not implemented...
        """
        colors = (
            colors
            if colors is not None
            else dict(WORKING="rgb(46, 137, 205)", READY="rgb(107, 127, 135)")
        )
        index_col = index_col if index_col is not None else "State"
        df = self.create_data_for_gantt_plotly(
            init_datetime,
            unit_timedelta,
            finish_margin=finish_margin,
            view_ready=view_ready,
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
            # fig.write_image(save_fig_path)
            dot_point = save_fig_path.rfind(".")

            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            elif save_mode in ["png", "jpg", "jpeg", "webp", "svg", "pdf", "eps"]:
                # We need to install plotly/orca
                # and set `plotly.io.orca.config.executable = '/path/to/orca'``
                # fig_go_figure = go.Figure(fig)
                # fig_go_figure.write_html(save_fig_path)
                save_mode = "error"

            if save_mode == "error":
                warnings.warn(
                    "Sorry, the function of saving this type is not implemented now. "
                    "pDESy is only support html and json in saving plotly."
                )

        return fig

    def create_data_for_cost_history_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
    ):
        """
        Create data for cost history plotly from cost_list of team_list.

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
        for team in self.team_list:
            data.append(go.Bar(name=team.name, x=x, y=team.cost_list))
        for workplace in self.workplace_list:
            data.append(go.Bar(name=workplace.name, x=x, y=workplace.cost_list))
        return data

    def create_cost_history_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        title="Cost Chart",
        save_fig_path=None,
    ):
        """
        Method for creating cost chart by plotly.
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

        TODO:
            Now, save_fig_path can be utilized only json and html format.
            Saving figure png, jpg, svg file is not implemented...
        """
        data = self.create_data_for_cost_history_plotly(init_datetime, unit_timedelta)
        fig = go.Figure(data)
        fig.update_layout(barmode="stack", title=title)
        if save_fig_path is not None:
            # fig.write_image(save_fig_path)
            dot_point = save_fig_path.rfind(".")

            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            elif save_mode in ["png", "jpg", "jpeg", "webp", "svg", "pdf", "eps"]:
                # We need to install plotly/orca
                # and set `plotly.io.orca.config.executable = '/path/to/orca'``
                # fig_go_figure = go.Figure(fig)
                # fig_go_figure.write_html(save_fig_path)
                save_mode = "error"

            if save_mode == "error":
                warnings.warn(
                    "Sorry, the function of saving this type is not implemented now. "
                    "pDESy is only support html and json in saving plotly."
                )
        return fig

    def get_networkx_graph(self, view_workers=False, view_facilities=False):
        """
        Get the information of networkx graph.

        Args:
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
        Returns:
            G: networkx.Digraph()
        """
        G = nx.DiGraph()

        # BaseTeam
        # 1. add all nodes
        for team in self.team_list:
            G.add_node(team)

        # 2. add all edges
        for team in self.team_list:
            if team.parent_team is not None:
                G.add_edge(team.parent_team, team)

        if view_workers:
            for team in self.team_list:
                for w in team.worker_list:
                    G.add_node(w)
                    G.add_edge(team, w)

        # BaseWorkplace
        # 1. add all nodes
        for workplace in self.workplace_list:
            G.add_node(workplace)

        # 2. add all edges
        for workplace in self.workplace_list:
            if workplace.parent_workplace is not None:
                G.add_edge(workplace.parent_workplace, workplace)

        if view_facilities:
            for workplace in self.workplace_list:
                for w in workplace.facility_list:
                    G.add_node(w)
                    G.add_edge(workplace, w)

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        view_workers=False,
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_facilities=False,
        workplace_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        figsize=[6.4, 4.8],
        dpi=100.0,
        save_fig_path=None,
        **kwds,
    ):
        """
        Draw networkx

        Args:
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
            arrows (bool, optional):
                Digraph or Graph(no arrows).
                Defaults to True.
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
            workplace_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            figsize ((float, float), optional):
                Width, height in inches.
                Default to [6.4, 4.8]
            dpi (float, optional):
                The resolution of the figure in dots-per-inch.
                Default to 100.0
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """

        fig = plt.figure(figsize=figsize, dpi=dpi)
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)

        # team
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=self.team_list,
            node_color=team_node_color,
            # **kwds,
        )
        # workers
        if view_workers:

            worker_list = []
            for team in self.team_list:
                worker_list.extend(team.worker_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=worker_list,
                node_color=worker_node_color,
                # **kwds,
            )

        # workplace
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=self.workplace_list,
            node_color=workplace_node_color,
            # **kwds,
        )
        # facility
        if view_facilities:

            facility_list = []
            for workplace in self.workplace_list:
                facility_list.extend(workplace.facility_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=facility_list,
                node_color=facility_node_color,
                # **kwds,
            )

        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        plt.axis("off")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig

    def get_node_and_edge_trace_for_plotly_network(
        self,
        G=None,
        pos=None,
        node_size=20,
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        workplace_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        view_facilities=False,
    ):
        """
        Get nodes and edges information of plotly network.

        Args:
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            workplace_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.

        Returns:
            team_node_trace: Team Node information of plotly network.
            worker_node_trace: Worker Node information of plotly network.
            workplace_node_trace: Workplace Node information of plotly network.
            facility_node_trace: Facility Node information of plotly network.
            edge_trace: Edge information of plotly network.
        """

        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)

        team_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=team_node_color,
                size=node_size,
            ),
        )
        worker_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=worker_node_color,
                size=node_size,
            ),
        )
        workplace_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=workplace_node_color,
                size=node_size,
            ),
        )
        facility_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=facility_node_color,
                size=node_size,
            ),
        )

        for node in G.nodes:
            x, y = pos[node]
            if isinstance(node, BaseTeam):
                team_node_trace["x"] = team_node_trace["x"] + (x,)
                team_node_trace["y"] = team_node_trace["y"] + (y,)
                team_node_trace["text"] = team_node_trace["text"] + (node,)
            elif isinstance(node, BaseWorkplace):
                workplace_node_trace["x"] = workplace_node_trace["x"] + (x,)
                workplace_node_trace["y"] = workplace_node_trace["y"] + (y,)
                workplace_node_trace["text"] = workplace_node_trace["text"] + (node,)
            elif isinstance(node, BaseFacility):
                facility_node_trace["x"] = facility_node_trace["x"] + (x,)
                facility_node_trace["y"] = facility_node_trace["y"] + (y,)
                facility_node_trace["text"] = facility_node_trace["text"] + (node,)
            elif isinstance(node, BaseWorker):
                worker_node_trace["x"] = worker_node_trace["x"] + (x,)
                worker_node_trace["y"] = worker_node_trace["y"] + (y,)
                worker_node_trace["text"] = worker_node_trace["text"] + (node,)

        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=1, color="#888"), hoverinfo="none", mode="lines"
        )

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace["x"] += (xposx, yposx)
            edge_trace["y"] += (xposy, yposy)

        return (
            team_node_trace,
            worker_node_trace,
            workplace_node_trace,
            facility_node_trace,
            edge_trace,
        )

    def draw_plotly_network(
        self,
        G=None,
        pos=None,
        title="Organization",
        node_size=20,
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        workplace_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        view_facilities=False,
        save_fig_path=None,
    ):
        """
        Draw plotly network

        Args:
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
            title (str, optional):
                Figure title of this network.
                Defaults to "Organization".
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            workplace_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network

        TODO:
            Now, save_fig_path can be utilized only json and html format.
            Saving figure png, jpg, svg file is not implemented...
        """
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)
        (
            team_node_trace,
            worker_node_trace,
            workplace_node_trace,
            facility_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(
            G,
            pos,
            node_size=node_size,
            team_node_color=team_node_color,
            worker_node_color=worker_node_color,
            view_workers=view_workers,
            workplace_node_color=workplace_node_color,
            facility_node_color=facility_node_color,
            view_facilities=view_facilities,
        )
        fig = go.Figure(
            data=[
                edge_trace,
                team_node_trace,
                worker_node_trace,
                workplace_node_trace,
                facility_node_trace,
            ],
            layout=go.Layout(
                title=title,
                showlegend=False,
                #         hovermode='closest',
                #         margin=dict(b=20,l=5,r=5,t=40),
                annotations=[
                    dict(
                        ax=edge_trace["x"][index * 2],
                        ay=edge_trace["y"][index * 2],
                        axref="x",
                        ayref="y",
                        x=edge_trace["x"][index * 2 + 1],
                        y=edge_trace["y"][index * 2 + 1],
                        xref="x",
                        yref="y",
                        showarrow=True,
                        arrowhead=5,
                    )
                    for index in range(0, int(len(edge_trace["x"]) / 2))
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        if save_fig_path is not None:
            # fig.write_image(save_fig_path)
            dot_point = save_fig_path.rfind(".")

            save_mode = "error" if dot_point == -1 else save_fig_path[dot_point + 1 :]

            if save_mode == "html":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_html(save_fig_path)
            elif save_mode == "json":
                fig_go_figure = go.Figure(fig)
                fig_go_figure.write_json(save_fig_path)
            elif save_mode in ["png", "jpg", "jpeg", "webp", "svg", "pdf", "eps"]:
                # We need to install plotly/orca
                # and set `plotly.io.orca.config.executable = '/path/to/orca'``
                # fig_go_figure = go.Figure(fig)
                # fig_go_figure.write_html(save_fig_path)
                save_mode = "error"

            if save_mode == "error":
                warnings.warn(
                    "Sorry, the function of saving this type is not implemented now. "
                    "pDESy is only support html and json in saving plotly."
                )
        return fig
