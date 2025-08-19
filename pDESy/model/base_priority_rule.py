#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_priority_rule.

This module defines enums and functions for sorting workplaces, workers, facilities, and tasks
according to various priority rules.
"""

from enum import IntEnum


class WorkplacePriorityRuleMode(IntEnum):
    """Enum for workplace priority rule modes.

    Attributes:
        FSS (int): Free Space Size.
        SSP (int): Sum Skill Points of targeted task.
    """

    FSS = 0  # Free Space Size
    SSP = 1  # Sum Skill Points of targeted task


class ResourcePriorityRuleMode(IntEnum):
    """Enum for resource (worker/facility) priority rule modes.

    Attributes:
        MW (int): A worker whose main workplace is equal to target has high priority.
        SSP (int): A worker/facility with lower skill point sum has high priority.
        VC (int): A worker/facility with lower cost has high priority.
        HSV (int): A worker/facility with higher target skill point has high priority.
    """

    MW = -1  # a worker whose main workplace is equal to target has high priority
    SSP = 0  # a worker which amount of skill point is lower has high priority
    VC = 1  # a worker which cost is lower has high priority
    HSV = 2  # a worker which target skill point is higher has high priority


class TaskPriorityRuleMode(IntEnum):
    """Enum for task priority rule modes.

    Attributes:
        TSLACK (int): Task with lower slack time has high priority.
        EST (int): Earliest Start Time.
        SPT (int): Shortest Processing Time.
        LPT (int): Longest Processing Time.
        FIFO (int): First in First Out.
        LRPT (int): Longest Remaining Process Time.
        SRPT (int): Shortest Remaining Process Time.
    """

    TSLACK = 0
    EST = 1  # Earliest Start Time
    SPT = 2  # Shortest Processing Time
    LPT = 3  # Longest Processing Time
    FIFO = 4  # First in First Out
    LRPT = 5  # Longest Remaining Process Time
    SRPT = 6  # Shortest Remaining Process Time


def sort_workplace_list(
    workplace_list: list, priority_rule_mode=WorkplacePriorityRuleMode.FSS, **kwargs
):
    """Sort workplace_list as priority_rule_mode.

    Args:
        workplace_list (List[BaseWorkplace]): Target workplace list of sorting.
        priority_rule_mode (WorkplacePriorityRuleMode, optional): Mode of priority rule for sorting. Defaults to WorkplacePriorityRuleMode.FSS.
        **kwargs: Other information of each rule.

    Returns:
        List[BaseWorkplace]: workplace_list after sorted.
    """
    # FSS: Free Space Size
    if priority_rule_mode == WorkplacePriorityRuleMode.FSS:
        workplace_list = sorted(
            workplace_list,
            key=lambda workplace: workplace.available_space_size,
            reverse=True,
        )
    # SSP: Sum Skill Points of targeted task
    elif priority_rule_mode == WorkplacePriorityRuleMode.SSP:

        task_name = kwargs.get("name")
        if task_name is None:
            raise ValueError("Task name must be provided for SSP mode.")

        skill_point_cache = {}

        def count_sum_skill_point(wp, task_name):
            if wp in skill_point_cache:
                return skill_point_cache[wp]
            skill_points = sum(
                facility.workamount_skill_mean_map[task_name]
                for facility in wp.facility_set
                if facility.has_workamount_skill(task_name)
            )
            skill_point_cache[wp] = skill_points
            return skill_points

        workplace_list = sorted(
            workplace_list,
            key=lambda workplace: count_sum_skill_point(workplace, task_name),
            reverse=True,
        )
    return workplace_list


def sort_worker_list(
    worker_list: list,
    priority_rule_mode=ResourcePriorityRuleMode.SSP,
    **kwargs,
):
    """Sort worker_list as priority_rule_mode.

    Args:
        worker_list (List[BaseWorker]): Target worker list of sorting.
        priority_rule_mode (ResourcePriorityRuleMode, optional): Mode of priority rule for sorting. Defaults to ResourcePriorityRuleMode.SSP.
        **kwargs: Other information of each rule.

    Returns:
        List[BaseWorker]: worker_list after sorted.
    """
    target_workplace_id = None
    if "workplace_id" in kwargs:
        target_workplace_id = kwargs["workplace_id"]

    skill_point_sum_dict = {
        w: sum(w.workamount_skill_mean_map.values()) for w in worker_list
    }

    # MW: a worker whose main workplace is equal to target has high priority
    if priority_rule_mode == ResourcePriorityRuleMode.MW:
        worker_list = sorted(
            worker_list,
            key=lambda worker: (
                worker.main_workplace_id is not target_workplace_id,  # MW1
                worker.main_workplace_id is not None,  # MW2
                skill_point_sum_dict[worker],  # SSP (additional)
            ),
        )
    # SSP: a worker which amount of skill point is lower has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.SSP:
        worker_list = sorted(
            worker_list,
            key=lambda worker: (
                skill_point_sum_dict[worker],
                worker.main_workplace_id is not target_workplace_id,
                worker.main_workplace_id is not None,
            ),
        )
    # VC: a worker which cost is lower has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.VC:
        worker_list = sorted(
            worker_list,
            key=lambda worker: (
                worker.cost_per_time,
                worker.main_workplace_id is not target_workplace_id,
                worker.main_workplace_id is not None,
            ),
        )
    # HSV: a worker which target skill point is higher has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.HSV:
        task_name = kwargs.get("name")
        if task_name is None:
            raise ValueError("task name must be provided for HSV mode.")
        worker_list = sorted(
            worker_list,
            key=lambda worker: (
                -worker.workamount_skill_mean_map.get(task_name, -float("inf")),
                worker.main_workplace_id is not target_workplace_id,
                worker.main_workplace_id is not None,
            ),
        )

    return worker_list


def sort_facility_list(
    facility_list: list,
    priority_rule_mode=ResourcePriorityRuleMode.SSP,
    **kwargs,
):
    """Sort facility_list as priority_rule_mode.

    Args:
        facility_list (List[BaseFacility]): Target facility list of sorting.
        priority_rule_mode (ResourcePriorityRuleMode, optional): Mode of priority rule for sorting. Defaults to ResourcePriorityRuleMode.SSP.
        **kwargs: Other information of each rule.

    Returns:
        List[BaseFacility]: facility_list after sorted.
    """
    facility_skill_sum = {
        f: sum(f.workamount_skill_mean_map.values()) for f in facility_list
    }
    # SSP: a facility which amount of skill point is lower has high priority
    if priority_rule_mode == ResourcePriorityRuleMode.SSP:
        facility_list = sorted(
            facility_list,
            key=lambda facility: facility_skill_sum[facility],
        )
    # VC :a facility which cost is lower has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.VC:
        facility_list = sorted(
            facility_list,
            key=lambda facility: (facility.cost_per_time),
        )
    # HSV: a facility which target skill point is higher has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.HSV:
        task_name = kwargs.get("name")
        if task_name is None:
            raise ValueError("task name must be provided for HSV mode.")
        facility_list = sorted(
            facility_list,
            key=lambda facility: facility.workamount_skill_mean_map.get(
                task_name, -float("inf")
            ),
            reverse=True,
        )

    return facility_list


def sort_task_list(
    task_list: list,
    priority_rule_mode=TaskPriorityRuleMode.TSLACK,
):
    """Sort task_list as priority_rule_mode.

    Args:
        task_list (List[BaseTask]): Target task list of sorting.
        priority_rule_mode (TaskPriorityRuleMode, optional): Mode of priority rule for sorting. Defaults to TaskPriorityRuleMode.TSLACK.

    Returns:
        List[BaseTask]: task_list after sorted.
    """
    # Task: TSLACK (a task which Slack time(LS-ES) is lower has high priority)
    if priority_rule_mode == TaskPriorityRuleMode.TSLACK:
        task_list = sorted(task_list, key=lambda task: task.lst - task.est)

    elif priority_rule_mode == TaskPriorityRuleMode.EST:
        # Task: EST (a task which EST is lower has high priority)
        task_list = sorted(task_list, key=lambda task: task.est)

    elif priority_rule_mode == TaskPriorityRuleMode.SPT:
        # Task: SPT (a task which default_work_amount is lower has high priority)
        task_list = sorted(task_list, key=lambda task: task.default_work_amount)

    elif priority_rule_mode == TaskPriorityRuleMode.LPT:
        # Task: LPT (a task which default_work_amount is higher has high priority)
        task_list = sorted(
            task_list, key=lambda task: task.default_work_amount, reverse=True
        )
    elif priority_rule_mode == TaskPriorityRuleMode.FIFO:
        # Task: FIFO (First In First Out rule)
        ready_count_cache = {}

        def count_ready(x):
            if x in ready_count_cache:
                return ready_count_cache[x]
            k = x.state_record_list
            num = sum(1 for state in k if state.name == "READY")
            ready_count_cache[x] = num
            return num

        task_list = sorted(task_list, key=count_ready, reverse=True)

    elif priority_rule_mode == TaskPriorityRuleMode.LRPT:
        # Task: LRPT (Longest Remaining Process Time)
        task_list = sorted(
            task_list,
            key=lambda task: task.remaining_work_amount,
            reverse=True,
        )
    elif priority_rule_mode == TaskPriorityRuleMode.SRPT:
        # Task: SRPT (Shortest Remaining Process Time)
        task_list = sorted(
            task_list,
            key=lambda task: task.remaining_work_amount,
        )
    return task_list
