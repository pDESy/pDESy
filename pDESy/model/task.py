#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_task import BaseTask, BaseTaskState


class Task(BaseTask):
    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        default_work_amount=None,
        input_task_list=None,
        output_task_list=None,
        allocated_team_list=None,
        target_component_list=None,
        default_progress=None,
        # Advanced parameters for customized simulation
        due_date=None,
        additional_work_amount=None,
        # Basic variables
        est=0.0,
        eft=0.0,
        lst=-1.0,
        lft=-1.0,
        remaining_work_amount=None,
        state=BaseTaskState.NONE,
        ready_time_list=None,
        start_time_list=None,
        finish_time_list=None,
        allocated_worker_list=None,
        # Advanced variables for customized simulation
        additional_task_flag=False,
        # actual_work_amount=None,
    ):
        super().__init__(
            name,
            ID=ID,
            default_work_amount=default_work_amount,
            input_task_list=input_task_list,
            output_task_list=output_task_list,
            allocated_team_list=allocated_team_list,
            target_component_list=target_component_list,
            default_progress=default_progress,
            # Advanced parameters for customized simulation
            due_date=due_date,
            additional_work_amount=additional_work_amount,
            # Basic variables
            est=est,
            eft=eft,
            lst=lst,
            lft=lft,
            remaining_work_amount=remaining_work_amount,
            state=state,
            ready_time_list=ready_time_list,
            start_time_list=start_time_list,
            finish_time_list=finish_time_list,
            allocated_worker_list=allocated_worker_list,
            # Advanced variables for customized simulation
            additional_task_flag=additional_task_flag,
            # actual_work_amount=None,
        )
