#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visualization helpers for BaseProject."""

from .base_product_vis import create_data_for_gantt_plotly as product_gantt_data
from .base_team_vis import create_data_for_gantt_plotly as team_gantt_data
from .base_workplace_vis import create_data_for_gantt_plotly as workplace_gantt_data
from .base_workflow_vis import create_data_for_gantt_plotly as workflow_gantt_data

from pDESy.model.base_component import BaseComponent
from pDESy.model.base_facility import BaseFacility
from pDESy.model.base_task import BaseTask
from pDESy.model.base_team import BaseTeam
from pDESy.model.base_worker import BaseWorker
from pDESy.model.base_workplace import BaseWorkplace


def create_gantt_plotly(
    project,
    title: str = "Gantt Chart",
    target_product_id_order_list: list[str] = None,
    target_component_id_order_list: list[str] = None,
    target_workflow_id_order_list: list[str] = None,
    target_task_id_order_list: list[str] = None,
    target_team_id_order_list: list[str] = None,
    target_worker_id_order_list: list[str] = None,
    target_workplace_id_order_list: list[str] = None,
    target_facility_id_order_list: list[str] = None,
    colors: dict[str, str] = None,
    index_col: str = None,
    showgrid_x: bool = True,
    showgrid_y: bool = True,
    group_tasks: bool = False,
    show_colorbar: bool = True,
    finish_margin: float = 1.0,
    save_fig_path: str = None,
):
    """Create a Gantt chart using Plotly."""
    try:
        import plotly.figure_factory as ff
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError(
            "plotly is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install plotly"
        )
    colors = (
        colors
        if colors is not None
        else {
            "Component": "rgb(246, 37, 105)",
            "Task": "rgb(146, 237, 5)",
            "Worker": "rgb(46, 137, 205)",
            "Facility": "rgb(46, 137, 205)",
        }
    )
    index_col = index_col if index_col is not None else "Type"
    df = []

    target_product_instance_list = project.product_set
    if target_product_id_order_list is not None:
        id_to_product_instance = {
            instance.ID: instance for instance in project.product_set
        }
        target_product_instance_list = [
            id_to_product_instance[tid]
            for tid in target_product_id_order_list
            if tid in id_to_product_instance
        ]
    for product in target_product_instance_list:
        df.extend(
            product_gantt_data(
                product,
                project.init_datetime,
                project.unit_timedelta,
                target_id_order_list=target_component_id_order_list,
                finish_margin=finish_margin,
            )
        )

    target_workflow_instance_list = project.workflow_set
    if target_workflow_id_order_list is not None:
        id_to_workflow_instance = {
            instance.ID: instance for instance in project.workflow_set
        }
        target_workflow_instance_list = [
            id_to_workflow_instance[tid]
            for tid in target_workflow_id_order_list
            if tid in id_to_workflow_instance
        ]
    for workflow in target_workflow_instance_list:
        df.extend(
            workflow_gantt_data(
                workflow,
                project.init_datetime,
                project.unit_timedelta,
                target_id_order_list=target_task_id_order_list,
                finish_margin=finish_margin,
            )
        )

    target_team_instance_list = project.team_set
    if target_team_id_order_list is not None:
        id_to_team_instance = {instance.ID: instance for instance in project.team_set}
        target_team_instance_list = [
            id_to_team_instance[tid]
            for tid in target_team_id_order_list
            if tid in id_to_team_instance
        ]
    for team in target_team_instance_list:
        df.extend(
            team_gantt_data(
                team,
                project.init_datetime,
                project.unit_timedelta,
                target_id_order_list=target_worker_id_order_list,
                finish_margin=finish_margin,
            )
        )

    target_workplace_instance_list = project.workplace_set
    if target_workplace_id_order_list is not None:
        id_to_workplace_instance = {
            instance.ID: instance for instance in project.workplace_set
        }
        target_workplace_instance_list = [
            id_to_workplace_instance[tid]
            for tid in target_workplace_id_order_list
            if tid in id_to_workplace_instance
        ]
    for workplace in target_workplace_instance_list:
        df.extend(
            workplace_gantt_data(
                workplace,
                project.init_datetime,
                project.unit_timedelta,
                target_id_order_list=target_facility_id_order_list,
                finish_margin=finish_margin,
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


def get_networkx_graph(project, view_workers: bool = False, view_facilities: bool = False):
    """Get the information of the project as a NetworkX directed graph."""
    try:
        import networkx as nx
    except ImportError:
        raise ImportError(
            "networkx is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install networkx"
        )
    g_product = nx.DiGraph()
    for product in project.product_set:
        g_product = nx.compose(g_product, product.get_networkx_graph())

    g_workflow = nx.DiGraph()
    for workflow in project.workflow_set:
        g_workflow = nx.compose(g_workflow, workflow.get_networkx_graph())

    g_team = nx.DiGraph()
    for team in project.team_set:
        g_team.add_node(team)
    # Build ID→instance mapping locally to avoid stale cached dicts
    team_id_to_instance = {team.ID: team for team in project.team_set}
    for team in project.team_set:
        if team.parent_team_id is not None:
            parent_team = team_id_to_instance.get(team.parent_team_id, None)
            if parent_team is not None:
                g_team.add_edge(parent_team, team)
    if view_workers:
        for team in project.team_set:
            for worker in team.worker_set:
                g_team.add_node(worker)
                g_team.add_edge(team, worker)

    g_workplace = nx.DiGraph()
    for workplace in project.workplace_set:
        g_workplace.add_node(workplace)
    # Build ID→instance mapping locally to avoid stale cached dicts
    workplace_id_to_instance = {workplace.ID: workplace for workplace in project.workplace_set}
    for workplace in project.workplace_set:
        if workplace.parent_workplace_id is not None:
            parent_workplace = workplace_id_to_instance.get(
                workplace.parent_workplace_id, None
            )
            if parent_workplace is not None:
                g_workplace.add_edge(parent_workplace, workplace)
    if view_facilities:
        for workplace in project.workplace_set:
            for facility in workplace.facility_set:
                g_workplace.add_node(facility)
                g_workplace.add_edge(workplace, facility)

    g = nx.compose_all([g_product, g_workflow, g_team, g_workplace])

    for product in project.product_set:
        for component in product.component_set:
            targeted_task_set = project.get_target_task_set(
                component.targeted_task_id_set
            )
            for task in targeted_task_set:
                g.add_edge(component, task)

    for team in project.team_set:
        targeted_task_set = project.get_target_task_set(team.targeted_task_id_set)
        for task in targeted_task_set:
            g.add_edge(team, task)

    if view_workers:
        for team in project.team_set:
            for worker in team.worker_set:
                g.add_edge(team, worker)

    for workplace in project.workplace_set:
        targeted_task_set = project.get_target_task_set(workplace.targeted_task_id_set)
        for task in targeted_task_set:
            g.add_edge(workplace, task)

    if view_facilities:
        for workplace in project.workplace_set:
            for facility in workplace.facility_set:
                g.add_edge(workplace, facility)

    return g


def draw_networkx(
    project,
    g=None,
    pos: dict = None,
    arrows: bool = True,
    component_node_color: str = "#FF6600",
    task_node_color: str = "#00EE00",
    auto_task_node_color: str = "#005500",
    team_node_color: str = "#0099FF",
    worker_node_color: str = "#D9E5FF",
    view_workers: bool = False,
    view_facilities: bool = False,
    workplace_node_color: str = "#0099FF",
    facility_node_color: str = "#D9E5FF",
    figsize: tuple[float, float] = None,
    dpi: float = 100.0,
    save_fig_path: str = None,
    **kwargs,
):
    """Draw the project structure as a NetworkX graph using matplotlib."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install matplotlib"
        )
    try:
        import networkx as nx
    except ImportError:
        raise ImportError(
            "networkx is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install networkx"
        )

    if figsize is None:
        figsize = [6.4, 4.8]
    fig = plt.figure(figsize=figsize, dpi=dpi)
    g = (
        g
        if g is not None
        else get_networkx_graph(
            project, view_workers=view_workers, view_facilities=view_facilities
        )
    )
    pos = pos if pos is not None else nx.spring_layout(g)

    # Derive node groups from the actual graph to avoid stale cached sets
    component_nodes = [n for n in g.nodes if isinstance(n, BaseComponent)]
    task_nodes = [n for n in g.nodes if isinstance(n, BaseTask)]
    normal_task_nodes = [n for n in task_nodes if not getattr(n, "auto_task", False)]
    auto_task_nodes = [n for n in task_nodes if getattr(n, "auto_task", False)]
    team_nodes = [n for n in g.nodes if isinstance(n, BaseTeam)]
    workplace_nodes = [n for n in g.nodes if isinstance(n, BaseWorkplace)]
    worker_nodes = (
        [n for n in g.nodes if isinstance(n, BaseWorker)] if view_workers else []
    )
    facility_nodes = (
        [n for n in g.nodes if isinstance(n, BaseFacility)] if view_facilities else []
    )

    nx.draw_networkx_nodes(
        g,
        pos,
        nodelist=component_nodes,
        node_color=component_node_color,
        **kwargs,
    )
    nx.draw_networkx_nodes(
        g,
        pos,
        nodelist=normal_task_nodes,
        node_color=task_node_color,
        **kwargs,
    )
    nx.draw_networkx_nodes(
        g,
        pos,
        nodelist=auto_task_nodes,
        node_color=auto_task_node_color,
    )
    nx.draw_networkx_nodes(
        g,
        pos,
        nodelist=team_nodes,
        node_color=team_node_color,
        **kwargs,
    )
    if view_workers and worker_nodes:
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=worker_nodes,
            node_color=worker_node_color,
            **kwargs,
        )

    nx.draw_networkx_nodes(
        g,
        pos,
        nodelist=workplace_nodes,
        node_color=workplace_node_color,
        **kwargs,
    )
    if view_facilities and facility_nodes:
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=facility_nodes,
            node_color=facility_node_color,
            **kwargs,
        )

    nx.draw_networkx_labels(g, pos)
    nx.draw_networkx_edges(g, pos, arrows=arrows, **kwargs)
    plt.axis("off")
    if save_fig_path is not None:
        plt.savefig(save_fig_path)
    plt.close()
    return fig


def get_node_and_edge_trace_for_plotly_network(
    project,
    g=None,
    pos: dict = None,
    node_size: int = 20,
    component_node_color: str = "#FF6600",
    task_node_color: str = "#00EE00",
    auto_task_node_color: str = "#005500",
    team_node_color: str = "#0099FF",
    worker_node_color: str = "#D9E5FF",
    view_workers: bool = False,
    workplace_node_color: str = "#0099FF",
    facility_node_color: str = "#D9E5FF",
    view_facilities: bool = False,
):
    """Get nodes and edges information for a Plotly network visualization."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError(
            "plotly is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install plotly"
        )
    try:
        import networkx as nx
    except ImportError:
        raise ImportError(
            "networkx is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install networkx"
        )
    g = (
        g
        if g is not None
        else get_networkx_graph(
            project, view_workers=view_workers, view_facilities=view_facilities
        )
    )
    pos = pos if pos is not None else nx.spring_layout(g)

    component_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": component_node_color,
            "size": node_size,
        },
    )

    task_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": task_node_color,
            "size": node_size,
        },
    )

    auto_task_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": auto_task_node_color,
            "size": node_size,
        },
    )

    team_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": team_node_color,
            "size": node_size,
        },
    )

    worker_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": worker_node_color,
            "size": node_size,
        },
    )

    workplace_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": workplace_node_color,
            "size": node_size,
        },
    )

    facility_node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": facility_node_color,
            "size": node_size,
        },
    )

    edge_trace = go.Scatter(
        x=[],
        y=[],
        line={"width": 0, "color": "#888"},
        mode="lines",
    )

    for node in g.nodes:
        x, y = pos[node]
        if isinstance(node, BaseComponent):
            component_node_trace["x"] = component_node_trace["x"] + (x,)
            component_node_trace["y"] = component_node_trace["y"] + (y,)
            component_node_trace["text"] = component_node_trace["text"] + (node,)
        elif isinstance(node, BaseTask):
            if not node.auto_task:
                task_node_trace["x"] = task_node_trace["x"] + (x,)
                task_node_trace["y"] = task_node_trace["y"] + (y,)
                task_node_trace["text"] = task_node_trace["text"] + (node,)
            elif node.auto_task:
                auto_task_node_trace["x"] = auto_task_node_trace["x"] + (x,)
                auto_task_node_trace["y"] = auto_task_node_trace["y"] + (y,)
                auto_task_node_trace["text"] = auto_task_node_trace["text"] + (node,)
        elif isinstance(node, BaseWorkplace):
            workplace_node_trace["x"] = workplace_node_trace["x"] + (x,)
            workplace_node_trace["y"] = workplace_node_trace["y"] + (y,)
            workplace_node_trace["text"] = workplace_node_trace["text"] + (node,)
        elif isinstance(node, BaseFacility):
            facility_node_trace["x"] = facility_node_trace["x"] + (x,)
            facility_node_trace["y"] = facility_node_trace["y"] + (y,)
            facility_node_trace["text"] = facility_node_trace["text"] + (node,)
        elif isinstance(node, BaseTeam):
            team_node_trace["x"] = team_node_trace["x"] + (x,)
            team_node_trace["y"] = team_node_trace["y"] + (y,)
            team_node_trace["text"] = team_node_trace["text"] + (node,)
        elif isinstance(node, BaseWorker):
            worker_node_trace["x"] = worker_node_trace["x"] + (x,)
            worker_node_trace["y"] = worker_node_trace["y"] + (y,)
            worker_node_trace["text"] = worker_node_trace["text"] + (node,)

    for edge in g.edges:
        x = edge[0]
        y = edge[1]
        x_pos_x, x_pos_y = pos[x]
        y_pos_x, y_pos_y = pos[y]
        edge_trace["x"] += (x_pos_x, y_pos_x)
        edge_trace["y"] += (x_pos_y, y_pos_y)

    return (
        component_node_trace,
        task_node_trace,
        auto_task_node_trace,
        team_node_trace,
        worker_node_trace,
        workplace_node_trace,
        facility_node_trace,
        edge_trace,
    )


def draw_plotly_network(
    project,
    g=None,
    pos: dict = None,
    title: str = "Project",
    node_size: int = 20,
    component_node_color: str = "#FF6600",
    task_node_color: str = "#00EE00",
    auto_task_node_color: str = "#005500",
    team_node_color: str = "#0099FF",
    worker_node_color: str = "#D9E5FF",
    view_workers: bool = False,
    workplace_node_color: str = "#0099FF",
    facility_node_color: str = "#D9E5FF",
    view_facilities: bool = False,
    save_fig_path: str = None,
):
    """Draw the project structure as a Plotly network graph."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError(
            "plotly is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install plotly"
        )
    try:
        import networkx as nx
    except ImportError:
        raise ImportError(
            "networkx is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install networkx"
        )
    g = (
        g
        if g is not None
        else get_networkx_graph(
            project, view_workers=view_workers, view_facilities=view_facilities
        )
    )
    pos = pos if pos is not None else nx.spring_layout(g)
    (
        component_node_trace,
        task_node_trace,
        auto_task_node_trace,
        team_node_trace,
        worker_node_trace,
        workplace_node_trace,
        facility_node_trace,
        edge_trace,
    ) = get_node_and_edge_trace_for_plotly_network(project, g, pos, node_size=node_size)
    fig = go.Figure(
        data=[
            edge_trace,
            component_node_trace,
            task_node_trace,
            auto_task_node_trace,
            team_node_trace,
            worker_node_trace,
            workplace_node_trace,
            facility_node_trace,
        ],
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
