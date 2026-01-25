"""Utility functions for Mermaid diagram output."""

import datetime


class MermaidDiagramMixin:
    """Mixin for building Mermaid diagram lines."""

    def _get_mermaid_label(self, print_extra_info: bool = False, **kwargs) -> str:
        raise NotImplementedError

    def get_mermaid_diagram(
        self,
        shape: str = "rect",
        subgraph: bool = False,
        subgraph_name: str | None = None,
        subgraph_direction: str = "LR",
        print_extra_info: bool = False,
        **kwargs,
    ) -> list[str]:
        """Get mermaid diagram lines for a single node."""
        list_of_lines = []
        if subgraph:
            name = subgraph_name if subgraph_name is not None else self.__class__.__name__
            list_of_lines.append(f"subgraph {name}")
            list_of_lines.append(f"direction {subgraph_direction}")

        node_label = self._get_mermaid_label(
            print_extra_info=print_extra_info,
            **kwargs,
        )
        list_of_lines.append(f"{self.ID}@{{shape: {shape}, label: '{node_label}'}}")

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        **kwargs,
    ) -> None:
        """Print mermaid diagram using the common output helper."""
        list_of_lines = self.get_mermaid_diagram(**kwargs)
        print_mermaid_diagram(orientations, list_of_lines)


class CollectionMermaidDiagramMixin:
    """Mixin for building Mermaid diagram lines for collections."""

    def _build_collection_mermaid_diagram(
        self,
        subgraph: bool,
        subgraph_name: str,
        subgraph_direction: str,
        node_lines: list[str],
        edge_lines: list[str] | None = None,
    ) -> list[str]:
        list_of_lines: list[str] = []
        if subgraph:
            list_of_lines.append(f"subgraph {subgraph_name}")
            list_of_lines.append(f"direction {subgraph_direction}")

        list_of_lines.extend(node_lines)
        if edge_lines:
            list_of_lines.extend(edge_lines)

        if subgraph:
            list_of_lines.append("end")

        return list_of_lines

    def _build_target_collection_mermaid_diagram(
        self,
        target_set,
        owner_set,
        subgraph: bool,
        subgraph_name: str,
        subgraph_direction: str,
        node_builder,
        edge_builder=None,
    ) -> list[str]:
        filtered_targets = [item for item in target_set if item in owner_set]
        node_lines: list[str] = []
        for item in filtered_targets:
            node_lines.extend(node_builder(item))
        edge_lines = edge_builder(filtered_targets) if edge_builder else None
        return self._build_collection_mermaid_diagram(
            subgraph=subgraph,
            subgraph_name=subgraph_name,
            subgraph_direction=subgraph_direction,
            node_lines=node_lines,
            edge_lines=edge_lines,
        )

    def _build_collection_gantt_mermaid_steps(
        self,
        target_instance_set,
        target_id_order_list: list[str] | None,
        section: bool,
        section_name: str,
        range_time: tuple[int, int],
        view_ready: bool,
        detailed_info: bool,
        id_name_dict: dict[str, str] | None,
        steps_builder,
    ) -> list[str]:
        target_instance_list = target_instance_set
        if target_id_order_list is not None:
            id_to_instance = {instance.ID: instance for instance in target_instance_set}
            target_instance_list = [
                id_to_instance[tid]
                for tid in target_id_order_list
                if tid in id_to_instance
            ]

        list_of_lines: list[str] = []
        if section:
            list_of_lines.append(f"section {section_name}")
        for instance in target_instance_list:
            list_of_lines.extend(
                steps_builder(
                    instance,
                    range_time=range_time,
                    view_ready=view_ready,
                    detailed_info=detailed_info,
                    id_name_dict=id_name_dict,
                )
            )
        return list_of_lines

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        **kwargs,
    ) -> None:
        """Print collection mermaid diagram using the common output helper."""
        list_of_lines = self.get_mermaid_diagram(**kwargs)
        print_mermaid_diagram(orientations, list_of_lines)


def print_mermaid_diagram(orientations: str, list_of_lines: list[str]) -> None:
    """Print mermaid diagram with a flowchart header.

    Args:
        orientations (str): Orientation of mermaid diagram.
        list_of_lines (list[str]): List of mermaid diagram lines.
    """
    print(f"flowchart {orientations}")
    print(*list_of_lines, sep="\n")


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
