#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_task import BaseTask, BaseTaskState


class Task(BaseTask):
    """Task
    Task class for expressing target workflow.
    This class is implemented from BaseTask.

    Args:
        name (str):
            Basic parameter.
            Name of this team.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        default_work_amount (float, optional):
            Basic parameter.
            Defalt workamount of this BaseTask.
            Defaults to None -> 10.0.
        input_task_list (List[BaseTask], optional):
            Basic parameter.
            List of input BaseTask.
            Defaults to None -> [].
        output_task_list (List[BaseTask], optional):
            Basic parameter.
            List of output BaseTask.
            Defaults to None -> [].
        allocated_team_list (List[BaseTeam], optional):
            Basic parameter.
            List of allocated BaseTeam
            Defaults to None -> [].
        target_component_list (List[BaseComponent], optional):
            Basic parameter.
            List of target BaseCompoenent.
            Defaults to None -> [].
        default_progress (float, optional):
            Basic parameter.
            Progress before starting simulation (0.0 ~ 1.0)
            Defaults to None -> 0.0.
        due_date (int, optional):
            Advanced parameter.
            Defaults to None -> int(-1).
        additional_work_amount (float, optional):
            Advanced parameter.
            Defaults to None.
        est (float, optional):
            Basic variable.
            Earliest start time of CPM. This will be updated step by step.
            Defaults to 0.0.
        eft (float, optional):
            Basic variable.
            Earliest finish time of CPM. This will be updated step by step.
            Defaults to 0.0.
        lst (float, optional):
            Basic variable.
            Latest start time of CPM. This will be updated step by step.
            Defaults to -1.0.
        lft (float, optional):
            Basic variable.
            Latest finish time of CPM. This will be updated step by step.
            Defaults to -1.0.
        remaining_work_amount (float, optional):
            Basic variable.
            Remaining workamount in simulation.
            Defaults to None -> default_work_amount * (1.0 - default_progress).
        state (BaseTaskState, optional):
            Basic variable.
            State of this task in simulation.
            Defaults to BaseTaskState.NONE.
        ready_time_list (List[float], optional):
            Basic variable.
            History or record of READY time in simumation.
            Defaults to None -> [].
        start_time_list (List[float], optional):
            Basic variable.
            History or record of start WORKING time in simumation.
            Defaults to None -> [].
        finish_time_list (List[float], optional):
            Basic variable.
            History or record of finish WORKING time in simumation.
            Defaults to None -> [].
        allocated_worker_list (List[BaseResource], optional):
            Basic variable.
            State of allocating resource list in simumation.
            Defaults to None -> [].
        additional_task_flag (bool, optional):
            Advanced variable.
            Defaults to False.
    """

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
        actual_work_amount=None,
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
        )
        # --
        # Advanced parameter for customized simulation
        self.due_date = due_date if due_date is not None else int(-1)
        self.additional_work_amount = (
            additional_work_amount if additional_work_amount is not None else 0.0
        )
        # --
        # Advanced varriables for customized simulation
        if additional_task_flag is not False:
            self.additional_task_flag = additional_task_flag
        else:
            self.additional_task_flag = False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )

    def initialize(self, error_tol=1e-10):
        """
        Initialize the changeable variables of Task

        - est
        - eft
        - lst
        - lft
        - remaining_work_amount
        - state
        - ready_time_list
        - start_time_list
        - finish_time_list
        - allocated_worker_list
        - additional_task_flag
        - actual_work_amount
        """
        super().initialize(error_tol=error_tol)

        self.additional_task_flag = False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )
