#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visualization helpers for BaseProduct."""

import datetime


def plot_simple_gantt(
    product,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_product_name: bool = True,
    view_ready: bool = False,
    component_color: str = "#00EE00",
    ready_color: str = "#C0C0C0",
    figsize: tuple[float, float] = None,
    dpi: float = 100.0,
    save_fig_path: str = None,
):
    """Plot Gantt chart by matplotlib."""
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
        product,
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
    product,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_product_name: bool = True,
    view_ready: bool = False,
    component_color: str = "#00EE00",
    ready_color: str = "#C0C0C0",
    figsize: tuple[float, float] = None,
    dpi: float = 100.0,
    save_fig_path: str = None,
):
    """Create Gantt chart by matplotlib."""
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

    target_instance_list = product.component_set
    if target_id_order_list is not None:
        id_to_instance = {instance.ID: instance for instance in product.component_set}
        target_instance_list = [
            id_to_instance[tid]
            for tid in target_id_order_list
            if tid in id_to_instance
        ]
    target_instance_list = list(reversed(list(target_instance_list)))

    y_ticks = [10 * (n + 1) for n in range(len(target_instance_list))]
    y_tick_labels = [component.name for component in target_instance_list]
    if print_product_name:
        y_tick_labels = [
            f"{product.name}: {component.name}" for component in target_instance_list
        ]

    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(y_tick_labels)

    for time, component in enumerate(target_instance_list):
        ready_time_list, working_time_list = component.get_time_list_for_gantt_chart(
            finish_margin=finish_margin
        )

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
    product,
    init_datetime: datetime.datetime,
    unit_timedelta: datetime.timedelta,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_product_name: bool = True,
    view_ready: bool = False,
):
    """Create data for gantt plotly from component_set."""
    df = []
    target_instance_list = product.component_set
    if target_id_order_list is not None:
        id_to_instance = {instance.ID: instance for instance in product.component_set}
        target_instance_list = [
            id_to_instance[tid]
            for tid in target_id_order_list
            if tid in id_to_instance
        ]
    for component in target_instance_list:
        ready_time_list, working_time_list = component.get_time_list_for_gantt_chart(
            finish_margin=finish_margin
        )

        component_name = component.name
        if print_product_name:
            component_name = f"{product.name}: {component.name}"

        if view_ready:
            for from_time, length in ready_time_list:
                to_time = from_time + length
                df.append(
                    {
                        "Task": component_name,
                        "Start": (init_datetime + from_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Finish": (init_datetime + to_time * unit_timedelta).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "State": "READY",
                        "Type": "Component",
                    }
                )
        for from_time, length in working_time_list:
            to_time = from_time + length
            df.append(
                {
                    "Task": component_name,
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
    product,
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
        else {
            "Component": "rgb(246, 37, 105)",
            "READY": "rgb(107, 127, 135)",
            "WORKING": "rgb(46, 137, 205)",
            "FINISHED": "rgb(114, 44, 121)",
        }
    )
    index_col = index_col if index_col is not None else "State"
    df = create_data_for_gantt_plotly(
        product,
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


def get_networkx_graph(product):
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

    for component in product.component_set:
        g.add_node(component)

    component_id_map = {component.ID: component for component in product.component_set}

    for component in product.component_set:
        for input_component_id in component.child_component_id_set:
            input_component = component_id_map.get(input_component_id)
            g.add_edge(component, input_component)

    return g


def draw_networkx(
    product,
    g=None,
    pos: dict = None,
    arrows: bool = True,
    node_color: str = "#00EE00",
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
    g = g if g is not None else get_networkx_graph(product)
    pos = pos if pos is not None else nx.spring_layout(g)

    nx.draw_networkx_nodes(g, pos, node_color=node_color, **kwargs)
    nx.draw_networkx_labels(g, pos, **kwargs)
    nx.draw_networkx_edges(g, pos, arrows=arrows, **kwargs)
    plt.axis("off")
    if save_fig_path is not None:
        plt.savefig(save_fig_path)
    plt.close()
    return fig


def get_node_and_edge_trace_for_plotly_network(
    product,
    g=None,
    pos: dict = None,
    node_size: int = 20,
    node_color: str = "#00EE00",
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
    g = g if g is not None else get_networkx_graph(product)
    pos = pos if pos is not None else nx.spring_layout(g)

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        marker={
            "color": node_color,
            "size": node_size,
        },
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

    return node_trace, edge_trace


def draw_plotly_network(
    product,
    g=None,
    pos: dict = None,
    title: str = "Product",
    node_size: int = 20,
    node_color: str = "#00EE00",
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
    g = g if g is not None else get_networkx_graph(product)
    pos = pos if pos is not None else nx.spring_layout(g)
    node_trace, edge_trace = get_node_and_edge_trace_for_plotly_network(
        product, g, pos, node_size=node_size, node_color=node_color
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
