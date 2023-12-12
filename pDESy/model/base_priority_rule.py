#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_priority_rule."""

from enum import IntEnum


class WorkplacePriorityRuleMode(IntEnum):
    """WorkplacePriorityRuleMode."""

    FSS = 0  # Free Space Size
    SSP = 1  # Sum Skill Points of targeted task


class ResourcePriorityRuleMode(IntEnum):
    """ResourcePriorityRuleMode."""

    MW = -1  # a worker whose main workplace is equal to target has high priority
    SSP = 0  # a worker which amount of skill point is lower has high priority
    VC = 1  # a worker which cost is lower has high priority
    HSV = 2  # a worker which target skill point is higher has high priority


class TaskPriorityRuleMode(IntEnum):
    """TaskPriorityRuleMode."""

    TSLACK = 0
    EST = 1  # Earliest Start Time
    SPT = 2  # Shortest Processing Time
    LPT = 3  # Longest Processing Time
    FIFO = 4  # First in First Out
    LRPT = 5  # Longest Remaining Process Time
    SRPT = 6  # Shortest Remaining Process Time
    LWRPT = 7  # Longest Workflow Remaining Process Time
    SWRPT = 8  # Shortest Workflow Remaining Process Time


def sort_workplace_list(
    workplace_list, priority_rule_mode=WorkplacePriorityRuleMode.FSS, **kwargs
):
    """
    Sort workplace_list as priority_rule_mode.

    Args:
        workplace_list (List[BaseWorkplace]):
            Target workplace list of sorting.
        priority_rule_mode (WorkplacePriorityRuleMode, optional):
            Mode of priority rule for sorting.
            Defaults to WorkplacePriorityRuleMode.FSS
        args:
            Other information of each rule.
    Returns:
        List[BaseWorkplace]: resource_list after sorted
    """
    # FSS: Free Space Size
    if priority_rule_mode == WorkplacePriorityRuleMode.FSS:
        workplace_list = sorted(
            workplace_list,
            key=lambda workplace: workplace.get_available_space_size(),
            reverse=True,
        )
    # SSP: Sum Skill Points of targeted task
    elif priority_rule_mode == WorkplacePriorityRuleMode.SSP:

        def count_sum_skill_point(wp, task_name):
            skill_points = sum(
                [
                    facility.workamount_skill_mean_map[task_name]
                    for facility in wp.facility_list
                    if facility.has_workamount_skill(task_name)
                ]
            )
            return skill_points

        workplace_list = sorted(
            workplace_list,
            key=lambda workplace: count_sum_skill_point(workplace, kwargs["name"]),
            reverse=True,
        )
    return workplace_list


def sort_worker_list(
    worker_list, priority_rule_mode=ResourcePriorityRuleMode.SSP, **kwargs
):
    """
    Sort worker_list as priority_rule_mode.

    Args:
        worker_list (List[BaseWorker]):
            Target worker list of sorting.
        priority_rule_mode (ResourcePriorityRuleMode, optional):
            Mode of priority rule for sorting.
            Defaults to ResourcePriorityRuleMode.SSP
        args:
            Other information of each rule.
    Returns:
        List[BaseWorker]: worker_list after sorted
    """
    target_workplace_id = None
    if "workplace_id" in kwargs:
        target_workplace_id = kwargs["workplace_id"]

    # MW: a worker whose main workplace is equal to target has high priority
    if priority_rule_mode == ResourcePriorityRuleMode.MW:
        worker_list = sorted(
            worker_list,
            key=lambda worker: (
                worker.main_workplace_id is not target_workplace_id,  # MW1
                worker.main_workplace_id is not None,  # MW2
                sum(worker.workamount_skill_mean_map.values()),  # SSP (additional)
            ),
        )
    # SSP: a worker which amount of skill point is lower has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.SSP:
        worker_list = sorted(
            worker_list,
            key=lambda worker: (
                sum(worker.workamount_skill_mean_map.values()),
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
        worker_list = sorted(
            worker_list,
            key=lambda worker: (
                -worker.workamount_skill_mean_map.get(kwargs["name"], -float("inf")),
                worker.main_workplace_id is not target_workplace_id,
                worker.main_workplace_id is not None,
            ),
        )

    return worker_list


def sort_facility_list(
    facility_list, priority_rule_mode=ResourcePriorityRuleMode.SSP, **kwargs
):
    """
    Sort facility_list as priority_rule_mode.

    Args:
        facility_list (List[BaseFacility]):
            Target facility list of sorting.
        priority_rule_mode (ResourcePriorityRuleMode, optional):
            Mode of priority rule for sorting.
            Defaults to ResourcePriorityRuleMode.SSP
        args:
            Other information of each rule.
    Returns:
        List[BaseFacility]: facility_list after sorted
    """
    # SSP: a facility which amount of skill point is lower has high priority
    if priority_rule_mode == ResourcePriorityRuleMode.SSP:
        facility_list = sorted(
            facility_list,
            key=lambda facility: sum(facility.workamount_skill_mean_map.values()),
        )
    # VC :a facility which cost is lower has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.VC:
        facility_list = sorted(
            facility_list,
            key=lambda facility: (facility.cost_per_time),
        )
    # HSV: a facility which target skill point is higher has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.HSV:
        facility_list = sorted(
            facility_list,
            key=lambda facility: facility.workamount_skill_mean_map.get(
                kwargs["name"], -float("inf")
            ),
            reverse=True,
        )

    return facility_list


def sort_task_list(task_list, priority_rule_mode=TaskPriorityRuleMode.TSLACK):
    """
    Sort task_list as priority_rule_mode.

    Args:
        task_list (List[BaseTask]):
            Target task list of sorting.
        priority_rule_mode (ResourcePriorityRuleMode, optional):
            Mode of priority rule for sorting.
            Defaults to TaskPriorityRuleMode.TSLACK
    Returns:
        List[BaseTask]: task_list after sorted
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
        def count_ready(x):
            k = x.state_record_list
            num = len([i for i in range(len(k)) if k[i].name == "READY"])
            return num

        task_list = sorted(task_list, key=lambda task: count_ready(task), reverse=True)
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
    elif priority_rule_mode == TaskPriorityRuleMode.LWRPT:
        # Task: LWRPT (Longest Workflow Remaining Process Time)
        task_list = sorted(
            task_list,
            key=lambda task: task.parent_workflow.critical_path_length,
            reverse=True,
        )
    elif priority_rule_mode == TaskPriorityRuleMode.SWRPT:
        # Task: SWRPT (Shortest Workflow Remaining Process Time)
        task_list = sorted(
            task_list,
            key=lambda task: task.parent_workflow.critical_path_length,
        )

    return task_list
