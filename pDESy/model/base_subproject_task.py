#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_subproject_task."""

import datetime
import warnings

from pDESy.model.base_priority_rule import (
    ResourcePriorityRuleMode,
    WorkplacePriorityRuleMode,
)

from .base_task import BaseTask, BaseTaskState


class BaseSubProjectTask(BaseTask):
    """BaseSubProjectTask.

    BaseSubProjectTask class for expressing target sub project.

    Args:
        file_path (str, optional):
            File path of sub project data.
            Defaults to None.
        unit_timedelta (datetime.timedelta, optional):
            Unit time of simulation.
            Defaults to None -> datetime.timedelta(minutes=1).
        read_json_file (bool, optional):
            Read json file or not.
            Defaults to False.
        remove_absence_time_list (bool, optional):
            Remove absence_time_list or not.
            Defaults to False.
    """

    def __init__(
        self,
        file_path=None,
        unit_timedelta=None,
        read_json_file=False,
        remove_absence_time_list=False,
        # BaseTask
        # Basic parameters
        name=None,
        ID=None,
        default_work_amount=None,
        work_amount_progress_of_unit_step_time=None,
        input_task_list=None,
        output_task_list=None,
        allocated_team_list=None,
        allocated_workplace_list=None,
        parent_workflow=None,
        workplace_priority_rule=WorkplacePriorityRuleMode.FSS,
        worker_priority_rule=ResourcePriorityRuleMode.SSP,
        facility_priority_rule=ResourcePriorityRuleMode.SSP,
        need_facility=False,
        target_component=None,
        default_progress=None,
        due_time=None,
        auto_task=True,
        fixing_allocating_worker_id_list=None,
        fixing_allocating_facility_id_list=None,
        # Basic variables
        est=0.0,
        eft=0.0,
        lst=-1.0,
        lft=-1.0,
        remaining_work_amount=None,
        remaining_work_amount_record_list=None,
        state=BaseTaskState.NONE,
        state_record_list=None,
        allocated_worker_list=None,
        allocated_worker_id_record=None,
        allocated_facility_list=None,
        allocated_facility_id_record=None,
        # Advanced parameters for customized simulation
        additional_work_amount=None,
        # Advanced variables for customized simulation
        additional_task_flag=False,
        actual_work_amount=None,
    ):
        self.file_path = file_path
        self.unit_timedelta = (
            unit_timedelta
            if unit_timedelta is not None
            else datetime.timedelta(minutes=1)
        )
        self.read_json_fil_or_not = read_json_file
        self.remove_absence_time_list = remove_absence_time_list
        super().__init__(
            name=name,
            ID=ID,
            default_work_amount=default_work_amount,
            work_amount_progress_of_unit_step_time=work_amount_progress_of_unit_step_time,
            input_task_list=input_task_list,
            output_task_list=output_task_list,
            allocated_team_list=allocated_team_list,
            allocated_workplace_list=allocated_workplace_list,
            parent_workflow=parent_workflow,
            workplace_priority_rule=workplace_priority_rule,
            worker_priority_rule=worker_priority_rule,
            facility_priority_rule=facility_priority_rule,
            need_facility=need_facility,
            target_component=target_component,
            default_progress=default_progress,
            due_time=due_time,
            auto_task=auto_task,
            fixing_allocating_worker_id_list=fixing_allocating_worker_id_list,
            fixing_allocating_facility_id_list=fixing_allocating_facility_id_list,
            # Basic variables
            est=est,
            eft=eft,
            lst=lst,
            lft=lft,
            remaining_work_amount=remaining_work_amount,
            remaining_work_amount_record_list=remaining_work_amount_record_list,
            state=state,
            state_record_list=state_record_list,
            allocated_worker_list=allocated_worker_list,
            allocated_worker_id_record=allocated_worker_id_record,
            allocated_facility_list=allocated_facility_list,
            allocated_facility_id_record=allocated_facility_id_record,
            # Advanced parameters for customized simulation
            additional_work_amount=additional_work_amount,
            # Advanced variables for customized simulation
            additional_task_flag=additional_task_flag,
            actual_work_amount=actual_work_amount,
        )

    def set_all_attributes_from_json(
        self, file_path=None, remove_absence_time_list=True
    ):
        """
        Read json file which is created by BaseProject.write_simple_json().

        Args:
            file_path (str, optional):
                Json file path for reading sub this project data.
                Default to None -> self.file_path
            remove_absence_time_list (bool, optional):
                Remove absence_time_list information from target json file or not.
                Default to True.
        Returns:
            int: duration step time of target project.
            datetime.timedelta: unit time of target project.
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
                "Please call this function again after simulating the target project from pDESy json file."
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

    def set_work_amount_progress_of_unit_step_time(self, project_unit_timedelta):
        self.work_amount_progress_of_unit_step_time = (
            project_unit_timedelta / self.unit_timedelta
        )

    def export_dict_json_data(self):
        """
        Export the information of this task to JSON data.

        Returns:
            dict: JSON format data.
        """
        data = super().export_dict_json_data()
        data["file_path"] = self.file_path
        data["unit_timedelta"] = str(self.unit_timedelta.total_seconds())
        data["remove_absence_time_list"] = self.remove_absence_time_list
        data["read_json_file"] = self.read_json_file
        return data
