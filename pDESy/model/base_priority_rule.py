#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum
import abc


class ResourcePriorityRuleMode(IntEnum):
    """ResourcePriorityRuleMode"""

    SSP = 0


class TaskPriorityRuleMode(IntEnum):
    """TaskPriorityRuleMode"""

    TSLACK = 0
    EST = 1  # Earliest Start Time
    SPT = 2  # Shortest Processing Time
    LPT = 3  # Longest Processing Time


class BasePriorityRule(object, metaclass=abc.ABCMeta):
    """BasePriorityRule
    BasePriorityRule for expressing dispatching rule.
    """

    def sort_resource_list(
        resource_list, priority_rule_mode=ResourcePriorityRuleMode.SSP
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
        Returns:
            List[BaseResource]: resource_list after sorted
        """

        # SSP: a resource which amount of skillpoint is lower has high priority
        if priority_rule_mode == ResourcePriorityRuleMode.SSP:
            resource_list = sorted(
                resource_list,
                key=lambda resource: sum(resource.workamount_skill_mean_map.values()),
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

        return task_list
