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
        auto_task (bool, optional):
            Basic parameter.
            If True, this task is performed automatically
            even if there are no allocated workers.
            Default to False.
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
        allocated_worker_id_record (List[List[str]], optional):
            Basic variable.
            State of allocating resource id list in simumation.
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
        auto_task=False,
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
        allocated_worker_id_record=None,
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
            auto_task=auto_task,
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
            allocated_worker_id_record=allocated_worker_id_record,
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
        - allocated_worker_id_record
        - additional_task_flag
        - actual_work_amount
        """
        super().initialize(error_tol=error_tol)

        self.additional_task_flag = False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )

    def perform(self, time: int, seed=None, increase_component_error=1.0):
        """
        @override BaseTask.perform()
        Perform this Task in this simulation

        Args:
            time (int):
                Simulation time executing this method.
            seed (int, optional):
                Random seed for describing deviation of progress.
                If workamount
                Defaults to None.
            increase_component_error (float, optional):
                For advanced simulation.
                Increment error value when error has occurred.
                Defaults to 1.0.
        Note:
            This method includes advanced code of custom simulation.
            We have to separete basic code and advanced code in the future.
        """
        if self.state == BaseTaskState.WORKING:
            work_amount_progress = 0.0
            noErrorProbability = 1.0
            if self.auto_task:
                work_amount_progress = 1.0
            else:
                for worker in self.allocated_worker_list:
                    work_amount_progress = (
                        work_amount_progress
                        + worker.get_work_amount_skill_progress(self.name, seed=seed)
                    )
                    noErrorProbability = (
                        noErrorProbability
                        - worker.get_quality_skill_point(self.name, seed=seed)
                    )

            self.remaining_work_amount = (
                self.remaining_work_amount - work_amount_progress
            )
            for component in self.target_component_list:
                component.update_error_value(
                    noErrorProbability, increase_component_error, seed=seed
                )
        else:
            pass
