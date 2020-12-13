#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from .base_resource import BaseResourceState
import plotly.graph_objects as go
import plotly.figure_factory as ff
import datetime


class BaseTeam(object, metaclass=abc.ABCMeta):
    """
    BaseTeam class for expressing team in a project.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter.
            Name of this team.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
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
        name: str,
        ID=None,
        worker_list=None,
        targeted_task_list=None,
        parent_team=None,
        # Basic variables
        cost_list=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name
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
        Set parent team

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
        Extend the list of targeted tasks

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
        Append targeted task

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
        Add worker to self.worker_list

        Args:
            worker (BaseWorker):
                Worker which is added to this factory
        """
        worker.team_id = self.ID
        self.worker_list.append(worker)

    def initialize(self):
        """
        Initialize the changeable variables of BaseTeam

        - cost_list
        - changeable variable of BaseWorker in worker_list
        """
        self.cost_list = []
        for w in self.worker_list:
            w.initialize()

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
                    if worker.state == BaseResourceState.WORKING:
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
        """
        Record assigned task id in this time.
        """
        for worker in self.worker_list:
            worker.record_assigned_task_id()

    def __str__(self):
        """
        Returns:
            str: name of BaseTeam
        Examples:
            >>> team = BaseTeam("team")
            >>> print(team)
            'team'
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
        of BaseWorker in worker_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
        Returns:
            List[dict]: Gantt plotly information of this BaseTeam
        """
        df = []
        for worker in self.worker_list:
            for start_time, finish_time in zip(
                worker.start_time_list, worker.finish_time_list
            ):
                df.append(
                    dict(
                        Task=self.name + ": " + worker.name,
                        Start=(init_datetime + start_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        Finish=(
                            init_datetime
                            + (finish_time + finish_margin) * unit_timedelta
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        Type="Worker",
                    )
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
                Defaults to None -> dict(Worker="rgb(46, 137, 205)").
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
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a gantt chart

        TODO:
            Saving figure file is not implemented...
        """
        colors = colors if colors is not None else dict(Worker="rgb(46, 137, 205)")
        index_col = index_col if index_col is not None else "Type"
        df = self.create_data_for_gantt_plotly(init_datetime, unit_timedelta)
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
            print("--- Sorry, save fig is not implemented now.---")
            # plotly.io.write_image(fig, save_fig_path)

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
            Saving figure file is not implemented...
        """
        data = self.create_data_for_cost_history_plotly(init_datetime, unit_timedelta)
        fig = go.Figure(data)
        fig.update_layout(barmode="stack", title=title)
        return fig
