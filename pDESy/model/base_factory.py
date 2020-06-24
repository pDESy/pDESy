#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from .base_resource import BaseResourceState
import plotly.graph_objects as go
import plotly.figure_factory as ff
import datetime


class BaseFactory(object, metaclass=abc.ABCMeta):
    """
    BaseFactory class for expressing factory including facilities in a project.
    This class will be used as template.

    Args:
        name (str):
            Basic parameter.
            Name of this factory.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        facility_list (List[BaseFacility], optional):
            Basic parameter.
            List of BaseFacility who belong to this factory.
            Defaults to None -> [].
        targeted_task_list (List[BaseTask], optional):
            Basic parameter.
            List of targeted BaseTasks.
            Defaults to None -> [].
        parent_factory (BaseFactory, optional):
            Basic parameter.
            Parent factory of this factory.
            Defaults to None.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this factory's cost in simumation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        facility_list=None,
        targeted_task_list=None,
        parent_factory=None,
        # Basic variables
        cost_list=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())

        self.facility_list = facility_list if facility_list is not None else []
        for facility in self.facility_list:
            if facility.factory_id is None:
                facility.factory_id = self.ID

        self.targeted_task_list = (
            targeted_task_list if targeted_task_list is not None else []
        )
        self.parent_factory = parent_factory if parent_factory is not None else None

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if cost_list is not None:
            self.cost_list = cost_list
        else:
            self.cost_list = []

    def set_parent_factory(self, parent_factory):
        """
        Set parent factory

        Args:
            parent_factory (BaseFactory):
                Parent factory
        Examples:
            >>> t = BaseFactory('t')
            >>> t1 = BaseFactory('t1')
            >>> t.set_parent_factory(t1)
            >>> print(t.parent_factory.name)
            't1'
        """
        self.parent_factory = parent_factory

    def extend_targeted_task_list(self, targeted_task_list):
        """
        Extend the list of targetd tasks

        Args:
            targeted_task_list (list[BaseTask]):
                List of targeted tasks
        Examples:
            >>> factory = BaseFactory('factory')
            >>> print([targeted_t.name for targeted_t in factory.targeted_task_list])
            []
            >>> factory.extend_targeted_task_list([BaseTask('t1'),BaseTask('t2')])
            >>> print([targeted_t.name for targeted_t in factory.targeted_task_list])
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
            >>> factory = BaseFactory('factory')
            >>> print([targeted_t.name for targeted_t in factory.targeted_task_list])
            []
            >>> t1 = BaseTask('t1')
            >>> factory.append_targeted_task(t1)
            >>> print([targeted_t.name for targeted_t in factory.targeted_task_list])
            ['t1']
            >>> print([target_f.name for target_f in t1.allocated_factory_list])
            ['factory']
        """
        self.targeted_task_list.append(targeted_task)
        targeted_task.allocated_factory_list.append(self)

    def initialize(self):
        """
        Initialize the changeable variables of BaseFactory

        - cost_list
        - changeable variable of BaseFacility in facility_list
        """
        self.cost_list = []
        for w in self.facility_list:
            w.initialize()

    def add_labor_cost(self, only_working=True, add_zero_to_all_facilities=False):
        """
        Add labor cost to resources in this factory.

        Args:
            only_working (bool, optional):
                If True, add labor cost to only WORKING facilitys in this factory.
                If False, add labor cost to all facilitys in this factory.
                Defaults to True.
            add_zero_to_all_facilities (bool, optional):
                If True, add 0 labor cost to all facilities in this factory.
                If False, calculate labor cost normally.
                Defaults to False.

        Returns:
            float: Total labor cost of this factory in this time.
        """
        cost_this_time = 0.0

        if add_zero_to_all_facilities:
            for facility in self.facility_list:
                facility.cost_list.append(0.0)

        else:

            if only_working:
                for facility in self.facility_list:
                    if facility.state == BaseResourceState.WORKING:
                        facility.cost_list.append(facility.cost_per_time)
                        cost_this_time += facility.cost_per_time
                    else:
                        facility.cost_list.append(0.0)

            else:
                for facility in self.facility_list:
                    facility.cost_list.append(facility.cost_per_time)
                    cost_this_time += facility.cost_per_time

        self.cost_list.append(cost_this_time)
        return cost_this_time

    def record_assigned_task_id(self):
        """
        Record assigned task id in this time.
        """
        for resource in self.facility_list:
            resource.record_assigned_task_id()

    def __str__(self):
        """
        Returns:
            str: name of BaseFactory
        Examples:
            >>> factory = BaseFactory("factory")
            >>> print(factory)
            'factory'
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
        of BaseFacility in facility_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulattion
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
        Returns:
            List[dict]: Gantt plotly information of this BaseFactory
        """
        df = []
        for facility in self.facility_list:
            for start_time, finish_time in zip(
                facility.start_time_list, facility.finish_time_list
            ):
                df.append(
                    dict(
                        Task=self.name + ": " + facility.name,
                        Start=(init_datetime + start_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        Finish=(
                            init_datetime
                            + (finish_time + finish_margin) * unit_timedelta
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        Type="Facility",
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
                Unit time of simulattion
            title (str, optional):
                Title of Gantt chart.
                Defaults to "Gantt Chart".
            colors (Dict[str, str], optional):
                Color setting of plotly Gantt chart.
                Defaults to None -> dict(Facility="rgb(46, 137, 205)").
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
        colors = colors if colors is not None else dict(Facility="rgb(46, 137, 205)")
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
        # if save_fig_path is not None:
        #     plotly.io.write_image(fig, save_fig_path)

        return fig

    def create_data_for_cost_history_plotly(
        self, init_datetime: datetime.datetime, unit_timedelta: datetime.timedelta,
    ):
        """
        Create data for cost history plotly from cost_list in facility_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulattion

        Returns:
            data (List[go.Bar(name, x, y)]: Information of cost history chart.
        """
        data = []
        x = [
            (init_datetime + time * unit_timedelta).strftime("%Y-%m-%d %H:%M:%S")
            for time in range(len(self.cost_list))
        ]
        for facility in self.facility_list:
            data.append(go.Bar(name=facility.name, x=x, y=facility.cost_list))
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
                Unit time of simulattion
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
