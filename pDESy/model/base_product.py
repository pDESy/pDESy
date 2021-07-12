#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_component import BaseComponent, BaseComponentState
from .base_task import BaseTaskState
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
import datetime
import matplotlib.pyplot as plt
import warnings


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

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of BaseProduct.

        BaseComponent in `component_list` are also initialized by this function.

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        for c in self.component_list:
            c.initialize(state_info=state_info, log_info=log_info)

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

    def export_dict_json_data(self):
        """
        Export the information of this product to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type="BaseProduct",
            component_list=[c.export_dict_json_data() for c in self.component_list],
        )
        return dict_json_data

    def read_json_data(self, json_data):
        """
        Read the JSON data for creating BaseOrganization instance.

        Args:
            json_data (dict): JSON data.
        """
        j_list = json_data["component_list"]
        self.component_list = [
            BaseComponent(
                name=j["name"],
                ID=j["ID"],
                parent_component_list=j["parent_component_list"],
                child_component_list=j["child_component_list"],
                targeted_task_list=j["targeted_task_list"],
                space_size=j["space_size"],
                state=BaseComponentState(j["state"]),
                state_record_list=[
                    BaseComponentState(num) for num in j["state_record_list"]
                ],
                placed_workplace=j["placed_workplace"],
                placed_workplace_id_record=j["placed_workplace_id_record"],
            )
            for j in j_list
        ]

    def extract_none_component_list(self, target_time_list):
        """
        Extract NONE component list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract none component from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseComponent]: List of BaseComponent
        """
        return self.__extract_state_component_list(
            target_time_list, BaseComponentState.NONE
        )

    def extract_ready_component_list(self, target_time_list):
        """
        Extract READY component list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract ready component from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseComponent]: List of BaseComponent
        """
        return self.__extract_state_component_list(
            target_time_list, BaseComponentState.READY
        )

    def extract_working_component_list(self, target_time_list):
        """
        Extract WORKING component list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract working component from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseComponent]: List of BaseComponent
        """
        return self.__extract_state_component_list(
            target_time_list, BaseComponentState.WORKING
        )

    def extract_finished_component_list(self, target_time_list):
        """
        Extract FINISHED component list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract finished component from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
        Returns:
            List[BaseComponent]: List of BaseComponent
        """
        return self.__extract_state_component_list(
            target_time_list, BaseComponentState.FINISHED
        )

    def __extract_state_component_list(self, target_time_list, target_state):
        """
        Extract state component list from simulation result.

        Args:
            target_time_list (List[int]):
                Target time list.
                If you want to extract target_state component from time 2 to time 4,
                you must set [2, 3, 4] to this argument.
            target_state (BaseComponentState):
                Target state.
        Returns:
            List[BaseComponent]: List of BaseComponent
        """
        component_list = []
        for component in self.component_list:
            extract_flag = True
            for time in target_time_list:
                if len(component.state_record_list) <= time:
                    extract_flag = False
                    break
                if component.state_record_list[time] != target_state:
                    extract_flag = False
                    break
            if extract_flag:
                component_list.append(component)
        return component_list

    def reverse_log_information(self):
        """
        Reverse log information of all.
        """
        for c in self.component_list:
            c.reverse_log_information()

    def get_component_list(
        self,
        name=None,
        ID=None,
        parent_component_list=None,
        child_component_list=None,
        targeted_task_list=None,
        space_size=None,
        placed_workplace=None,
        placed_workplace_id_record=None,
    ):
        """
        Get component list by using search conditions related to BaseComponent parameter.
        If there is no searching condition, this function returns `component_list`.

        Args:
            name (str, optional):
                Target component name.
                Default to None.
            ID (str, optional):
                Target component ID.
                Default to None.
            parent_component_list (List[BaseComponent], optional):
                Target component parent_component_list.
                Default to None.
            child_component_list (List[BaseComponent], optional):
                Target component child_component_list.
                Default to None.
            targeted_task_list (List[BaseTask], optional):
                Target component targeted_task_list.
                Default to None.
            space_size (float, optional):
                Target component space_size.
                Default to None.
            placed_workplace (BaseWorkplace, optional):
                Target component placed_workplace.
                Default to None.
            placed_workplace_id_record (List[str], optional):
                Target component placed_workplace_id_record.
                Default to None.
        Returns:
            List[BaseComponent]: List of BaseComponent.
        """
        component_list = self.component_list
        if name is not None:
            component_list = list(
                filter(lambda component: component.name == name, component_list)
            )
        if ID is not None:
            component_list = list(
                filter(lambda component: component.ID == ID, component_list)
            )
        if parent_component_list is not None:
            component_list = list(
                filter(
                    lambda component: component.parent_component_list
                    == parent_component_list,
                    component_list,
                )
            )
        if child_component_list is not None:
            component_list = list(
                filter(
                    lambda component: component.child_component_list
                    == child_component_list,
                    component_list,
                )
            )
        if targeted_task_list is not None:
            component_list = list(
                filter(
                    lambda component: component.targeted_task_list
                    == targeted_task_list,
                    component_list,
                )
            )
        if space_size is not None:
            component_list = list(
                filter(
                    lambda component: component.space_size == space_size, component_list
                )
            )
        if placed_workplace is not None:
            component_list = list(
                filter(
                    lambda component: component.placed_workplace == placed_workplace,
                    component_list,
                )
            )
        if placed_workplace_id_record is not None:
            component_list = list(
                filter(
                    lambda component: component.placed_workplace_id_record
                    == placed_workplace_id_record,
                    component_list,
                )
            )
        return component_list

    def record(self):
        """
        Record placed workplace id in this time.
        """
        for c in self.component_list:
            c.record_placed_workplace_id()
            c.record_state()

    def check_state(self):
        """
        Check state
        """
        for c in self.component_list:
            c.check_state()

    def check_removing_placed_workplace(self, print_debug=False):
        """
        Check removing this product from placed_workplace or not.
        If all tasks of this product is finished, this product will be removed automatically.

        Returns:
            log_txt: List of log text about removing placed workplace.
        """
        top_component_list = list(
            filter(lambda c: len(c.parent_component_list) == 0, self.component_list)
        )

        removing_placed_workplace_component = []
        for c in top_component_list:
            all_finished_flag = all(
                map(
                    lambda task: task.state == BaseTaskState.FINISHED,
                    c.targeted_task_list,
                )
            )
            if all_finished_flag and c.placed_workplace is not None:
                removing_placed_workplace_component.append(c)

        log_txt = []
        for c in removing_placed_workplace_component:
            if print_debug:
                print(
                    "REMOVE ",
                    c.name,
                    " from ",
                    c.placed_workplace.name,
                )
            log_txt.append(
                "REMOVE " + c.name + " from " + c.placed_workplace.name,
            )
            c.placed_workplace.remove_placed_component(c)
            c.set_placed_workplace(None)
        return log_txt

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        view_ready=True,
        component_color="#FF6600",
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
                Defaults to True.
            component_color (str, optional):
                Component color setting information.
                Defaults to "#FF6600".
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
            gnt: gnt in plt.subplots()
        """
        fig, gnt = plt.subplots()
        fig.figsize = figsize
        fig.dpi = dpi
        gnt.set_xlabel("step")
        gnt.grid(True)

        yticks = [10 * (n + 1) for n in range(len(self.component_list))]
        yticklabels = [com.name for com in self.component_list]

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        for ttime in range(len(self.component_list)):
            c = self.component_list[ttime]
            (
                ready_time_list,
                working_time_list,
            ) = c.get_time_list_for_gannt_chart(finish_margin=finish_margin)
            if view_ready:
                gnt.broken_barh(
                    ready_time_list, (yticks[ttime] - 5, 9), facecolors=(ready_color)
                )
            gnt.broken_barh(
                working_time_list, (yticks[ttime] - 5, 9), facecolors=(component_color)
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
        Create data for gantt plotly from component_list.

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
            List[dict]: Gantt plotly information of this BaseProduct
        """
        df = []
        for component in self.component_list:
            df.extend(
                component.create_data_for_gantt_plotly(
                    init_datetime,
                    unit_timedelta,
                    finish_margin=finish_margin,
                    view_ready=view_ready,
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
                Defaults to None -> dict(Component="rgb(246, 37, 105)", READY="rgb(107, 127, 135)").
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
            else dict(WORKING="rgb(246, 37, 105)", READY="rgb(107, 127, 135)")
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
        component_node_color="#FF6600",
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
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
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
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

        # component
        component_list = [component for component in self.component_list]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=component_list,
            node_color=component_node_color,
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
            Now, save_fig_path can be utilized only json and html format.
            Saving figure png, jpg, svg file is not implemented...
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
