#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_team import BaseTeam
from .base_factory import BaseFactory
from .base_worker import BaseWorker
from .base_facility import BaseFacility
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
import datetime
import matplotlib.pyplot as plt


class BaseOrganization(object, metaclass=abc.ABCMeta):
    """BaseOrganization
    BaseOrganization class for expressing organization in target project.
    BaseOrganization is consist of multiple BaseTeam and BaseFactory.
    This class will be used as template.

    Args:
        team_list (List[BaseTeam]):
            Basic parameter.
            List of BaseTeam in this organization.
        factory_list (List[BaseFactory], optional):
            Basic parameter.
            List of BaseFactory in this organization.
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
        factory_list=None,
        # Basic variables
        cost_list=None,
    ):
        # ----
        # Constraint parameters on simulation
        # --
        # Basic parameter
        self.team_list = team_list
        self.factory_list = factory_list if factory_list is not None else []
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

    def initialize(self):
        """
        Initialize the changeable variables of BaseOrganization

        - cost_list
        - changeable variables of BaseTeam in team_list

        """
        self.cost_list = []
        for team in self.team_list:
            team.initialize()
        for factory in self.factory_list:
            factory.initialize()

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
        for factory in self.factory_list:
            cost_this_time += factory.add_labor_cost(
                only_working=only_working,
                add_zero_to_all_facilities=add_zero_to_all_facilities,
            )
        self.cost_list.append(cost_this_time)
        return cost_this_time

    def record(self):
        """
        Record assigned task id and component in this time.
        """
        for team in self.team_list:
            team.record_assigned_task_id()
        for factory in self.factory_list:
            factory.record_assigned_task_id()
            factory.record_placed_component_id()

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        view_workers=True,
        view_facilities=True,
        team_color="#0099FF",
        worker_color="#D9E5FF",
        factory_color="#0099FF",
        facility_color="#D9E5FF",
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
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to True.
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to True.
            team_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            factory_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
            gnt: gnt in plt.subplots()
        Note:
            view_worker=False mode is not implemented now...

        TODO:
            view_worker=False mode should be implemented.
            view_facility=False mode should be implemented.
        """
        fig, gnt = plt.subplots()
        gnt.set_xlabel("step")
        gnt.grid(True)

        target_worker_list = []
        target_facility_list = []
        yticklabels = []
        for team in self.team_list:
            for worker in team.worker_list:
                target_worker_list.append(worker)
                yticklabels.append(team.name + ":" + worker.name)
        for factory in self.factory_list:
            for facility in factory.facility_list:
                target_facility_list.append(facility)
                yticklabels.append(factory.name + ":" + facility.name)
        yticks = [
            10 * (n + 1)
            for n in range(len(target_worker_list) + len(target_facility_list))
        ]

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        for ttime in range(len(target_worker_list)):
            worker = target_worker_list[ttime]
            wlist = []
            for wtime in range(len(worker.start_time_list)):
                wlist.append(
                    (
                        worker.start_time_list[wtime],
                        worker.finish_time_list[wtime]
                        - worker.start_time_list[wtime]
                        + finish_margin,
                    )
                )
            gnt.broken_barh(wlist, (yticks[ttime] - 5, 9), facecolors=(worker_color))

        for ttime in range(len(target_facility_list)):
            facility = target_facility_list[ttime]
            wlist = []
            for wtime in range(len(facility.start_time_list)):
                wlist.append(
                    (
                        facility.start_time_list[wtime],
                        facility.finish_time_list[wtime]
                        - facility.start_time_list[wtime]
                        + finish_margin,
                    )
                )
            gnt.broken_barh(
                wlist,
                (yticks[ttime + len(target_worker_list)] - 5, 9),
                facecolors=(worker_color),
            )

        if save_fig_path is not None:
            plt.savefig(save_fig_path)

        return fig, gnt

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
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
        Returns:
            List[dict]: Gantt plotly information of this BaseOrganization.
        """
        df = []
        for team in self.team_list:
            df.extend(
                team.create_data_for_gantt_plotly(
                    init_datetime, unit_timedelta, finish_margin=finish_margin
                )
            )
        for factory in self.factory_list:
            df.extend(
                factory.create_data_for_gantt_plotly(
                    init_datetime, unit_timedelta, finish_margin=finish_margin
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
                Defaults to None -> dict(Worker="rgb(46, 137, 205)",Facility="rgb(46, 137, 205)").
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
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a gantt chart

        TODO:
            Saving figure file is not implemented...
        """
        colors = (
            colors
            if colors is not None
            else dict(Worker="rgb(46, 137, 205)", Facility="rgb(46, 137, 205)")
        )
        index_col = index_col if index_col is not None else "Type"
        df = self.create_data_for_gantt_plotly(
            init_datetime, unit_timedelta, finish_margin=finish_margin
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
            #     plotly.io.write_image(fig, save_fig_path)
            print("--- Sorry, save fig is not implemented now.---")

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
        for factory in self.factory_list:
            data.append(go.Bar(name=factory.name, x=x, y=factory.cost_list))
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

        # BaseFactory
        # 1. add all nodes
        for factory in self.factory_list:
            G.add_node(factory)

        # 2. add all edges
        for factory in self.factory_list:
            if factory.parent_factory is not None:
                G.add_edge(factory.parent_factory, factory)

        if view_facilities:
            for factory in self.factory_list:
                for w in factory.facility_list:
                    G.add_node(w)
                    G.add_edge(factory, w)

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        with_labels=True,
        view_workers=False,
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_facilities=False,
        factory_node_color="#0099FF",
        facility_node_color="#D9E5FF",
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
            with_labels (bool, optional):
                Label is describing or not.
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
            factory_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)

        # nx.draw_networkx(G, pos=pos, arrows=arrows, with_labels=with_labels, **kwds)

        # team
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.team_list,
            node_color=team_node_color,
            # **kwds,
        )
        # resources
        if view_workers:

            worker_list = []
            for team in self.team_list:
                worker_list.extend(team.worker_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                with_labels=with_labels,
                nodelist=worker_list,
                node_color=worker_node_color,
                # **kwds,
            )

        # factory
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.factory_list,
            node_color=factory_node_color,
            # **kwds,
        )
        # facility
        if view_facilities:

            facility_list = []
            for factory in self.factory_list:
                facility_list.extend(factory.facility_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                with_labels=with_labels,
                nodelist=facility_list,
                node_color=facility_node_color,
                # **kwds,
            )

        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)

    def get_node_and_edge_trace_for_plotly_network(
        self,
        G=None,
        pos=None,
        node_size=20,
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        factory_node_color="#0099FF",
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
            factory_node_color (str, optional):
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
            factory_node_trace: Factory Node information of plotly network.
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
        factory_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=factory_node_color,
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
            elif isinstance(node, BaseFactory):
                factory_node_trace["x"] = factory_node_trace["x"] + (x,)
                factory_node_trace["y"] = factory_node_trace["y"] + (y,)
                factory_node_trace["text"] = factory_node_trace["text"] + (node,)
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
            factory_node_trace,
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
        factory_node_color="#0099FF",
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
            factory_node_color (str, optional):
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
            Saving figure file is not implemented...
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
            factory_node_trace,
            facility_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(
            G,
            pos,
            node_size=node_size,
            team_node_color=team_node_color,
            worker_node_color=worker_node_color,
            view_workers=view_workers,
            factory_node_color=factory_node_color,
            facility_node_color=facility_node_color,
            view_facilities=view_facilities,
        )
        fig = go.Figure(
            data=[
                edge_trace,
                team_node_trace,
                worker_node_trace,
                factory_node_trace,
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
            print("--- Sorry, save fig is not implemented now.---")
        #     plotly.io.write_image(fig, save_fig_path)

        return fig
