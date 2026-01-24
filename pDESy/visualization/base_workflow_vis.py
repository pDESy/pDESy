#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visualization helpers for BaseWorkflow."""

import datetime


def plot_simple_gantt(
    workflow,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_workflow_name: bool = True,
    view_auto_task: bool = False,
    view_ready: bool = False,
    task_color: str = "#00EE00",
    auto_task_color: str = "#005500",
    ready_color: str = "#C0C0C0",
    figsize: tuple[float, float] = None,
    dpi: float = 100.0,
    save_fig_path: str = None,
):
    """
    Plot Gantt chart by matplotlib.

    In this Gantt chart, datetime information is not included.
    This method will be used after simulation.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install matplotlib"
        )
    if figsize is None:
        figsize = [6.4, 4.8]
    fig, gnt = create_simple_gantt(
        workflow,
        target_id_order_list=target_id_order_list,
        finish_margin=finish_margin,
        print_workflow_name=print_workflow_name,
        view_auto_task=view_auto_task,
        view_ready=view_ready,
        task_color=task_color,
        auto_task_color=auto_task_color,
        ready_color=ready_color,
        figsize=figsize,
        dpi=dpi,
        save_fig_path=save_fig_path,
    )
    _ = gnt
    return fig


def create_simple_gantt(
    workflow,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_workflow_name: bool = True,
    view_auto_task: bool = False,
    view_ready: bool = False,
    task_color: str = "#00EE00",
    auto_task_color: str = "#005500",
    ready_color: str = "#C0C0C0",
    figsize: tuple[float, float] = None,
    dpi: float = 100.0,
    save_fig_path: str = None,
):
    """
    Create Gantt chart by matplotlib.

    In this Gantt chart, datetime information is not included.
    This method will be used after simulation.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install matplotlib"
        )
    if figsize is None:
        figsize = [6.4, 4.8]
    fig, gnt = plt.subplots()
    fig.figsize = figsize
    fig.dpi = dpi
    gnt.set_xlabel("step")
    gnt.grid(True)

    target_task_set = set(filter(lambda task: not task.auto_task, workflow.task_set))
    if view_auto_task:
        target_task_set = workflow.task_set

    target_instance_list = target_task_set
    if target_id_order_list is not None:
        id_to_instance = {instance.ID: instance for instance in target_task_set}
        target_instance_list = [
            id_to_instance[tid]
            for tid in target_id_order_list
            if tid in id_to_instance
        ]
    target_instance_list = list(reversed(list(target_instance_list)))

    y_ticks = [10 * (n + 1) for n in range(len(target_instance_list))]
    y_tick_labels = [task.name for task in target_instance_list]
    if print_workflow_name:
        y_tick_labels = [f"{workflow.name}: {task.name}" for task in target_instance_list]

    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(y_tick_labels)

    for time, task in enumerate(target_instance_list):
        ready_time_list, working_time_list = task.get_time_list_for_gantt_chart(
            finish_margin=finish_margin
        )

        if view_ready:
            gnt.broken_barh(
                ready_time_list, (y_ticks[time] - 5, 9), facecolors=(ready_color)
            )
        if task.auto_task:
            gnt.broken_barh(
                working_time_list,
                (y_ticks[time] - 5, 9),
                facecolors=(auto_task_color),
            )
        else:
            gnt.broken_barh(
                working_time_list, (y_ticks[time] - 5, 9), facecolors=(task_color)
            )

    if save_fig_path is not None:
        plt.savefig(save_fig_path)
    plt.close()
    return fig, gnt


def create_data_for_gantt_plotly(
    workflow,
    init_datetime: datetime.datetime,
    unit_timedelta: datetime.timedelta,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_workflow_name: bool = True,
    view_ready: bool = False,
):
    """Create data for gantt plotly from task_set."""
    df = []
    target_instance_list = workflow.task_set
    if target_id_order_list is not None:
        id_to_instance = {instance.ID: instance for instance in workflow.task_set}
        target_instance_list = [
            id_to_instance[tid]
            for tid in target_id_order_list
            if tid in id_to_instance
        ]
    for task in target_instance_list:
        ready_time_list, working_time_list = task.get_time_list_for_gantt_chart(
            finish_margin=finish_margin
        )

        task_name = task.name
        if print_workflow_name:
            task_name = f"{workflow.name}: {task.name}"

        if view_ready:
            for from_time, length in ready_time_list:
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
                        "State": "READY",
                        "Type": "Task",
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
                    "Type": "Task",
                }
            )
    return df


def create_gantt_plotly(
    workflow,
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
    print_workflow_name: bool = True,
    view_ready: bool = False,
    save_fig_path: str = None,
):
    """Create Gantt chart by plotly."""
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
        else {"WORKING": "rgb(146, 237, 5)", "READY": "rgb(107, 127, 135)"}
    )
    index_col = index_col if index_col is not None else "State"
    df = create_data_for_gantt_plotly(
        workflow,
        init_datetime,
        unit_timedelta,
        target_id_order_list=target_id_order_list,
        finish_margin=finish_margin,
        print_workflow_name=print_workflow_name,
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


def get_networkx_graph(workflow):
    """Get the information of networkx graph."""
    try:
        import networkx as nx
    except ImportError:
        raise ImportError(
            "networkx is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install networkx"
        )
    g = nx.DiGraph()

    for task in workflow.task_set:
        g.add_node(task)

    task_id_map = {task.ID: task for task in workflow.task_set}

    for task in workflow.task_set:
        for input_task_id, _ in task.input_task_id_dependency_set:
            input_task = task_id_map.get(input_task_id)
            g.add_edge(input_task, task)

    return g


def draw_networkx(
    workflow,
    g=None,
    pos: dict = None,
    arrows: bool = True,
    task_node_color: str = "#00EE00",
    auto_task_node_color: str = "#005500",
    figsize: tuple[float, float] = None,
    dpi: float = 100.0,
    save_fig_path: str = None,
    **kwargs,
):
    """Draw networkx."""
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
    g = g if g is not None else get_networkx_graph(workflow)
    pos = pos if pos is not None else nx.spring_layout(g)

    normal_task_set = {task for task in workflow.task_set if not task.auto_task}
    nx.draw_networkx_nodes(
        g,
        pos,
        nodelist=normal_task_set,
        node_color=task_node_color,
        **kwargs,
    )

    auto_task_set = {task for task in workflow.task_set if task.auto_task}
    nx.draw_networkx_nodes(
        g,
        pos,
        nodelist=auto_task_set,
        node_color=auto_task_node_color,
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
    workflow,
    g=None,
    pos: dict = None,
    node_size: int = 20,
    task_node_color: str = "#00EE00",
    auto_task_node_color: str = "#005500",
):
    """Get nodes and edges information of plotly network."""
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
    g = g if g is not None else get_networkx_graph(workflow)
    pos = pos if pos is not None else nx.spring_layout(g)

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

    for node in g.nodes:
        x, y = pos[node]
        if not node.auto_task:
            task_node_trace["x"] = task_node_trace["x"] + (x,)
            task_node_trace["y"] = task_node_trace["y"] + (y,)
            task_node_trace["text"] = task_node_trace["text"] + (node,)
        elif node.auto_task:
            auto_task_node_trace["x"] = auto_task_node_trace["x"] + (x,)
            auto_task_node_trace["y"] = auto_task_node_trace["y"] + (y,)
            auto_task_node_trace["text"] = auto_task_node_trace["text"] + (node,)

    edge_trace = go.Scatter(
        x=[],
        y=[],
        line={"width": 1, "color": "#888"},
        hoverinfo="none",
        mode="lines",
    )

    for edge in g.edges:
        x = edge[0]
        y = edge[1]
        x_pos_x, x_pos_y = pos[x]
        y_pos_x, y_pos_y = pos[y]
        edge_trace["x"] += (x_pos_x, y_pos_x)
        edge_trace["y"] += (x_pos_y, y_pos_y)

    return task_node_trace, auto_task_node_trace, edge_trace


def draw_plotly_network(
    workflow,
    g=None,
    pos: dict = None,
    title: str = "Workflow",
    node_size: int = 20,
    task_node_color: str = "#00EE00",
    auto_task_node_color: str = "#005500",
    save_fig_path=None,
):
    """Draw plotly network."""
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
    g = g if g is not None else get_networkx_graph(workflow)
    pos = pos if pos is not None else nx.spring_layout(g)
    (
        task_node_trace,
        auto_task_node_trace,
        edge_trace,
    ) = get_node_and_edge_trace_for_plotly_network(
        workflow,
        g,
        pos,
        node_size=node_size,
        task_node_color=task_node_color,
        auto_task_node_color=auto_task_node_color,
    )
    fig = go.Figure(
        data=[edge_trace, task_node_trace, auto_task_node_trace],
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
