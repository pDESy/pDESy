"""Utility functions for Gantt chart generation."""

import datetime


def convert_steps_to_datetime_gantt_mermaid(
    list_of_lines: list[str],
    project_init_datetime: datetime.datetime,
    project_unit_timedelta: datetime.timedelta,
) -> str:
    """Convert step-based Gantt chart data to datetime-formatted Mermaid diagram.

    Args:
        list_of_lines (list[str]): List of Gantt chart lines with step-based time ranges.
        project_init_datetime (datetime.datetime): Start datetime of project.
        project_unit_timedelta (datetime.timedelta): Unit time of simulation.

    Returns:
        str: Mermaid Gantt diagram text with datetime formatting.
    """
    if project_unit_timedelta < datetime.timedelta(days=1):
        date_format = "YYYY-MM-DD HH:mm"
        axis_format = "%Y-%m-%d %H:%M"
        output_date_format = "%Y-%m-%d %H:%M"
    else:
        date_format = "YYYY-MM-DD"
        axis_format = "%Y-%m-%d"
        output_date_format = "%Y-%m-%d"
    converted_lines = []
    for line in list_of_lines:
        try:
            text, time_range = line.rsplit(":", 1)
            start_str, end_str = time_range.split(",", 1)
            start_step = int(start_str)
            end_step = int(end_str)
            start_dt = project_init_datetime + start_step * project_unit_timedelta
            end_dt = project_init_datetime + end_step * project_unit_timedelta
            start_out = start_dt.strftime(output_date_format)
            end_out = end_dt.strftime(output_date_format)
            converted_lines.append(f"{text}:{start_out},{end_out}")
        except (ValueError, TypeError):
            converted_lines.append(line)
    header_lines = [
        "gantt",
        f"dateFormat {date_format}",
        f"axisFormat {axis_format}",
    ]
    return "\n".join([*header_lines, *converted_lines])


def build_gantt_mermaid_steps_lines(
    ready_time_list: list[tuple[int, int]],
    working_time_list: list[tuple[int, int]],
    range_time: tuple[int, int],
    view_ready: bool,
    ready_text_builder,
    work_text_builder,
) -> list[str]:
    """Build step-based Gantt chart lines with shared clipping logic.

    Args:
        ready_time_list (list[tuple[int, int]]): List of ready time ranges.
        working_time_list (list[tuple[int, int]]): List of working time ranges.
        range_time (tuple[int, int]): Range time of gantt chart.
        view_ready (bool): If True, ready ranges are included.
        ready_text_builder (Callable[[int], str]): Builder for ready text.
        work_text_builder (Callable[[int], str]): Builder for working text.

    Returns:
        list[str]: List of lines for gantt mermaid steps diagram.
    """
    list_of_lines = []

    def add_lines(time_list, text_builder):
        for start, duration in time_list:
            end = start + duration - 1
            if end < range_time[0] or start > range_time[1]:
                continue
            clipped_start = max(start, range_time[0])
            clipped_end = min(end + 1, range_time[1])
            if clipped_end == float("inf"):
                clipped_end = end + 1
            text = text_builder(clipped_start)
            list_of_lines.append(f"{text}:{int(clipped_start)},{int(clipped_end)}")

    if view_ready:
        add_lines(ready_time_list, ready_text_builder)
    add_lines(working_time_list, work_text_builder)
    return list_of_lines

