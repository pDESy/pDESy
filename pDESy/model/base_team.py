#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_team."""

from __future__ import annotations
import abc
import datetime
import sys
import uuid
import warnings

from pDESy.model.base_task import BaseTask

from .base_worker import BaseWorker, BaseWorkerState
from .mermaid_utils import (
    CollectionMermaidDiagramMixin,
    convert_steps_to_datetime_gantt_mermaid,
    print_mermaid_diagram as print_mermaid_diagram_lines,
)
from .pdesy_utils import CollectionCommonMixin, CollectionLogJsonMixin


class BaseTeam(
    CollectionMermaidDiagramMixin,
    CollectionCommonMixin,
    CollectionLogJsonMixin,
    object,
    metaclass=abc.ABCMeta,
):
    _absence_cost_record_attr_name = "cost_record_list"
    """BaseTeam.

    BaseTeam class for expressing team in a project.
    This class will be used as a template.

    Args:
        name (str, optional): Name of this team. Defaults to None -> "New Team".
        ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
        worker_set (set[BaseWorker], optional): Set of BaseWorkers who belong to this team. Defaults to None -> set().
        targeted_task_id_set (set[str], optional): Targeted BaseTasks id set. Defaults to None -> set().
        parent_team_id (str, optional): Parent team id of this team. Defaults to None.
        cost_record_list (List[float], optional): History or record of this team's cost in simulation. Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        worker_set: set[BaseWorker] = None,
        targeted_task_id_set: set[str] = None,
        parent_team_id: str = None,
        # Basic variables
        cost_record_list: list[float] = None,
    ):
        """init."""
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.name = name if name is not None else "New Team"
        self.ID = ID if ID is not None else str(uuid.uuid4())

        self.worker_set = worker_set if worker_set is not None else set()
        for worker in self.worker_set:
            if worker.team_id is None:
                worker.team_id = self.ID

        self.targeted_task_id_set = (
            targeted_task_id_set if targeted_task_id_set is not None else set()
        )
        self.parent_team_id = parent_team_id if parent_team_id is not None else None

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        if cost_record_list is not None:
            self.cost_record_list = cost_record_list
        else:
            self.cost_record_list = []

    def set_parent_team(self, parent_team: BaseTeam):
        """
        Set parent team.

        Args:
            parent_team (BaseTeam): Parent team.
        """
        self.parent_team_id = parent_team.ID if parent_team is not None else None

    def extend_targeted_task_list(self, targeted_task_list: list[BaseTask]):
        """
        Extend the list of targeted tasks.

        .. deprecated:: Use `update_targeted_task_set` instead.

        Args:
            targeted_task_list (list[BaseTask]): List of targeted tasks.
        """
        warnings.warn(
            "extend_targeted_task_list is deprecated. Use update_targeted_task_set instead.",
            DeprecationWarning,
        )
        for targeted_task in targeted_task_list:
            self.append_targeted_task(targeted_task)

    def update_targeted_task_set(self, targeted_task_set: set[BaseTask]):
        """
        Extend the set of targeted tasks.

        Args:
            targeted_task_set (set[BaseTask]): Set of targeted tasks.
        """
        for targeted_task in targeted_task_set:
            self.add_targeted_task(targeted_task)

    def append_targeted_task(self, targeted_task: BaseTask):
        """
        Append targeted task.

        .. deprecated:: Use `add_targeted_task` instead.

        Args:
            targeted_task (BaseTask): Targeted task.
        """
        warnings.warn(
            "append_targeted_task is deprecated. Use add_targeted_task instead.",
            DeprecationWarning,
        )
        self.targeted_task_id_set.add(targeted_task.ID)
        targeted_task.allocated_team_id_set.add(self.ID)

    def add_targeted_task(self, targeted_task: BaseTask):
        """
        Add targeted task.

        Args:
            targeted_task (BaseTask): Targeted task.
        """
        if not isinstance(targeted_task, BaseTask):
            raise TypeError(
                f"targeted_task must be BaseTask, but {type(targeted_task)}"
            )
        if targeted_task.ID in self.targeted_task_id_set:
            warnings.warn(
                f"Targeted task {targeted_task.ID} is already added to {self.ID}.",
                UserWarning,
            )
        else:
            self.targeted_task_id_set.add(targeted_task.ID)
            targeted_task.allocated_team_id_set.add(self.ID)

    def add_worker(self, worker: BaseWorker):
        """
        Add worker to `worker_set`.

        Args:
            worker (BaseWorker): Worker which is added to this workplace.
        """
        if not isinstance(worker, BaseWorker):
            raise TypeError(f"worker must be BaseWorker, but got {type(worker)}")
        worker.team_id = self.ID
        self.worker_set.add(worker)

    def create_worker(
        self,
        # Basic parameters
        name: str = None,
        ID: str = None,
        main_workplace_id: str = None,
        cost_per_time: float = 0.0,
        solo_working: bool = False,
        workamount_skill_mean_map: dict[str, float] = None,
        workamount_skill_sd_map: dict[str, float] = None,
        facility_skill_map: dict[str, float] = None,
        absence_time_list: list[int] = None,
        # Basic variables
        state: BaseWorkerState = BaseWorkerState.FREE,
        state_record_list: list[BaseWorkerState] = None,
        cost_record_list: list[float] = None,
        assigned_task_facility_id_tuple_set: set[tuple[str, str]] = None,
        assigned_task_facility_id_tuple_set_record_list: list[
            set[tuple[str, str]]
        ] = None,
        # Advanced parameters for customized simulation
        quality_skill_mean_map: dict[str, float] = None,
        quality_skill_sd_map: dict[str, float] = None,
    ):
        """
        Create a BaseWorker instance and add it to this team.

        Args:
            name (str, optional): Name of this worker. Defaults to None -> "New Worker".
            ID (str, optional): ID will be defined automatically. Defaults to None -> str(uuid.uuid4()).
            main_workplace_id (str, optional): Main workplace ID. Defaults to None.
            cost_per_time (float, optional): Cost of this worker per unit time. Defaults to 0.0.
            solo_working (bool, optional): Flag whether this worker can work with other workers or not. Defaults to False.
            workamount_skill_mean_map (Dict[str, float], optional): Skill for expressing progress in unit time. Defaults to None -> {}.
            workamount_skill_sd_map (Dict[str, float], optional): Standard deviation of skill for expressing progress in unit time. Defaults to None -> {}.
            facility_skill_map (Dict[str, float], optional): Skill for operating facility in unit time. Defaults to None -> {}.
            absence_time_list (List[int], optional): List of absence time of simulation. Defaults to None -> [].
            state (BaseWorkerState, optional): State of this worker in simulation. Defaults to BaseWorkerState.FREE.
            state_record_list (List[BaseWorkerState], optional): Record list of state. Defaults to None -> [].
            cost_record_list (List[float], optional): History or record of his or her cost in simulation. Defaults to None -> [].
            assigned_task_facility_id_tuple_set (set(tuple(str, str)), optional): State of his or her assigned task and facility id tuple in simulation. Defaults to None -> set().
            assigned_task_facility_id_tuple_set_record_list (List[set(tuple(str, str))], optional): Record of his or her assigned tasks' id in simulation. Defaults to None -> [].
            quality_skill_mean_map (Dict[str, float], optional): Skill for expressing quality in unit time. Defaults to None -> {}.
            quality_skill_sd_map (Dict[str, float], optional): Standard deviation of skill for expressing quality in unit time. Defaults to None -> {}.

        Returns:
            BaseWorker: The created worker.
        """
        worker = BaseWorker(
            # Basic parameters
            name=name,
            ID=ID,
            main_workplace_id=main_workplace_id,
            cost_per_time=cost_per_time,
            solo_working=solo_working,
            workamount_skill_mean_map=workamount_skill_mean_map,
            workamount_skill_sd_map=workamount_skill_sd_map,
            facility_skill_map=facility_skill_map,
            absence_time_list=absence_time_list,
            # Basic variables
            state=state,
            state_record_list=state_record_list,
            cost_record_list=cost_record_list,
            assigned_task_facility_id_tuple_set=assigned_task_facility_id_tuple_set,
            assigned_task_facility_id_tuple_set_record_list=(
                assigned_task_facility_id_tuple_set_record_list
            ),
            # Advanced parameters for customized simulation
            quality_skill_mean_map=quality_skill_mean_map,
            quality_skill_sd_map=quality_skill_sd_map,
        )
        self.add_worker(worker)
        return worker

    def initialize(self, state_info: bool = True, log_info: bool = True):
        """
        Initialize the changeable variables of BaseTeam.

        If `log_info` is True, the following attributes are initialized:
            - cost_record_list

        BaseWorker in `worker_set` are also initialized by this function.

        Args:
            state_info (bool, optional): Whether to initialize state information. Defaults to True.
            log_info (bool, optional): Whether to initialize log information. Defaults to True.
        """
        if log_info:
            self.cost_record_list = []
        for w in self.worker_set:
            w.initialize(state_info=state_info, log_info=log_info)

    def reverse_log_information(self):
        """Reverse log information of all."""
        super().reverse_log_information()

    def add_labor_cost(
        self, only_working: bool = True, add_zero_to_all_workers: bool = False
    ):
        """
        Add labor cost to workers in this team.

        Args:
            only_working (bool, optional): If True, add labor cost to only WORKING workers in this team. If False, add labor cost to all workers in this team. Defaults to True.
            add_zero_to_all_workers (bool, optional): If True, add 0 labor cost to all workers in this team. If False, calculate labor cost normally. Defaults to False.

        Returns:
            float: Total labor cost of this team in this time.
        """
        cost_this_time = 0.0

        if add_zero_to_all_workers:
            for worker in self.worker_set:
                worker.cost_record_list.append(0.0)

        else:
            if only_working:
                for worker in self.worker_set:
                    if worker.state == BaseWorkerState.WORKING:
                        worker.cost_record_list.append(worker.cost_per_time)
                        cost_this_time += worker.cost_per_time
                    else:
                        worker.cost_record_list.append(0.0)

            else:
                for worker in self.worker_set:
                    worker.cost_record_list.append(worker.cost_per_time)
                    cost_this_time += worker.cost_per_time

        self.cost_record_list.append(cost_this_time)
        return cost_this_time

    def record_assigned_task_id(self):
        """Record assigned task id in this time."""
        super().record_children_assigned_task_id()

    def record_all_worker_state(self, working: bool = True):
        """Record the state of all workers by using BaseWorker.record_state()."""
        super().record_children_state(working=working)

    def __str__(self):
        """Return the name of BaseTeam.

        Returns:
            str: Name of BaseTeam.
        """
        return f"{self.name}"

    def _iter_log_children(self):
        return self.worker_set

    def _iter_absence_children(self):
        return self.worker_set

    def _get_reverse_log_lists(self) -> list[list]:
        return [self.cost_record_list]

    def _get_export_dict_extra_fields(self) -> dict:
        return {
            "worker_set": [w.export_dict_json_data() for w in self.worker_set],
            "targeted_task_id_set": list(self.targeted_task_id_set),
            "parent_team_id": (
                self.parent_team_id if self.parent_team_id is not None else None
            ),
            "cost_record_list": self.cost_record_list,
        }

    def _read_json_extra_fields(self, json_data: dict) -> None:
        self.worker_set = set()
        for w in json_data["worker_set"]:
            worker = BaseWorker(
                name=w["name"],
                ID=w["ID"],
                team_id=w["team_id"],
                cost_per_time=w["cost_per_time"],
                solo_working=w["solo_working"],
                workamount_skill_mean_map=w["workamount_skill_mean_map"],
                workamount_skill_sd_map=w["workamount_skill_sd_map"],
                facility_skill_map=w["facility_skill_map"],
                absence_time_list=w["absence_time_list"],
                state=BaseWorkerState(w["state"]),
                state_record_list=[
                    BaseWorkerState(state_num) for state_num in w["state_record_list"]
                ],
                cost_record_list=w["cost_record_list"],
                assigned_task_facility_id_tuple_set=set(
                    w["assigned_task_facility_id_tuple_set"]
                ),
                assigned_task_facility_id_tuple_set_record_list=w[
                    "assigned_task_facility_id_tuple_set_record_list"
                ],
            )
            self.worker_set.add(worker)
        self.targeted_task_id_set = set(json_data["targeted_task_id_set"])
        self.parent_team_id = json_data["parent_team_id"]
        self.cost_record_list = json_data["cost_record_list"]

    def get_worker_set_by_state(
        self, target_time_list: list[int], target_state: BaseWorkerState
    ):
        """
        Extract state worker list from simulation result.

        Args:
            target_time_list (List[int]): Target time list. If you want to extract target_state worker from time 2 to time 4, you must set [2, 3, 4] to this argument.
            target_state (BaseWorkerState): Target state.

        Returns:
            set[BaseWorker]: Set of BaseWorker.
        """
        return {
            worker
            for worker in self.worker_set
            if all(
                len(worker.state_record_list) > time
                and worker.state_record_list[time] == target_state
                for time in target_time_list
            )
        }

    def get_worker_set(
        self,
        name: str = None,
        ID: str = None,
        team_id: str = None,
        cost_per_time: float = None,
        solo_working: bool = None,
        workamount_skill_mean_map: dict[str, float] = None,
        workamount_skill_sd_map: dict[str, float] = None,
        facility_skill_map: dict[str, float] = None,
        state: BaseWorkerState = None,
        cost_record_list: list[float] = None,
        assigned_task_facility_id_tuple_set: set[tuple[str, str]] = None,
        assigned_task_facility_id_tuple_set_record_list: list[list[str]] = None,
    ):
        """
        Get worker list by using search conditions related to BaseWorker parameter.

        If there is no searching condition, this function returns all self.worker_set

        Args:
            name (str, optional): Target worker name. Defaults to None.
            ID (str, optional): Target worker ID. Defaults to None.
            team_id (str, optional): Target worker team_id. Defaults to None.
            cost_per_time (float, optional): Target worker cost_per_time. Defaults to None.
            solo_working (bool, optional): Target worker solo_working. Defaults to None.
            workamount_skill_mean_map (Dict[str, float], optional): Target worker workamount_skill_mean_map. Defaults to None.
            workamount_skill_sd_map (Dict[str, float], optional): Target worker workamount_skill_sd_map. Defaults to None.
            facility_skill_map (Dict[str, float], optional): Target worker facility_skill_map. Defaults to None.
            state (BaseWorkerState, optional): Target worker state. Defaults to None.
            cost_record_list (List[float], optional): Target worker cost_record_list. Defaults to None.
            assigned_task_facility_id_tuple_set (set[str], optional): Target worker assigned_task_facility_id_tuple_set. Defaults to None.
            assigned_task_facility_id_tuple_set_record_list (List[List[str]], optional): Target worker assigned_task_facility_id_tuple_set_record_list. Defaults to None.

        Returns:
            set[BaseWorker]: Set of BaseWorker.
        """
        worker_set = self.worker_set
        if name is not None:
            worker_set = set(filter(lambda x: x.name == name, worker_set))
        if ID is not None:
            worker_set = set(filter(lambda x: x.ID == ID, worker_set))
        if team_id is not None:
            worker_set = set(filter(lambda x: x.team_id == team_id, worker_set))
        if cost_per_time is not None:
            worker_set = set(
                filter(lambda x: x.cost_per_time == cost_per_time, worker_set)
            )
        if solo_working is not None:
            worker_set = set(
                filter(lambda x: x.solo_working == solo_working, worker_set)
            )
        if workamount_skill_mean_map is not None:
            worker_set = set(
                filter(
                    lambda x: x.workamount_skill_mean_map == workamount_skill_mean_map,
                    worker_set,
                )
            )
        if workamount_skill_sd_map is not None:
            worker_set = set(
                filter(
                    lambda x: x.workamount_skill_sd_map == workamount_skill_sd_map,
                    worker_set,
                )
            )
        if facility_skill_map is not None:
            worker_set = set(
                filter(lambda x: x.facility_skill_map == facility_skill_map, worker_set)
            )
        if state is not None:
            worker_set = set(filter(lambda x: x.state == state, worker_set))
        if cost_record_list is not None:
            worker_set = set(
                filter(lambda x: x.cost_record_list == cost_record_list, worker_set)
            )
        if assigned_task_facility_id_tuple_set is not None:
            worker_set = set(
                filter(
                    lambda x: x.assigned_task_facility_id_tuple_set
                    == assigned_task_facility_id_tuple_set,
                    worker_set,
                )
            )
        if assigned_task_facility_id_tuple_set_record_list is not None:
            worker_set = set(
                filter(
                    lambda x: x.assigned_task_facility_id_tuple_set_record_list
                    == assigned_task_facility_id_tuple_set_record_list,
                    worker_set,
                )
            )
        return worker_set

    def check_update_state_from_absence_time_list(self, step_time: int):
        """
        Check and update state of all resources to ABSENCE or FREE or WORKING.

        Args:
            step_time (int): Target step time of checking and updating state of workers.
        """
        for worker in self.worker_set:
            worker.check_update_state_from_absence_time_list(step_time)

    def set_absence_state_to_all_workers(self):
        """Set absence state to all workers and facilities."""
        for worker in self.worker_set:
            worker.state = BaseWorkerState.ABSENCE

    def plot_simple_gantt(
        self,
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
        """
        Plot Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            target_id_order_list (list[str], optional): Target ID order list for Gantt chart. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_team_name (bool, optional): Print team name or not. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to True.
            worker_color (str, optional): Node color setting information. Defaults to "#D9E5FF".
            ready_color (str, optional): Ready color setting information. Defaults to "#C0C0C0".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            fig: Figure in plt.subplots().
        """
        from pDESy.visualization import base_team_vis as team_viz

        return team_viz.plot_simple_gantt(
            self,
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

    def create_simple_gantt(
        self,
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
        """
        Create Gantt chart by matplotlib.

        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            target_id_order_list (list[str], optional): Target ID order list for Gantt chart. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_team_name (bool, optional): Print team name or not. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to False.
            view_absence (bool, optional): View ABSENCE time or not. Defaults to False.
            worker_color (str, optional): Node color setting information. Defaults to "#D9E5FF".
            ready_color (str, optional): Ready color setting information. Defaults to "#DCDCDC".
            absence_color (str, optional): Absence color setting information. Defaults to "#696969".
            figsize ((float, float), optional): Width, height in inches. Default to None -> [6.4, 4.8].
            dpi (float, optional): The resolution of the figure in dots-per-inch. Default to 100.0.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            fig: Figure in plt.subplots().
            gnt: Axes in plt.subplots().
        
        Raises:
            ImportError: If matplotlib is not installed.
        """
        from pDESy.visualization import base_team_vis as team_viz

        return team_viz.create_simple_gantt(
            self,
            target_id_order_list=target_id_order_list,
            finish_margin=finish_margin,
            print_team_name=print_team_name,
            view_ready=view_ready,
            view_absence=view_absence,
            worker_color=worker_color,
            ready_color=ready_color,
            absence_color=absence_color,
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
        print_team_name: bool = True,
        view_ready: bool = False,
        view_absence: bool = False,
    ):
        """
        Create data for gantt plotly of BaseWorker in worker_set.

        Args:
            init_datetime (datetime.datetime): Start datetime of project.
            unit_timedelta (datetime.timedelta): Unit time of simulation.
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            finish_margin (float, optional): Margin of finish time in Gantt chart. Defaults to 1.0.
            print_team_name (bool, optional): Print team name or not. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to False.
            view_absence (bool, optional): View Absence time or not. Defaults to False.

        Returns:
            List[dict]: Gantt plotly information of this BaseTeam.
        """
        from pDESy.visualization import base_team_vis as team_viz

        return team_viz.create_data_for_gantt_plotly(
            self,
            init_datetime,
            unit_timedelta,
            target_id_order_list=target_id_order_list,
            finish_margin=finish_margin,
            print_team_name=print_team_name,
            view_ready=view_ready,
            view_absence=view_absence,
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
        print_team_name: bool = True,
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
            colors (Dict[str, str], optional): Color setting of plotly Gantt chart. Defaults to None. If None, default color setting will be used.
            index_col (str, optional): index_col of plotly Gantt chart. Defaults to None -> "State".
            showgrid_x (bool, optional): showgrid_x of plotly Gantt chart. Defaults to True.
            showgrid_y (bool, optional): showgrid_y of plotly Gantt chart. Defaults to True.
            group_tasks (bool, optional): group_tasks of plotly Gantt chart. Defaults to True.
            show_colorbar (bool, optional): show_colorbar of plotly Gantt chart. Defaults to True.
            view_ready (bool, optional): View READY time or not. Defaults to False.
            print_team_name (bool, optional): Print team name or not. Defaults to True.
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            figure: Figure for a gantt chart.
        
        Raises:
            ImportError: If plotly is not installed.
        """
        from pDESy.visualization import base_team_vis as team_viz

        return team_viz.create_gantt_plotly(
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
            print_team_name=print_team_name,
            save_fig_path=save_fig_path,
        )

    def create_data_for_cost_history_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
    ):
        """
        Create data for cost history plotly from cost_record_list of BaseWorker in worker_set.

        Args:
            init_datetime (datetime.datetime): Start datetime of project.
            unit_timedelta (datetime.timedelta): Unit time of simulation.

        Returns:
            List[go.Bar]: Information of cost history chart.
        
        Raises:
            ImportError: If plotly is not installed.
        """
        from pDESy.visualization import base_team_vis as team_viz

        return team_viz.create_data_for_cost_history_plotly(
            self, init_datetime, unit_timedelta
        )

    def create_cost_history_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        title: str = "Cost Chart",
        save_fig_path: str = None,
    ):
        """
        Create cost chart by plotly.

        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime): Start datetime of project.
            unit_timedelta (datetime.timedelta): Unit time of simulation.
            title (str, optional): Title of cost chart. Defaults to "Cost Chart".
            save_fig_path (str, optional): Path of saving figure. Defaults to None.

        Returns:
            figure: Figure for a gantt chart.
        
        Raises:
            ImportError: If plotly is not installed.
        """
        from pDESy.visualization import base_team_vis as team_viz

        return team_viz.create_cost_history_plotly(
            self,
            init_datetime,
            unit_timedelta,
            title=title,
            save_fig_path=save_fig_path,
        )

    def get_target_worker_mermaid_diagram(
        self,
        target_worker_set: set[BaseWorker],
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of target worker.

        Args:
            target_worker_set (set[BaseWorker]): List of target workers.
            print_worker (bool, optional): Print workers or not. Defaults to True.
            shape_worker (str, optional): Shape of workers in this team. Defaults to "stadium".
            link_type_str (str, optional): Link type string. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        def node_builder(worker: BaseWorker) -> list[str]:
            if not print_worker:
                return []
            return worker.get_mermaid_diagram(shape=shape_worker)

        return self._build_target_collection_mermaid_diagram(
            target_set=target_worker_set,
            owner_set=self.worker_set,
            subgraph=subgraph,
            subgraph_name=f"{self.ID}[{self.name}]",
            subgraph_direction=subgraph_direction,
            node_builder=node_builder,
            edge_builder=None,
        )

    def get_mermaid_diagram(
        self,
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Get mermaid diagram of this team.

        Args:
            print_worker (bool, optional): Print workers or not. Defaults to True.
            shape_worker (str, optional): Shape of workers in this team. Defaults to "stadium".
            link_type_str (str, optional): Link type string. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".

        Returns:
            list[str]: List of lines for mermaid diagram.
        """

        return self.get_target_worker_mermaid_diagram(
            target_worker_set=self.worker_set,
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )

    def print_target_worker_mermaid_diagram(
        self,
        target_worker_set: set[BaseWorker],
        orientations: str = "LR",
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of target worker.

        Args:
            target_worker_set (set[BaseWorker]): List of target workers.
            orientations (str): Orientation of the flowchart. Defaults to "LR".
            print_worker (bool, optional): Print workers or not. Defaults to True.
            shape_worker (str, optional): Shape of workers in this team. Defaults to "stadium".
            link_type_str (str, optional): Link type string. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
        """
        list_of_lines = self.get_target_worker_mermaid_diagram(
            target_worker_set=target_worker_set,
            print_worker=print_worker,
            shape_worker=shape_worker,
            link_type_str=link_type_str,
            subgraph=subgraph,
            subgraph_direction=subgraph_direction,
        )
        print_mermaid_diagram_lines(orientations, list_of_lines)

    def print_mermaid_diagram(
        self,
        orientations: str = "LR",
        print_worker: bool = True,
        shape_worker: str = "stadium",
        link_type_str: str = "-->",
        subgraph: bool = True,
        subgraph_direction: str = "LR",
    ):
        """
        Print mermaid diagram of this team.

        Args:
            orientations (str): Orientation of the flowchart. Defaults to "LR".
            print_worker (bool, optional): Print workers or not. Defaults to True.
            shape_worker (str, optional): Shape of workers in this team. Defaults to "stadium".
            link_type_str (str, optional): Link type string. Defaults to "-->".
            subgraph (bool, optional): Whether to use subgraph or not. Defaults to True.
            subgraph_direction (str, optional): Direction of subgraph. Defaults to "LR".
        """
        super().print_mermaid_diagram(
            orientations=orientations,
            print_worker=print_worker,
            shape_worker=shape_worker,
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
        Get mermaid steps diagram of Gantt chart.

        Args:
            target_id_order_list (list[str], optional): Target ID order list. Defaults to None.
            section (bool, optional): Section or not. Defaults to True.
            range_time (tuple[int, int], optional): Range of Gantt chart. Defaults to (0, sys.maxsize).
            view_ready (bool, optional): Whether to include ready workers in the Gantt chart. Defaults to False.
            detailed_info (bool, optional): Whether to include detailed information in the Gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary mapping worker IDs to names. Defaults to None.

        Returns:
            list[str]: List of lines for mermaid steps diagram.
        """
        def steps_builder(worker, **kwargs):
            return worker.get_gantt_mermaid_steps_data(**kwargs)

        return self._build_collection_gantt_mermaid_steps(
            target_instance_set=self.worker_set,
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
            view_ready (bool, optional): Whether to include ready workers in the Gantt chart. Defaults to False.
            detailed_info (bool, optional): Whether to include detailed information in the Gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary mapping worker IDs to names. Defaults to None.

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
            detailed_info (bool, optional): Whether to include detailed information in the Gantt chart. Defaults to False.
            id_name_dict (dict[str, str], optional): Dictionary mapping worker IDs to names. Defaults to None.
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
