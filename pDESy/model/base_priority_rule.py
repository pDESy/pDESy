#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


class ResourcePriorityRuleMode(IntEnum):
    """ResourcePriorityRuleMode"""

    SSP = 0
    VC = 1
    HSV = 2


class TaskPriorityRuleMode(IntEnum):
    """TaskPriorityRuleMode"""

    TSLACK = 0
    EST = 1  # Earliest Start Time
    SPT = 2  # Shortest Processing Time
    LPT = 3  # Longest Processing Time
    FIFO = 4  # First in First Out
    LRPT = 5  # Longest Remaining Process Time
    SRPT = 6  # Shortest Remaining Process Time
    LWRPT = 7  # Longest Workflow Remaining Process Time
    SWRPT = 8  # Shortest Workflow Remaining Process Time


def sort_resource_list(
    resource_list, priority_rule_mode=ResourcePriorityRuleMode.SSP, **kwargs
):
    """
    Sort resource_list as priority_rule_mode.

    Args:
        resource_list (List[BaseResource]):
            Target resource list of sorting.
            BaseWorker and BaseFacility are one of resource type in this repository.
        priority_rule_mode (ResourcePriorityRuleMode, optional):
            Mode of priority rule for sorting.
            Defaults to ResourcePriorityRuleMode.SSP
        args:
            Other information of each rule.
    Returns:
        List[BaseResource]: resource_list after sorted
    """

    # SSP: a resource which amount of skillpoint is lower has high priority
    if priority_rule_mode == ResourcePriorityRuleMode.SSP:
        resource_list = sorted(
            resource_list,
            key=lambda resource: sum(resource.workamount_skill_mean_map.values()),
        )
    # VC :a resource which cost is lower has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.VC:
        resource_list = sorted(
            resource_list,
            key=lambda resource: (resource.cost_per_time),
        )
    # HSV: a resource which target skillpoint is higher has high priority
    elif priority_rule_mode == ResourcePriorityRuleMode.HSV:
        resource_list = sorted(
            resource_list,
            key=lambda resource: resource.workamount_skill_mean_map[kwargs["name"]],
            reverse=True,
        )

    return resource_list


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
