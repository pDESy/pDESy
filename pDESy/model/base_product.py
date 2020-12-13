#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_component import BaseComponent
from .base_task import BaseTaskState
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
import datetime
import matplotlib.pyplot as plt


class BaseProduct(object, metaclass=abc.ABCMeta):
    """BaseProduct
    BaseProduct class for expressing target product in a project.
    BaseProduct is consist of multiple BaseComponents.
    This class will be used as template.

    Args:
        component_list (List[BaseComponent]):
            List of BaseComponents
    """

    def __init__(self, component_list: List[BaseComponent]):
        # ----
        # Constraint parameters on simulation
        # --
        # Basic parameter
        self.component_list = component_list

    def initialize(self):
        """
        Initialize the changeable variables of BaseProduct

        - changeable variables of BaseComponent in component_list
        """
        for c in self.component_list:
            c.initialize()

    def __str__(self):
        """
        Returns:
            str: name list of BaseComponent
        Examples:
            >>> p = BaseProduct([BaseComponent('c')])
            >>> print([c.name for c in p.component_list])
            ['c']
        """
        return "{}".format(list(map(lambda c: str(c), self.component_list)))

    def record_placed_factory_id(self):
        """
        Record placed factory id in this time.
        """
        for c in self.component_list:
            c.record_placed_factory_id()

    def check_removing_placed_factory(self):
        """
        Check removing this product from placed_factory or not.
        If all tasks of this product is finished, this product will be removed automatically.
        """
        top_component_list = list(
            filter(lambda c: len(c.parent_component_list) == 0, self.component_list)
        )

        removing_placed_factory_component = []
        for c in top_component_list:
            all_finished_flag = all(
                map(
                    lambda task: task.state == BaseTaskState.FINISHED,
                    c.targeted_task_list,
                )
            )
            if all_finished_flag and c.placed_factory is not None:
                removing_placed_factory_component.append(c)

        for c in removing_placed_factory_component:
            print(
                "REMOVE ",
                c.name,
                " from ",
                c.placed_factory.name,
            )
            c.placed_factory.remove_placed_component(c)
            c.set_placed_factory(None)

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        view_auto_task=False,
        view_ready=True,
        component_color="#FF6600",
        ready_color="#C0C0C0",
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
            view_auto_task (bool, optional):
                View auto_task or not.
                Defaults to False.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to True.
            component_color (str, optional):
                Component color setting information.
                Defaults to "#FF6600".
            ready_color (str, optional):
                Ready color setting information.
                Defaults to "#C0C0C0".
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
            gnt: gnt in plt.subplots()
        """
        fig, gnt = plt.subplots()
        gnt.set_xlabel("step")
        gnt.grid(True)

        yticks = [10 * (n + 1) for n in range(len(self.component_list))]
        yticklabels = [com.name for com in self.component_list]

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        for ttime in range(len(self.component_list)):
            com = self.component_list[ttime]
            target_task_list = com.targeted_task_list
            if not view_auto_task:
                target_task_list = list(
                    filter(lambda task: not task.auto_task, com.targeted_task_list)
                )

            if view_ready:
                # 1. READY periods of all tasks are described.
                for task in target_task_list:
                    rlist = []
                    for wtime in range(len(task.start_time_list)):
                        rlist.append(
                            (
                                task.ready_time_list[wtime] + finish_margin,
                                task.start_time_list[wtime]
                                - task.ready_time_list[wtime],
                            )
                        )
                    gnt.broken_barh(
                        rlist, (yticks[ttime] - 5, 9), facecolors=(ready_color)
                    )

            # 2. WORKING periods of all tasks are described.
            for task in target_task_list:
                wlist = []
                for wtime in range(len(task.start_time_list)):
                    wlist.append(
                        (
                            task.start_time_list[wtime],
                            task.finish_time_list[wtime]
                            - task.start_time_list[wtime]
                            + finish_margin,
                        )
                    )
                gnt.broken_barh(
                    wlist, (yticks[ttime] - 5, 9), facecolors=(component_color)
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
        Create data for gantt plotly from component_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
        Returns:
            List[dict]: Gantt plotly information of this BaseProduct
        """
        df = []
        for component in self.component_list:
            df.extend(
                component.create_data_for_gantt_plotly(
                    init_datetime, unit_timedelta, finish_margin=finish_margin
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
                Defaults to None -> dict(Component="rgb(246, 37, 105)").
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
        colors = colors if colors is not None else dict(Component="rgb(246, 37, 105)")
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
            print("--- Sorry, save fig is not implemented now.---")
        #     plotly.io.write_image(fig, save_fig_path)

        return fig

    def get_networkx_graph(self):
        """
        Get the information of networkx graph.

        Returns:
            G: networkx.Digraph()
        """
        G = nx.DiGraph()

        # 1. add all nodes
        for component in self.component_list:
            G.add_node(component)

        # 2. add all edges
        for component in self.component_list:
            for child_c in component.child_component_list:
                G.add_edge(component, child_c)

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        with_labels=True,
        component_node_color="#FF6600",
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
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)
        return nx.draw_networkx(
            G,
            pos=pos,
            arrows=arrows,
            with_labels=with_labels,
            node_color=component_node_color,
            **kwds,
        )

    def get_node_and_edge_trace_for_plotly_network(
        self, G=None, pos=None, node_size=20, component_node_color="#FF6600"
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
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".

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
            marker=dict(
                color=component_node_color,
                size=node_size,
            ),
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
        title="Product",
        node_size=20,
        component_node_color="#FF6600",
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
                Defaults to "Product".
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network

        TODO:
            Saving figure file is not implemented...
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)
        node_trace, edge_trace = self.get_node_and_edge_trace_for_plotly_network(
            G, pos, node_size=node_size, component_node_color=component_node_color
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
        if save_fig_path is not None:
            print("--- Sorry, save fig is not implemented now.---")
        #     plotly.io.write_image(fig, save_fig_path)

        return fig
