#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_product."""

import abc
import datetime
import sys
import uuid
import warnings


from .base_component import BaseComponent, BaseComponentState
from .mermaid_utils import (
    CollectionMermaidDiagramMixin,
    convert_steps_to_datetime_gantt_mermaid,
    print_mermaid_diagram as print_mermaid_diagram_lines,
)
from .pdesy_utils import CollectionCommonMixin, CollectionLogJsonMixin


class BaseProduct(
    CollectionMermaidDiagramMixin,
    CollectionCommonMixin,
    CollectionLogJsonMixin,
    object,
    metaclass=abc.ABCMeta,
):
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

    def _iter_log_children(self):
        return self.component_set

    def _iter_absence_children(self):
        return self.component_set

    def _get_reverse_log_lists(self) -> list[list]:
        return []

    def _record_child_before_state(self, child) -> None:
        child.record_placed_workplace_id()

    def _get_export_dict_extra_fields(self) -> dict:
        return {"component_set": [c.export_dict_json_data() for c in self.component_set]}

    def _read_json_extra_fields(self, json_data: dict) -> None:
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

    def get_component_set_by_state(
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

    def record(self, working=True):
        """Record placed workplace id in this time.

        Args:
            working (bool, optional): Whether to record as working. Defaults to True.
        """
        super().record(working=working)

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

        Raises:
            ImportError: If matplotlib is not installed.
        """
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.plot_simple_gantt(
            self,
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

        Raises:
            ImportError: If matplotlib is not installed.
        """
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.create_simple_gantt(
            self,
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
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.create_data_for_gantt_plotly(
            self,
            init_datetime,
            unit_timedelta,
            target_id_order_list=target_id_order_list,
            finish_margin=finish_margin,
            print_product_name=print_product_name,
            view_ready=view_ready,
        )

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

        Raises:
            ImportError: If plotly is not installed.
        """
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.create_gantt_plotly(
            self,
            init_datetime,
            unit_timedelta,
            target_id_order_list=target_id_order_list,
            title=title,
            colors=colors,
            index_col=index_col,
            showgrid_x=showgrid_x,
            showgrid_y=showgrid_y,
            group_tasks=group_tasks,
            show_colorbar=show_colorbar,
            finish_margin=finish_margin,
            print_product_name=print_product_name,
            view_ready=view_ready,
            save_fig_path=save_fig_path,
        )

    def get_networkx_graph(self):
        """
        Get the information of networkx graph.

        Returns:
            networkx.DiGraph: Directed graph of the product.
        """
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.get_networkx_graph(self)

    def draw_networkx(
        self,
        g=None,
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

        Raises:
            ImportError: If matplotlib is not installed.
        """
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.draw_networkx(
            self,
            g=g,
            pos=pos,
            arrows=arrows,
            node_color=component_node_color,
            figsize=figsize,
            dpi=dpi,
            save_fig_path=save_fig_path,
            **kwargs,
        )

    def get_node_and_edge_trace_for_plotly_network(
        self,
        g=None,
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

        Raises:
            ImportError: If plotly is not installed.
        """
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.get_node_and_edge_trace_for_plotly_network(
            self,
            g=g,
            pos=pos,
            node_size=node_size,
            node_color=component_node_color,
        )

    def draw_plotly_network(
        self,
        g=None,
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

        Raises:
            ImportError: If plotly is not installed.
        """
        from pDESy.visualization import base_product_vis as product_viz

        return product_viz.draw_plotly_network(
            self,
            g=g,
            pos=pos,
            title=title,
            node_size=node_size,
            node_color=component_node_color,
            save_fig_path=save_fig_path,
        )

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

        def node_builder(component: BaseComponent) -> list[str]:
            return component.get_mermaid_diagram(shape=shape_component)

        def edge_builder(filtered_targets: list[BaseComponent]) -> list[str]:
            edge_lines = []
            target_component_id_set = {component.ID for component in filtered_targets}
            for component in filtered_targets:
                for child_component_id in component.child_component_id_set:
                    if child_component_id in target_component_id_set:
                        edge_lines.append(
                            f"{component.ID}{link_type_str}{child_component_id}"
                        )
            return edge_lines

        return self._build_target_collection_mermaid_diagram(
            target_set=target_component_set,
            owner_set=self.component_set,
            subgraph=subgraph,
            subgraph_name=f"{self.ID}[{self.name}]",
            subgraph_direction=subgraph_direction,
            node_builder=node_builder,
            edge_builder=edge_builder,
        )

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
        return self.get_target_component_mermaid_diagram(
            target_component_set=self.component_set,
            shape_component=shape_component,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

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
        list_of_lines = self.get_target_component_mermaid_diagram(
            target_component_set=target_component_set,
            shape_component=shape_component,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print_mermaid_diagram_lines(orientations, list_of_lines)

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
        super().print_mermaid_diagram(
            orientations=orientations,
            shape_component=shape_component,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def get_gantt_mermaid_steps(
        self,
        target_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get mermaid diagram of Gantt chart (step-based).

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
        def steps_builder(component, **kwargs):
            return component.get_gantt_mermaid_steps_data(**kwargs)

        return self._build_collection_gantt_mermaid_steps(
            target_instance_set=self.component_set,
            target_id_order_list=target_id_order_list,
            section=section,
            section_name=self.name,
            range_time=range_time,
            view_ready=view_ready,
            detailed_info=detailed_info,
            id_name_dict=id_name_dict,
            steps_builder=steps_builder,
        )

    def get_gantt_mermaid_text(
        self,
        project_init_datetime: datetime.datetime,
        project_unit_timedelta: datetime.timedelta,
        target_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Get mermaid diagram text of Gantt chart.

        Args:
            project_init_datetime (datetime.datetime, optional): Start datetime of project.
            project_unit_timedelta (datetime.timedelta, optional): Unit time of simulation.
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            section (bool, optional): Section or not. Defaults to True.
            range_time (tuple[int, int], optional): Range of Gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): If True, detailed information is included in gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for detailed information. Defaults to None.

        Returns:
            str: Mermaid gantt diagram text.
        """
        list_of_lines = self.get_gantt_mermaid_steps(
            target_id_order_list=target_id_order_list,
            section=section,
            range_time=range_time,
            view_ready=view_ready,
            detailed_info=detailed_info,
            id_name_dict=id_name_dict,
        )
        return convert_steps_to_datetime_gantt_mermaid(
            list_of_lines, project_init_datetime, project_unit_timedelta
        )

    def print_gantt_mermaid(
        self,
        project_init_datetime: datetime.datetime = None,
        project_unit_timedelta: datetime.timedelta = None,
        target_id_order_list: list[str] = None,
        section: bool = True,
        range_time: tuple[int, int] = (0, sys.maxsize),
        view_ready: bool = False,
        detailed_info: bool = False,
        id_name_dict: dict[str, str] = None,
    ):
        """
        Print mermaid diagram of Gantt chart.

        Args:
            project_init_datetime (datetime.datetime, optional): Start datetime of project.
                If None, outputs step-based Gantt chart. Defaults to None.
            project_unit_timedelta (datetime.timedelta, optional): Unit time of simulation.
                Required if project_init_datetime is provided. Defaults to None.
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            section (bool, optional): Section or not. Defaults to True.
            range_time (tuple[int, int], optional): Range of Gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): If True, ready tasks are included in gantt chart. Defaults to False.
            detailed_info (bool, optional): If True, detailed information is included in gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary of ID and name for detailed information. Defaults to None.
        """
        if project_init_datetime is not None and project_unit_timedelta is None:
            raise ValueError(
                "project_unit_timedelta must be provided when project_init_datetime is specified"
            )
        
        if project_init_datetime is None:
            # Step-based output
            list_of_lines = self.get_gantt_mermaid_steps(
                target_id_order_list=target_id_order_list,
                section=section,
                range_time=range_time,
                view_ready=view_ready,
                detailed_info=detailed_info,
                id_name_dict=id_name_dict,
            )
            print("gantt")
            print("    dateFormat X")
            print("    axisFormat %s")
            print(*list_of_lines, sep="\n")
        else:
            # Datetime-based output
            text = self.get_gantt_mermaid_text(
                project_init_datetime=project_init_datetime,
                project_unit_timedelta=project_unit_timedelta,
                target_id_order_list=target_id_order_list,
                section=section,
                range_time=range_time,
                view_ready=view_ready,
                detailed_info=detailed_info,
                id_name_dict=id_name_dict,
            )
            print(text)
