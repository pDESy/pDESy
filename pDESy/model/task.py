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
        allocated_workplace_list (List[BaseWorkplace], optional):
            Basic parameter.
            List of allocated BaseWorkplace
            Defaults to None -> [].
        need_facility (bool, optional):
            Basic parameter.
            Whether one facility is needed for performing this task or not.
            Default to False
        target_component (BaseComponent, optional):
            Basic parameter.
            Target BaseComponent.
            Defaults to None.
        default_progress (float, optional):
            Basic parameter.
            Progress before starting simulation (0.0 ~ 1.0)
            Defaults to None -> 0.0.
        due_time (int, optional):
            Basic parameter.
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
        allocated_worker_list (List[BaseWorker], optional):
            Basic variable.
            State of allocating worker list in simulation.
            Defaults to None -> [].
        allocated_worker_id_record (List[List[str]], optional):
            Basic variable.
            State of allocating worker id list in simulation.
            Defaults to None -> [].
        allocated_facility_list (List[BaseFacility], optional):
            Basic variable.
            State of allocating facility list in simulation.
            Defaults to None -> [].
        allocated_facility_id_record (List[List[str]], optional):
            Basic variable.
            State of allocating facility id list in simulation.
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
        allocated_workplace_list=None,
        need_facility=False,
        target_component=None,
        default_progress=None,
        due_time=None,
        auto_task=False,
        # Advanced parameters for customized simulation
        additional_work_amount=None,
        # Basic variables
        est=0.0,
        eft=0.0,
        lst=-1.0,
        lft=-1.0,
        remaining_work_amount=None,
        state=BaseTaskState.NONE,
        allocated_worker_list=None,
        allocated_worker_id_record=None,
        allocated_facility_list=None,
        allocated_facility_id_record=None,
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
            allocated_workplace_list=allocated_workplace_list,
            need_facility=need_facility,
            target_component=target_component,
            default_progress=default_progress,
            due_time=due_time,
            auto_task=auto_task,
            # Basic variables
            est=est,
            eft=eft,
            lst=lst,
            lft=lft,
            remaining_work_amount=remaining_work_amount,
            state=state,
            allocated_worker_list=allocated_worker_list,
            allocated_worker_id_record=allocated_worker_id_record,
            allocated_facility_list=allocated_facility_list,
            allocated_facility_id_record=allocated_facility_id_record,
        )
        # --
        # Advanced parameter for customized simulation
        self.additional_work_amount = (
            additional_work_amount if additional_work_amount is not None else 0.0
        )
        # --
        # Advanced variables for customized simulation
        if additional_task_flag is not False:
            self.additional_task_flag = additional_task_flag
        else:
            self.additional_task_flag = False
        self.actual_work_amount = self.default_work_amount * (
            1.0 - self.default_progress
        )

    def initialize(self, error_tol=1e-10, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of Task.
        If `state_info` is True, the following attributes are initialized
        in addition to 'BaseTask.initialize()'.

          - additional_task_flag
          - actual_work_amount

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        super().initialize(error_tol=error_tol, state_info=True, log_info=True)

        if state_info:
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
                # for worker in self.allocated_worker_list:
                #     work_amount_progress = (
                #         work_amount_progress
                #         + worker.get_work_amount_skill_progress(self.name, seed=seed)
                #     )
                #     noErrorProbability = (
                #         noErrorProbability
                #         - worker.get_quality_skill_point(self.name, seed=seed)
                #     )
                if self.need_facility:
                    min_length = min(
                        len(self.allocated_worker_list),
                        len(self.allocated_facility_list),
                    )
                    for i in range(min_length):
                        worker = self.allocated_worker_list[i]
                        w_progress = worker.get_work_amount_skill_progress(
                            self.name, seed=seed
                        )
                        facility = self.allocated_facility_list[i]
                        f_progress = facility.get_work_amount_skill_progress(
                            self.name, seed=seed
                        )
                        work_amount_progress += w_progress * f_progress

                        noErrorProbability = (
                            noErrorProbability
                            - worker.get_quality_skill_point(self.name, seed=seed)
                        )
                else:
                    for worker in self.allocated_worker_list:
                        work_amount_progress = (
                            work_amount_progress
                            + worker.get_work_amount_skill_progress(
                                self.name, seed=seed
                            )
                        )
                        noErrorProbability = (
                            noErrorProbability
                            - worker.get_quality_skill_point(self.name, seed=seed)
                        )

            self.remaining_work_amount = (
                self.remaining_work_amount - work_amount_progress
            )

            if self.target_component is not None:
                self.target_component.update_error_value(
                    noErrorProbability, increase_component_error, seed=seed
                )
        else:
            pass
