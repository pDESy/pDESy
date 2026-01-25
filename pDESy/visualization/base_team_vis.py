#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visualization helpers for BaseTeam."""

import datetime


def plot_simple_gantt(
    team,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_team_name: bool = True,
    view_ready: bool = False,
    worker_color: str = "#D9E5FF",
    ready_color: str = "#C0C0C0",
    figsize: tuple[float, float] = None,
    dpi: float = 100.0,
    save_fig_path: str = None,
):
    """Plot Gantt chart by matplotlib."""
    if figsize is None:
        figsize = [6.4, 4.8]
    fig, gnt = create_simple_gantt(
        team,
        target_id_order_list=target_id_order_list,
        finish_margin=finish_margin,
        print_team_name=print_team_name,
        view_ready=view_ready,
        worker_color=worker_color,
        ready_color=ready_color,
        figsize=figsize,
        dpi=dpi,
        save_fig_path=save_fig_path,
    )
    _ = gnt
    return fig


def create_simple_gantt(
    team,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_team_name: bool = True,
    view_ready: bool = False,
    view_absence: bool = False,
    worker_color: str = "#D9E5FF",
    ready_color: str = "#DCDCDC",
    absence_color: str = "#696969",
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
    fig, gnt = plt.subplots(figsize=figsize, dpi=dpi)
    gnt.set_xlabel("step")
    gnt.grid(True)

    target_instance_list = team.worker_set
    if target_id_order_list is not None:
        id_to_instance = {instance.ID: instance for instance in team.worker_set}
        target_instance_list = [
            id_to_instance[tid]
            for tid in target_id_order_list
            if tid in id_to_instance
        ]

    target_instance_list = list(reversed(list(target_instance_list)))

    y_ticks = [10 * (n + 1) for n in range(len(target_instance_list))]
    y_tick_labels = [worker.name for worker in target_instance_list]
    if print_team_name:
        y_tick_labels = [f"{team.name}: {worker.name}" for worker in target_instance_list]

    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(y_tick_labels)

    for time, worker in enumerate(target_instance_list):
        ready_time_list, working_time_list, absence_time_list = (
            worker.get_time_list_for_gantt_chart(finish_margin=finish_margin)
        )
        if view_ready:
            gnt.broken_barh(
                ready_time_list,
                (y_ticks[time] - 5, 9),
                facecolors=(ready_color),
            )
        if view_absence:
            gnt.broken_barh(
                absence_time_list,
                (y_ticks[time] - 5, 9),
                facecolors=(absence_color),
            )
        gnt.broken_barh(
            working_time_list,
            (y_ticks[time] - 5, 9),
            facecolors=(worker_color),
        )
    if save_fig_path is not None:
        plt.savefig(save_fig_path)
    plt.close()
    return fig, gnt


def create_data_for_gantt_plotly(
    team,
    init_datetime: datetime.datetime,
    unit_timedelta: datetime.timedelta,
    target_id_order_list: list[str] = None,
    finish_margin: float = 1.0,
    print_team_name: bool = True,
    view_ready: bool = False,
    view_absence: bool = False,
):
    """Create data for gantt plotly of BaseWorker in worker_set."""
    df = []
    target_instance_list = team.worker_set
    if target_id_order_list is not None:
        id_to_instance = {instance.ID: instance for instance in team.worker_set}
        target_instance_list = [
            id_to_instance[tid]
            for tid in target_id_order_list
            if tid in id_to_instance
        ]
    for worker in target_instance_list:
        ready_time_list, working_time_list, absence_time_list = (
            worker.get_time_list_for_gantt_chart(finish_margin=finish_margin)
        )

        task_name = worker.name
        if print_team_name:
            task_name = f"{team.name}: {worker.name}"

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
                        "Type": "Worker",
                    }
                )
        if view_absence:
            for from_time, length in absence_time_list:
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
                        "State": "ABSENCE",
                        "Type": "Worker",
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
                    "Type": "Worker",
                }
            )
    return df


def create_gantt_plotly(
    team,
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
    print_team_name: bool = True,
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
            "WORKING": "rgb(46, 137, 205)",
        }
    )
    index_col = index_col if index_col is not None else "State"
    
    # Determine which states to view based on provided colors
    # Only include READY/ABSENCE if the user explicitly provides colors for them
    view_ready_flag = "READY" in (colors if colors is not None else {})
    view_absence_flag = "ABSENCE" in (colors if colors is not None else {})
    
    df = create_data_for_gantt_plotly(
        team,
        init_datetime,
        unit_timedelta,
        target_id_order_list=target_id_order_list,
        print_team_name=print_team_name,
        view_ready=view_ready_flag,
        view_absence=view_absence_flag,
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


def create_data_for_cost_history_plotly(
    team,
    init_datetime: datetime.datetime,
    unit_timedelta: datetime.timedelta,
):
    """Create data for cost history plotly from cost_record_list of BaseWorker."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError(
            "plotly is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install plotly"
        )

    data = []
    x = [
        (init_datetime + time * unit_timedelta).strftime("%Y-%m-%d %H:%M:%S")
        for time in range(len(team.cost_record_list))
    ]
    for worker in team.worker_set:
        data.append(go.Bar(name=worker.name, x=x, y=worker.cost_record_list))
    return data


def create_cost_history_plotly(
    team,
    init_datetime: datetime.datetime,
    unit_timedelta: datetime.timedelta,
    title: str = "Cost Chart",
    save_fig_path: str = None,
):
    """Create cost chart by plotly."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError(
            "plotly is required for visualization. "
            "Install it with: pip install pdesy[vis] "
            "or: pip install plotly"
        )

    data = create_data_for_cost_history_plotly(team, init_datetime, unit_timedelta)
    fig = go.Figure(data)
    fig.update_layout(barmode="stack", title=title)
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
