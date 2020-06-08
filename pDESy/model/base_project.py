#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import datetime
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
from .base_component import BaseComponent
from .base_task import BaseTask
from .base_team import BaseTeam


class BaseProject(object, metaclass=ABCMeta):
    """BaseProject
    BaseProject class for expressing target project
    including product, organization and workflow.
    This class will be used as template.

    Args:
        file_path (str, optional):
            File path of this project data for reading.
            Defaults to None. (New Project)
        init_datetime (datetime.datetime, optional):
            Start datetime of project.
            Defaults to None -> datetime.datetime.now().
        unit_timedelta (datetime.timedelta, optional):
            Unit time of simulattion.
            Defaults to None -> datetime.timedelta(minutes=1).
        product (BaseProduct, optional):
            BaseProduct in this project.
            Defaults to None. (New Project)
        organization (BaseOrganization, optional):
            BaseOrganization in this project.
            Defaults to None. (New Project)
        workflow (BaseWorkflow, optional):
            BaseWorkflow in this project.
            Defaults to None. (New Project)
        time (int, optional):
            Simulation time executing this method.
            Defaults to 0.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this project's cost in simumation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        file_path=None,
        # Basic parameters
        init_datetime=None,
        unit_timedelta=None,
        # Basic variables
        product=None,
        organization=None,
        workflow=None,
        time=0,
        cost_list=None,
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.init_datetime = (
            init_datetime if init_datetime is not None else datetime.datetime.now()
        )
        self.unit_timedelta = (
            unit_timedelta
            if unit_timedelta is not None
            else datetime.timedelta(minutes=1)
        )
        # --
        # Advanced parameter for customized simulation
        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if product is not None:
            self.product = product
        else:
            self.product = None

        if organization is not None:
            self.organization = organization
        else:
            self.organization = None

        if workflow is not None:
            self.workflow = workflow
        else:
            self.workflow = None

        if time != int(0):
            self.time = time
        else:
            self.time = int(0)

        if cost_list is not None:
            self.cost_list = cost_list
        else:
            self.cost_list = []
        # --
        # Advanced varriables for customized simulation

    def __str__(self):
        """
        Returns:
            str: time and name lists of product, organization and workflow.
        """
        return "TIME: {}\nPRODUCT\n{}\n\nORGANIZATION\n{}\n\nWORKFLOW\n{}".format(
            self.time, str(self.product), str(self.organization), str(self.workflow)
        )

    @abstractmethod
    def initialize(self):
        """
        Initialize the changeable variables of this BaseProject.
        This abstract method should be implemented and updated in your class.
        """
        pass

    # @abstractmethod
    # def read_pDES_json(self, file_path: str, encoding: str):
    #     "This abstract method should be implemented in your class"

    @abstractmethod
    def simulate(
        self,
        worker_perfoming_mode="single-task",
        task_performed_mode="multi-workers",
        error_tol=1e-10,
        print_debug=False,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
        max_time=10000,
    ):
        """
        Simulation funciton for simulate this BaseProject.
        This abstract method should be implemented and updated in your class.

        Args:
            worker_perfoming_mode (str, optional):
                Mode of worker's performance in simulation.
                pDESy has the following options of this mode in simulation.

                - single-task
                - multi-task

                Defaults to "single-task".
            task_performed_mode (str, optional):
                Mode of performed task in simulation.
                pDESy has the following options of this mode in simulation.

                - single-worker
                - multi-workers

                Defaults to "multi-workers".
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            print_debug (bool, optional):
                Whether prrint debug is inclde or not
                Defaults to False.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every timw.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.
            max_time (int, optional):
                Max time of simulation.
                Defaults to 10000.
        """

    def is_business_time(
        self,
        target_datetime: datetime.datetime,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
    ):
        """
        Check whether target_datetime is business time or not in thip project.

        Args:
            target_datetime (datetime.datetime):
                Target datetime of checking business time or not.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every timw.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.

        Returns:
            bool: whether target_datetime is business time or not.
        """
        if not weekend_working:
            if target_datetime.weekday() >= 5:
                return False
            else:
                if work_start_hour is not None and work_finish_hour is not None:
                    if (
                        target_datetime.hour >= work_start_hour
                        and target_datetime.hour <= work_finish_hour
                    ):
                        return True
                    else:
                        return False
                else:
                    return True

        else:
            if work_start_hour is not None and work_finish_hour is not None:
                if (
                    target_datetime.hour >= work_start_hour
                    and target_datetime.hour <= work_finish_hour
                ):
                    return True
                else:
                    return False
            else:
                return True

    def create_gantt_plotly(
        self,
        title="Gantt Chart",
        colors=None,
        index_col=None,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=False,
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
        colors = (
            colors
            if colors is not None
            else dict(
                Component="rgb(246, 37, 105)",
                Task="rgb(146, 237, 5)",
                Worker="rgb(46, 137, 205)",
            )
        )
        index_col = index_col if index_col is not None else "Type"
        df = []
        df.extend(
            self.product.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            )
        )
        df.extend(
            self.workflow.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            ),
        )
        df.extend(
            self.organization.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            )
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
        Gp = self.product.get_networkx_graph()
        Gw = self.workflow.get_networkx_graph()
        Go = self.organization.get_networkx_graph(view_workers=view_workers)
        G = nx.compose_all([Gp, Gw, Go])

        # add edge between product and workflow
        for c in self.product.component_list:
            for task in c.targeted_task_list:
                G.add_edge(c, task)

        # add edge between workflow and organization
        for team in self.organization.team_list:
            for task in team.targeted_task_list:
                G.add_edge(team, task)

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

        G = G if G is not None else self.get_networkx_graph(view_workers=view_workers)
        pos = pos if pos is not None else nx.spring_layout(G)

        # Node
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.product.component_list,
            node_color="orangered",
        )
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.workflow.task_list,
            node_color="lime",
        )
        nx.draw_networkx_nodes(
            G, pos, with_labels=with_labels, nodelist=self.organization.team_list
        )
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)

    def get_node_and_edge_trace_for_ploty_network(self, G=None, pos=None, node_size=20):
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

        Returns:
            p_node_trace: BaseProduct nodes information of plotly network.
            o_node_trace: BaseOrganization nodes information of plotly network.
            w_node_trace: BaseWorkflow nodes information of plotly network.
            edge_trace: Edge information of plotly network.
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

        p_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(color="rgb(246, 37, 105)", size=node_size,),
        )

        w_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(color="rgb(146, 237, 5)", size=node_size,),
        )

        o_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(color="rgb(46, 137, 205)", size=node_size,),
        )

        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0, color="#888"), hoverinfo="none", mode="lines"
        )

        for node in G.nodes:
            x, y = pos[node]
            if isinstance(node, BaseComponent):
                p_node_trace["x"] = p_node_trace["x"] + (x,)
                p_node_trace["y"] = p_node_trace["y"] + (y,)
                p_node_trace["text"] = p_node_trace["text"] + (node,)
            elif isinstance(node, BaseTask):
                w_node_trace["x"] = w_node_trace["x"] + (x,)
                w_node_trace["y"] = w_node_trace["y"] + (y,)
                w_node_trace["text"] = w_node_trace["text"] + (node,)
            elif isinstance(node, BaseTeam):
                o_node_trace["x"] = o_node_trace["x"] + (x,)
                o_node_trace["y"] = o_node_trace["y"] + (y,)
                o_node_trace["text"] = o_node_trace["text"] + (node,)

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace["x"] += (xposx, yposx)
            edge_trace["y"] += (xposy, yposy)

        return p_node_trace, w_node_trace, o_node_trace, edge_trace

    def draw_plotly_network(
        self,
        G=None,
        pos=None,
        title="Project",
        node_size=20,
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
                Defaults to "Project".
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
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
        (
            p_node_trace,
            w_node_trace,
            o_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_ploty_network(G, pos, node_size=node_size)
        fig = go.Figure(
            data=[edge_trace, p_node_trace, w_node_trace, o_node_trace],
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
