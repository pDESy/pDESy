#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""BaseSubProjectTask module.

This module provides the BaseSubProjectTask class for expressing target sub projects.

Classes:
    BaseSubProjectTask: A class representing a sub project task, inheriting from BaseTask.
"""

import datetime
import warnings

from pDESy.model.base_priority_rule import (
    ResourcePriorityRuleMode,
    WorkplacePriorityRuleMode,
)

from .base_task import BaseTask, BaseTaskState


class BaseSubProjectTask(BaseTask):
    """A class representing a sub project task.

    This class is used for expressing a target sub project within the simulation.
    """

    def __init__(
        self,
        file_path: str = None,
        unit_timedelta: datetime.timedelta = None,
        read_json_file: bool = False,
        remove_absence_time_list: bool = False,
        # BaseTask
        # Basic parameters
        name: str = None,
        ID: str = None,
        default_work_amount: float = None,
        work_amount_progress_of_unit_step_time: float = None,
        input_task_id_dependency_set: set = None,
        allocated_team_id_set: set = None,
        allocated_workplace_id_set: set = None,
        parent_workflow_id: str = None,
        workplace_priority_rule: WorkplacePriorityRuleMode = WorkplacePriorityRuleMode.FSS,
        worker_priority_rule: ResourcePriorityRuleMode = ResourcePriorityRuleMode.SSP,
        facility_priority_rule: ResourcePriorityRuleMode = ResourcePriorityRuleMode.SSP,
        need_facility: bool = False,
        target_component_id: str = None,
        default_progress: float = None,
        due_time: float = None,
        auto_task: bool = True,
        fixing_allocating_worker_id_set: set = None,
        fixing_allocating_facility_id_set: set = None,
        # Basic variables
        est: float = 0.0,
        eft: float = 0.0,
        lst: float = -1.0,
        lft: float = -1.0,
        remaining_work_amount: float = None,
        remaining_work_amount_record_list: list = None,
        state: BaseTaskState = BaseTaskState.NONE,
        state_record_list: list = None,
        allocated_worker_facility_id_tuple_set: set = None,
        allocated_worker_facility_id_tuple_set_record_list: list = None,
        # Advanced parameters for customized simulation
        additional_work_amount: float = None,
        # Advanced variables for customized simulation
        additional_task_flag: bool = False,
        actual_work_amount: float = None,
    ):
        """Initializes a BaseSubProjectTask.

        Args:
            file_path (str, optional): File path of sub project data. Defaults to None.
            unit_timedelta (datetime.timedelta, optional): Unit time of simulation. Defaults to None, which means datetime.timedelta(minutes=1).
            read_json_file (bool, optional): Whether to read a JSON file. Defaults to False.
            remove_absence_time_list (bool, optional): Whether to remove absence_time_list. Defaults to False.
            name (str, optional): Name of the task.
            ID (str, optional): ID of the task.
            default_work_amount (float, optional): Default work amount.
            work_amount_progress_of_unit_step_time (float, optional): Work amount progress per unit step time.
            input_task_id_dependency_set (set, optional): Set of input task ID dependencies.
            allocated_team_id_set (set, optional): Set of allocated team IDs.
            allocated_workplace_id_set (set, optional): Set of allocated workplace IDs.
            parent_workflow_id (str, optional): Parent workflow ID.
            workplace_priority_rule (WorkplacePriorityRuleMode, optional): Workplace priority rule.
            worker_priority_rule (ResourcePriorityRuleMode, optional): Worker priority rule.
            facility_priority_rule (ResourcePriorityRuleMode, optional): Facility priority rule.
            need_facility (bool, optional): Whether a facility is needed.
            target_component_id (str, optional): Target component ID.
            default_progress (float, optional): Default progress.
            due_time (float, optional): Due time.
            auto_task (bool, optional): Whether the task is automatic.
            fixing_allocating_worker_id_set (set, optional): Set of fixed allocating worker IDs.
            fixing_allocating_facility_id_set (set, optional): Set of fixed allocating facility IDs.
            est (float, optional): Earliest start time.
            eft (float, optional): Earliest finish time.
            lst (float, optional): Latest start time.
            lft (float, optional): Latest finish time.
            remaining_work_amount (float, optional): Remaining work amount.
            remaining_work_amount_record_list (list, optional): Record list of remaining work amount.
            state (BaseTaskState, optional): State of the task.
            state_record_list (list, optional): Record list of states.
            allocated_worker_facility_id_tuple_set (set, optional): Set of allocated worker/facility ID tuples.
            allocated_worker_facility_id_tuple_set_record_list (list, optional): Record list of allocated worker/facility ID tuples.
            additional_work_amount (float, optional): Additional work amount for customized simulation.
            additional_task_flag (bool, optional): Additional task flag for customized simulation.
            actual_work_amount (float, optional): Actual work amount for customized simulation.
        """
        self.file_path = file_path
        self.unit_timedelta = (
            unit_timedelta
            if unit_timedelta is not None
            else datetime.timedelta(minutes=1)
        )
        self.read_json_file = read_json_file
        self.remove_absence_time_list = remove_absence_time_list
        super().__init__(
            name=name,
            ID=ID,
            default_work_amount=default_work_amount,
            work_amount_progress_of_unit_step_time=work_amount_progress_of_unit_step_time,
            input_task_id_dependency_set=input_task_id_dependency_set,
            allocated_team_id_set=allocated_team_id_set,
            allocated_workplace_id_set=allocated_workplace_id_set,
            parent_workflow_id=parent_workflow_id,
            workplace_priority_rule=workplace_priority_rule,
            worker_priority_rule=worker_priority_rule,
            facility_priority_rule=facility_priority_rule,
            need_facility=need_facility,
            target_component_id=target_component_id,
            default_progress=default_progress,
            due_time=due_time,
            auto_task=auto_task,
            fixing_allocating_worker_id_set=fixing_allocating_worker_id_set,
            fixing_allocating_facility_id_set=fixing_allocating_facility_id_set,
            # Basic variables
            est=est,
            eft=eft,
            lst=lst,
            lft=lft,
            remaining_work_amount=remaining_work_amount,
            remaining_work_amount_record_list=remaining_work_amount_record_list,
            state=state,
            state_record_list=state_record_list,
            allocated_worker_facility_id_tuple_set=allocated_worker_facility_id_tuple_set,
            allocated_worker_facility_id_tuple_set_record_list=allocated_worker_facility_id_tuple_set_record_list,
            # Advanced parameters for customized simulation
            additional_work_amount=additional_work_amount,
            # Advanced variables for customized simulation
            additional_task_flag=additional_task_flag,
            actual_work_amount=actual_work_amount,
        )

    def set_all_attributes_from_json(
        self, file_path: str = None, remove_absence_time_list: bool = True
    ):
        """Reads attributes from a JSON file created by BaseProject.write_simple_json().

        Args:
            file_path (str, optional): JSON file path for reading sub project data. Defaults to None, which uses self.file_path.
            remove_absence_time_list (bool, optional): Whether to remove absence_time_list information from the JSON file. Defaults to True.

        Returns:
            int: Duration step time of the target project.
            datetime.timedelta: Unit time of the target project.
        """

        from .base_project import (
            BaseProject,
            BaseProjectStatus,
        )  # for avoiding circular import error

        file_path = file_path if file_path is not None else self.file_path
        # make project from json file
        project = BaseProject()
        project.read_simple_json(file_path)
        if project.status != BaseProjectStatus.FINISHED_SUCCESS:
            warnings.warn(
                "The target pDESy json file is not simulated. Some error will be occurred."
                "Call this function again after simulating the target project from pDESy json file."
            )
            return (
                -1,
                datetime.timedelta(days=1),
            )

        # remove absence_time_list info
        if remove_absence_time_list:
            project.remove_absence_time_list()

        self.remove_absence_time_list = remove_absence_time_list
        self.read_json_file = True
        self.default_work_amount = project.time
        self.unit_timedelta = project.unit_timedelta

    def set_work_amount_progress_of_unit_step_time(
        self, project_unit_timedelta: datetime.timedelta
    ):
        """Sets the work amount progress of unit step time.

        Args:
            project_unit_timedelta (datetime.timedelta): The unit time of the project.
        """
        self.work_amount_progress_of_unit_step_time = (
            project_unit_timedelta / self.unit_timedelta
        )

    def export_dict_json_data(self):
        """Exports the information of this task to a JSON-serializable dictionary.

        Returns:
            dict: JSON format data.
        """
        data = super().export_dict_json_data()
        data["file_path"] = self.file_path
        data["unit_timedelta"] = str(self.unit_timedelta.total_seconds())
        data["remove_absence_time_list"] = self.remove_absence_time_list
        data["read_json_file"] = self.read_json_file
        return data
