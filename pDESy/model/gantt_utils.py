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
