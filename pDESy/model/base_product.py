#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_product."""

import abc
import datetime
import sys
import uuid
import warnings

import matplotlib.pyplot as plt

import networkx as nx

import plotly.figure_factory as ff
import plotly.graph_objects as go

from .base_component import BaseComponent, BaseComponentState


class BaseProduct(object, metaclass=abc.ABCMeta):
    """BaseProduct.

    BaseProduct class for expressing target product in a project.
    BaseProduct consists of multiple BaseComponents.
    This class will be used as a template.

    Args:
        name (str, optional): Name of this product. Defaults to None -> "Product".
        ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
        component_set (set[BaseComponent], optional): Set of BaseComponents.
    """

    def __init__(
        self, name: str = None, ID: str = None, component_set: set[BaseComponent] = None
    ):
        """init."""
        # ----
        # Constraint parameters on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "Product"
        self.ID = ID if ID is not None else str(uuid.uuid4())

        self.component_set = set()
        if component_set is not None:
            self.update_component_set(component_set)

    def initialize(self, state_info: bool = True, log_info: bool = True):
        """
        Initialize the changeable variables of BaseProduct.

        BaseComponent in `component_set` are also initialized by this function.

        Args:
            state_info (bool, optional): Whether to initialize state information. Defaults to True.
            log_info (bool, optional): Whether to initialize log information. Defaults to True.
        """
        for c in self.component_set:
            c.initialize(state_info=state_info, log_info=log_info)

    def __str__(self):
        """Return the name list of BaseComponent.

        Returns:
            str: Name list of BaseComponent.
        """
        return f"{[str(c) for c in self.component_set]}"

    def append_component(self, component: BaseComponent):
        """
        Append target component to this workflow.

        .. deprecated:: Use add_component instead.

        Args:
            component (BaseComponent): Target component.
        """
        warnings.warn(
            "append_component is deprecated, use add_component instead.",
            DeprecationWarning,
        )
        self.add_component(component)

    def extend_component_list(self, component_set: set[BaseComponent]):
        """
        Extend target component_set to this product.

        .. deprecated:: Use update_component_set instead.

        Args:
            component_set (set[BaseComponent]): Target component set.
        """
        warnings.warn(
            "extend_component_list is deprecated, use update_component_set instead.",
            DeprecationWarning,
        )
        for component in component_set:
            self.add_component(component)

    def add_component(self, component: BaseComponent):
        """
        Add target component to this workflow.

        Args:
            component (BaseComponent): Target component.
        """
        if not isinstance(component, BaseComponent):
            raise TypeError(
                f"component must be BaseComponent, but got {type(component)}"
            )
        self.component_set.add(component)
        component.parent_product_id = self.ID

    def update_component_set(self, component_set: set[BaseComponent]):
        """
        Update target component_set to this product.

        Args:
            component_set (set[BaseComponent]): Target component set.
        """
        for component in component_set:
            if not isinstance(component, BaseComponent):
                raise TypeError(
                    f"All elements of component_set must be BaseComponent, but found {type(component)}"
                )
            self.component_set.add(component)
            component.parent_product_id = self.ID

    def create_component(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        child_component_id_set: set[str] = None,
        targeted_task_id_set: set[str] = None,
        space_size: float = None,
        # Basic variables
        state: BaseComponentState = BaseComponentState.NONE,
        state_record_list: list[BaseComponentState] = None,
        placed_workplace_id: str = None,
        placed_workplace_id_record_list: list[str] = None,
        # Advanced parameters for customized simulation
        error_tolerance: float = None,
        # Advanced variables for customized simulation
        error: float = None,
    ):
        """
        Create BaseComponent instance and add it to this product.

        Args:
            name (str, optional): Name of this component. Defaults to None -> "New Component".
            ID (str, optional): ID will be defined automatically.
            child_component_id_set (set[str], optional): Child BaseComponents id set. Defaults to None -> set().
            targeted_task_id_set (set[str], optional): Targeted tasks id set. Defaults to None -> set().
            space_size (float, optional): Space size related to base_workplace's max_space_size. Default to None -> 1.0.
            state (BaseComponentState, optional): State of this task in simulation. Defaults to BaseComponentState.NONE.
            state_record_list (List[BaseComponentState], optional): Record list of state. Defaults to None -> [].
            placed_workplace_id (str, optional): A workplace which this component is placed in simulation. Defaults to None.
            placed_workplace_id_record_list (List[str], optional): Record of placed workplace ID in simulation. Defaults to None -> [].
            error_tolerance (float, optional): Advanced parameter.
            error (float, optional): Advanced variables.

        Returns:
            BaseComponent: The created component.
        """
        component = BaseComponent(
            name=name,
            ID=ID,
            child_component_id_set=child_component_id_set,
            targeted_task_id_set=targeted_task_id_set,
            space_size=space_size,
            state=state,
            state_record_list=state_record_list,
            placed_workplace_id=placed_workplace_id,
            placed_workplace_id_record_list=placed_workplace_id_record_list,
            error_tolerance=error_tolerance,
            error=error,
        )
        self.add_component(component)
        return component

    def export_dict_json_data(self):
        """
        Export the information of this product to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type=self.__class__.__name__,
            name=self.name,
            ID=self.ID,
            component_set=[c.export_dict_json_data() for c in self.component_set],
        )
        return dict_json_data

    def read_json_data(self, json_data: dict):
        """
        Read the JSON data for creating BaseProduct instance.

        Args:
            json_data (dict): JSON data.
        """
        self.name = json_data["name"]
        self.ID = json_data["ID"]
        j_list = json_data["component_set"]
        self.component_set = {
            BaseComponent(
                name=j["name"],
                ID=j["ID"],
                child_component_id_set=set(j["child_component_id_set"]),
                targeted_task_id_set=set(j["targeted_task_id_set"]),
                space_size=j["space_size"],
                state=BaseComponentState(j["state"]),
                state_record_list=[
                    BaseComponentState(num) for num in j["state_record_list"]
                ],
                placed_workplace_id=j["placed_workplace_id"],
                placed_workplace_id_record_list=j["placed_workplace_id_record_list"],
            )
            for j in j_list
        }

    def extract_none_component_set(self, target_time_list: list[int]):
        """
        Extract NONE component set from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract none component from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseComponent]: List of BaseComponent.
        """
        return self.__extract_state_component_set(
            target_time_list, BaseComponentState.NONE
        )

    def extract_ready_component_set(self, target_time_list: list[int]):
        """
        Extract READY component set from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract ready component from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseComponent]: List of BaseComponent.
        """
        return self.__extract_state_component_set(
            target_time_list, BaseComponentState.READY
        )

    def extract_working_component_set(self, target_time_list: list[int]):
        """
        Extract WORKING component set from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract working component from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseComponent]: List of BaseComponent.
        """
        return self.__extract_state_component_set(
            target_time_list, BaseComponentState.WORKING
        )

    def extract_finished_component_set(self, target_time_list: list[int]):
        """
        Extract FINISHED component set from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract finished component from time 2 to time 4, you must set [2, 3, 4] to this argument.

        Returns:
            List[BaseComponent]: List of BaseComponent.
        """
        return self.__extract_state_component_set(
            target_time_list, BaseComponentState.FINISHED
        )

    def __extract_state_component_set(
        self, target_time_list: list[int], target_state: BaseComponentState
    ):
        """
        Extract state component set from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract target_state component from time 2 to time 4, you must set [2, 3, 4] to this argument.
            target_state (BaseComponentState): Target state.

        Returns:
            List[BaseComponent]: List of BaseComponent.
        """
        return {
            component
            for component in self.component_set
            if all(
                len(component.state_record_list) > time
                and component.state_record_list[time] == target_state
                for time in target_time_list
            )
        }

    def reverse_log_information(self):
        """Reverse log information of all."""
        for c in self.component_set:
            c.reverse_log_information()

    def record(self, working=True):
        """Record placed workplace id in this time.

        Args:
            working (bool, optional): Whether to record as working. Defaults to True.
        """
        for c in self.component_set:
            c.record_placed_workplace_id()
            c.record_state(working=working)

    def remove_absence_time_list(self, absence_time_list: list[int]):
        """
        Remove record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]): List of absence step time in simulation.
        """
        for c in self.component_set:
            c.remove_absence_time_list(absence_time_list)

    def insert_absence_time_list(self, absence_time_list: list[int]):
        """
        Insert record information on `absence_time_list`.

        Args:
            absence_time_list (List[int]): List of absence step time in simulation.
        """
        for c in self.component_set:
            c.insert_absence_time_list(absence_time_list)

    def print_log(self, target_step_time: int):
        """
        Print log in `target_step_time`.

        Args:
            target_step_time (int): Target step time of printing log.
        """
        for component in self.component_set:
            component.print_log(target_step_time)

    def print_all_log_in_chronological_order(self, backward: bool = False):
        """
        Print all log in chronological order.

        Args:
            backward (bool, optional): If True, print logs in reverse order. Defaults to False.
        """
        if len(self.component_set) > 0:
            sample_component = next(iter(self.component_set))
            n = len(sample_component.state_record_list)
            if backward:
                for i in range(n):
                    t = n - 1 - i
                    print("TIME: ", t)
                    self.print_log(t)
            else:
                for t in range(n):
                    print("TIME: ", t)
                    self.print_log(t)

    def plot_simple_gantt(
        self,
        target_id_order_list: list[str] = None,
        finish_margin: float = 1.0,
        print_product_name: bool = True,
        view_ready: bool = True,
        component_color: str = "#FF6600",
        ready_color: str = "#C0C0C0",
        figsize: tuple[float, float] = None,
        dpi: float = 100.0,
        save_fig_path: str = None,
    ):
        """
        Plot Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_product_name (bool, optional): Print product name or not. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to True.
            component_color (str, optional): Component color setting information. Defaults to "#FF6600".
            ready_color (str, optional): Ready color setting information. Defaults to "#C0C0C0".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            fig: Figure in plt.subplots().
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig, gnt = self.create_simple_gantt(
            target_id_order_list=target_id_order_list,
            finish_margin=finish_margin,
            print_product_name=print_product_name,
            view_ready=view_ready,
            component_color=component_color,
            ready_color=ready_color,
            figsize=figsize,
            dpi=dpi,
            save_fig_path=save_fig_path,
        )
        _ = gnt
        return fig

    def create_simple_gantt(
        self,
        target_id_order_list: list[str] = None,
        finish_margin: float = 1.0,
        print_product_name: bool = True,
        view_ready: bool = True,
        component_color: str = "#FF6600",
        ready_color: str = "#C0C0C0",
        figsize: tuple[float, float] = None,
        dpi: float = 100.0,
        save_fig_path: str = None,
    ):
        """
        Create Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            view_ready (bool, optional): View READY time or not. Defaults to True.
            print_product_name (bool, optional): Print product name or not. Defaults to True.
            component_color (str, optional): Component color setting information. Defaults to "#FF6600".
            ready_color (str, optional): Ready color setting information. Defaults to "#C0C0C0".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            fig: Figure in plt.subplots().
            gnt: Axes in plt.subplots().
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig, gnt = plt.subplots()
        fig.figsize = figsize
        fig.dpi = dpi
        gnt.set_xlabel("step")
        gnt.grid(True)

        target_instance_list = self.component_set
        if target_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.component_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_id_order_list
                if tid in id_to_instance
            ]

        target_instance_list = list(reversed(list(target_instance_list)))

        y_ticks = [10 * (n + 1) for n in range(len(target_instance_list))]
        y_tick_labels = [com.name for com in target_instance_list]
        if print_product_name:
            y_tick_labels = [f"{self.name}: {com.name}" for com in target_instance_list]

        gnt.set_yticks(y_ticks)
        gnt.set_yticklabels(y_tick_labels)

        for time, c in enumerate(target_instance_list):
            (
                ready_time_list,
                working_time_list,
            ) = c.get_time_list_for_gantt_chart(finish_margin=finish_margin)
            if view_ready:
                gnt.broken_barh(
                    ready_time_list, (y_ticks[time] - 5, 9), facecolors=(ready_color)
                )
            gnt.broken_barh(
                working_time_list, (y_ticks[time] - 5, 9), facecolors=(component_color)
            )

        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig, gnt

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        target_id_order_list: list[str] = None,
        finish_margin: float = 1.0,
        print_product_name: bool = True,
        view_ready: bool = False,
    ):
        """
        Create data for gantt plotly from component_set.

        Args:
            init_datetime (datetime.datetime): Start datetime of project.
            unit_timedelta (datetime.timedelta): Unit time of simulation.
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_product_name (bool, optional): Print product name or not. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to False.

        Returns:
            List[dict]: Gantt plotly information of this BaseProduct.
        """
        df = []
        target_instance_list = self.component_set
        if target_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.component_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_id_order_list
                if tid in id_to_instance
            ]
        for component in target_instance_list:
            (
                ready_time_list,
                working_time_list,
            ) = component.get_time_list_for_gantt_chart(finish_margin=finish_margin)

            task_name = component.name
            if print_product_name:
                task_name = f"{self.name}: {component.name}"

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
                            "Type": "Component",
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
                        "Type": "Component",
                    }
                )
        return df

    def create_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        target_id_order_list: list[str] = None,
        title: str = "Gantt Chart",
        colors: dict[str, str] = None,
        index_col: str = None,
        showgrid_x: bool = True,
        showgrid_y: bool = True,
        group_tasks: bool = True,
        show_colorbar: bool = True,
        finish_margin: float = 1.0,
        print_product_name: bool = True,
        view_ready: bool = False,
        save_fig_path: str = None,
    ):
        """
        Create Gantt chart by plotly.

        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime): Start datetime of project.
            unit_timedelta (datetime.timedelta): Unit time of simulation.
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            title (str, optional): Title of Gantt chart. Defaults to "Gantt Chart".
            colors (Dict[str, str], optional): Color setting of plotly Gantt chart. Defaults to None -> dict(Component="rgb(246, 37, 105)", READY="rgb(107, 127, 135)").
            index_col (str, optional): index_col of plotly Gantt chart. Defaults to None -> "State".
            showgrid_x (bool, optional): showgrid_x of plotly Gantt chart. Defaults to True.
            showgrid_y (bool, optional): showgrid_y of plotly Gantt chart. Defaults to True.
            group_tasks (bool, optional): group_tasks of plotly Gantt chart. Defaults to True.
            show_colorbar (bool, optional): show_colorbar of plotly Gantt chart. Defaults to True.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_product_name (bool, optional): Print product name or not. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to False.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            figure: Figure for a gantt chart.
        """
        colors = (
            colors
            if colors is not None
            else {"WORKING": "rgb(246, 37, 105)", "READY": "rgb(107, 127, 135)"}
        )
        index_col = index_col if index_col is not None else "State"
        df = self.create_data_for_gantt_plotly(
            init_datetime,
            unit_timedelta,
            target_id_order_list=target_id_order_list,
            finish_margin=finish_margin,
            print_product_name=print_product_name,
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

    def get_networkx_graph(self):
        """
        Get the information of networkx graph.

        Returns:
            networkx.DiGraph: Directed graph of the product.
        """
        g = nx.DiGraph()

        # 1. add all nodes
        for component in self.component_set:
            g.add_node(component)

        id_to_component = {c.ID: c for c in self.component_set}

        # 2. add all edges
        for component in self.component_set:
            for child_c_id in component.child_component_id_set:
                child_c = id_to_component.get(child_c_id, None)
                if child_c is not None:
                    g.add_edge(component, child_c)

        return g

    def draw_networkx(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        arrows: bool = True,
        component_node_color: str = "#FF6600",
        figsize: tuple[float, float] = None,
        dpi: float = 100.0,
        save_fig_path: str = None,
        **kwargs,
    ):
        """
        Draw networkx.

        Args:
            g (networkx.Digraph, optional): The information of networkx graph. Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional): Layout of networkx. Defaults to None -> networkx.spring_layout(g).
            arrows (bool, optional): Digraph or Graph(no arrows). Defaults to True.
            component_node_color (str, optional): Node color setting information. Defaults to "#FF6600".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.
            **kwargs: Other networkx settings.

        Returns:
            figure: Figure for a network.
        """
        if figsize is None:
            figsize = [6.4, 4.8]
        fig = plt.figure(figsize=figsize, dpi=dpi)
        g = g if g is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(g)

        # component
        component_set = self.component_set
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=component_set,
            node_color=component_node_color,
            **kwargs,
        )

        nx.draw_networkx_labels(g, pos, **kwargs)
        nx.draw_networkx_edges(g, pos, arrows=arrows, **kwargs)
        plt.axis("off")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        plt.close()
        return fig

    def get_node_and_edge_trace_for_plotly_network(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        node_size: int = 20,
        component_node_color: str = "#FF6600",
    ):
        """
        Get nodes and edges information of plotly network.

        Args:
            g (networkx.Digraph, optional): The information of networkx graph. Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional): Layout of networkx. Defaults to None -> networkx.spring_layout(g).
            node_size (int, optional): Node size setting information. Defaults to 20.
            component_node_color (str, optional): Node color setting information. Defaults to "#FF6600".

        Returns:
            node_trace: Node information of plotly network.
            edge_trace: Edge information of plotly network.
        """
        g = g if g is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(g)

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            marker={"color": component_node_color, "size": node_size},
        )

        for node in g.nodes:
            x, y = pos[node]
            node_trace["x"] = node_trace["x"] + (x,)
            node_trace["y"] = node_trace["y"] + (y,)
            node_trace["text"] = node_trace["text"] + (node,)

        edge_trace = go.Scatter(
            x=[],
            y=[],
            line={"width": 1, "color": "#888"},
            mode="lines",
        )

        for edge in g.edges:
            x = edge[0]
            y = edge[1]
            x_pos_x, x_pos_y = pos[x]
            y_pos_x, y_pos_y = pos[y]
            edge_trace["x"] += (x_pos_x, y_pos_x)
            edge_trace["y"] += (x_pos_y, y_pos_y)
        return node_trace, edge_trace

    def draw_plotly_network(
        self,
        g: nx.DiGraph = None,
        pos: dict = None,
        title: str = "Product",
        node_size: int = 20,
        component_node_color: str = "#FF6600",
        save_fig_path: str = None,
    ):
        """
        Draw plotly network.

        Args:
            g (networkx.Digraph, optional): The information of networkx graph. Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional): Layout of networkx. Defaults to None -> networkx.spring_layout(g).
            title (str, optional): Figure title of this network. Defaults to "Product".
            node_size (int, optional): Node size setting information. Defaults to 20.
            component_node_color (str, optional): Node color setting information. Defaults to "#FF6600".
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            figure: Figure for a network.
        """
        g = g if g is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(g)
        node_trace, edge_trace = self.get_node_and_edge_trace_for_plotly_network(
            g, pos, node_size=node_size, component_node_color=component_node_color
        )
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=title,
                showlegend=False,
                annotations=[
                    {
                        "ax": edge_trace["x"][index * 2],
                        "ay": edge_trace["y"][index * 2],
                        "axref": "x",
                        "ayref": "y",
                        "x": edge_trace["x"][index * 2 + 1],
                        "y": edge_trace["y"][index * 2 + 1],
                        "xref": "x",
                        "yref": "y",
                        "showarrow": True,
                        "arrowhead": 5,
                    }
                    for index in range(0, int(len(edge_trace["x"]) / 2))
                ],
                xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            ),
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

    def get_target_component_mermaid_diagram(
        self,
        target_component_set: set[BaseComponent],
        shape_component: str = "odd",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of target component.

        Args:
            target_component_set (set[BaseComponent]): Target component set.
            shape_component (str, optional): Shape of mermaid diagram. Defaults to "odd".
            link_type_str (str, optional): Link type of mermaid diagram. Defaults to "-->".
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for component in target_component_set:
            if component in self.component_set:
                list_of_lines.extend(
                    component.get_mermaid_diagram(
                        shape=shape_component,
                    )
                )

        for component in target_component_set:
            if component in self.component_set:
                for child_component_id in component.child_component_id_set:
                    if child_component_id in [c.ID for c in target_component_set]:
                        list_of_lines.append(
                            f"{component.ID}{link_type_str}{child_component_id}"
                        )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def get_mermaid_diagram(
        self,
        shape_component: str = "odd",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this product.

        Args:
            shape_component (str, optional): Shape of mermaid diagram. Defaults to "odd".
            link_type_str (str, optional): Link type of mermaid diagram. Defaults to "-->".
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        list_of_lines = []
        if subgraph:
            list_of_lines.append(f"subgraph {self.ID}[{self.name}]")
            list_of_lines.append(f"direction {subgraph_direction}")

        for component in self.component_set:
            list_of_lines.extend(
                component.get_mermaid_diagram(
                    shape=shape_component,
                )
            )

        for component in self.component_set:
            for child_component_id in component.child_component_id_set:
                list_of_lines.append(
                    f"{component.ID}{link_type_str}{child_component_id}"
                )

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_target_component_mermaid_diagram(
        self,
        target_component_set: set[BaseComponent],
        orientations: str = "LR",
        shape_component: str = "odd",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of target component.

        Args:
            target_component_set (set[BaseComponent]): Target component set.
            orientations (str, optional): Orientation of mermaid diagram. See: https://mermaid.js.org/syntax/flowchart.html#direction. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram. Defaults to "odd".
            link_type_str (str, optional): Link type of mermaid diagram. Defaults to "-->".
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
        """
        print(f"flowchart {orientations}")
        list_of_lines = self.get_target_component_mermaid_diagram(
            target_component_set=target_component_set,
            shape_component=shape_component,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print(*list_of_lines, sep="\n")

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        shape_component: str = "odd",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this product.

        Args:
            orientations (str, optional): Orientation of mermaid diagram. See: https://mermaid.js.org/syntax/flowchart.html#direction. Defaults to "LR".
            shape_component (str, optional): Shape of mermaid diagram. Defaults to "odd".
            link_type_str (str, optional): Link type of mermaid diagram. Defaults to "-->".
            subgraph (bool, optional): Subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
        """
        self.print_target_component_mermaid_diagram(
            target_component_set=self.component_set,
            orientations=orientations,
            shape_component=shape_component,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def get_gantt_mermaid(
        self,
        target_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get mermaid diagram of Gantt chart.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            section (bool, optional): Section or not. Defaults to True.
            range_time (tuple[int, int], optional): Range of Gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): If True, detailed information is included in gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for detailed information. Defaults to None.

        Returns:
            list[str]: List of lines for mermaid diagram.
        """
        target_instance_list = self.component_set
        if target_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in self.component_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_id_order_list
                if tid in id_to_instance
            ]

        list_of_lines = []
        if section:
            list_of_lines.append(f"section {self.name}")
        for component in target_instance_list:
            list_of_lines.extend(
                component.get_gantt_mermaid_data(
                    range_time=range_time,
                    view_ready=view_ready,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_gantt_mermaid(
        self,
        target_id_order_list: list[str] = None,
        date_format: str = "X",
        axis_format: str = "%s",
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Print mermaid diagram of Gantt chart.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            date_format (str, optional): Date format of mermaid diagram. Defaults to "X".
            axis_format (str, optional): Axis format of mermaid diagram. Defaults to "%s".
            section (bool, optional): Section or not. Defaults to True.
            range_time (tuple[int, int], optional): Range of Gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): If True, detailed information is included in gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for detailed information. Defaults to None.
        """
        print("gantt")
        print(f"dateFormat {date_format}")
        print(f"axisFormat {axis_format}")
        list_of_lines = self.get_gantt_mermaid(
            target_id_order_list=target_id_order_list,
            section=section,
            range_time=range_time,
            view_ready=view_ready,
            detailed_info=detailed_info,
            id_name_dict=id_name_dict,
        )
        print(*list_of_lines, sep="\n")
