#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_team import BaseTeam
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
import datetime


class BaseOrganization(object, metaclass=abc.ABCMeta):
    """BaseOrganization
    BaseOrganization class for expressing organizaiton in target project.
    BaseOrganization is consist of multiple BaseTeams.
    This class will be used as template.

    Args:
        team_list (List[BaseTeam]):
            Basic parameter.
            List of BaseTeam in this organization.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this organization's cost in simumation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        team_list: List[BaseTeam],
        # Basic variables
        cost_list=None,
    ):
        # ----
        # Constraint parameters on simulation
        # --
        # Basic parameter
        self.team_list = team_list
        # --
        # Advanced parameter for customized simulation

        # ----
        # Changeable variables on simulation
        # --
        # Basic variables
        self.cost_list = []
        # --
        # Advanced varriables for customized simulation

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

    def add_labor_cost(self, only_working=True):
        """
        Add labor cost to teams and workers in this organization.

        Args:
            only_working (bool, optional):
                If True, add labor cost to only WORKING workers in this organization.
                If False, add labor cost to all workers in this organization.
                Defaults to True.

        Returns:
            float: Total labor cost of this team in this time.
        """
        cost_this_time = 0.0
        for team in self.team_list:
            cost_this_time += team.add_labor_cost(only_working=True)
        self.cost_list.append(cost_this_time)
        return cost_this_time

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=0.9,
    ):
        """
        Create data for gantt plotly from team_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulattion
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 0.9.
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
        finish_margin=0.9,
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
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 0.9.
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
        # if save_fig_path is not None:
        #     plotly.io.write_image(fig, save_fig_path)

        return fig

    def create_data_for_cost_history_plotly(
        self, init_datetime: datetime.datetime, unit_timedelta: datetime.timedelta,
    ):
        """
        Create data for cost history plotly from cost_list of team_list.

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
        for team in self.team_list:
            data.append(go.Bar(name=team.name, x=x, y=team.cost_list))
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

    def get_networkx_graph(self, view_workers=False):
        """
        Get the information of networkx graph.

        Args:
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
        Returns:
            G: networkx.Digraph()
        """
        G = nx.DiGraph()

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

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        with_labels=True,
        view_workers=False,
        **kwds,
    ):
        """
        Draw networx

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
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """
        G = G if G is not None else self.get_networkx_graph(view_workers)
        pos = pos if pos is not None else nx.spring_layout(G)
        return nx.draw_networkx(
            G, pos=pos, arrows=arrows, with_labels=with_labels, **kwds
        )

    def get_node_and_edge_trace_for_ploty_network(
        self, G=None, pos=None, node_size=20, node_color="rgb(46, 137, 205)"
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
            node_color (str, optional):
                Node color setting information.
                Defaults to "rgb(46, 137, 205)".

        Returns:
            node_trace: Node information of plotly network.
            edge_trace: Edge information of plotly network.
        """

        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(color=node_color, size=node_size,),
        )

        for node in G.nodes:
            x, y = pos[node]
            node_trace["x"] = node_trace["x"] + (x,)
            node_trace["y"] = node_trace["y"] + (y,)
            node_trace["text"] = node_trace["text"] + (node,)

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
        return node_trace, edge_trace

    def draw_plotly_network(
        self,
        G=None,
        pos=None,
        title="Organization",
        node_size=20,
        node_color="rgb(46, 137, 205)",
        view_workers=False,
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
            node_color (str, optional):
                Node color setting information.
                Defaults to "rgb(46, 137, 205)".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network

        TODO:
            Saving figure file is not implemented...
        """
        G = G if G is not None else self.get_networkx_graph(view_workers=view_workers)
        pos = pos if pos is not None else nx.spring_layout(G)
        node_trace, edge_trace = self.get_node_and_edge_trace_for_ploty_network(
            G, pos, node_size=node_size, node_color=node_color
        )
        fig = go.Figure(
            data=[edge_trace, node_trace],
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
        # if save_fig_path is not None:
        #     plotly.io.write_image(fig, save_fig_path)

        return fig
