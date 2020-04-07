#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from enum import IntEnum

class BaseTaskState(IntEnum):
    NONE = 0
    READY = 1
    WORKING = 2
    WORKING_ADDITIONALLY = 3
    FINISHED = 4

class BaseTask(object, metaclass=abc.ABCMeta):
    
    def __init__(self, name:str, ID=None, default_work_amount=None, input_task_list=None, output_task_list=None, due_date=None, allocated_team_list=None, target_component_list=None, default_progress=None, additional_work_amount=None):    
        # Constraint variables on simulation
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.default_work_amount =  default_work_amount if default_work_amount is not None else 10.0
        self.input_task_list = input_task_list if input_task_list is not None else []
        self.output_task_list = output_task_list if output_task_list is not None else []
        self.due_date = due_date if due_date is not None else int(-1)
        self.allocated_team_list = allocated_team_list if allocated_team_list is not None else []
        self.target_component_list = target_component_list if target_component_list is not None else []
        self.default_progress = default_progress if default_progress is not None else 0.0
        self.additional_work_amount = additional_work_amount if additional_work_amount is not None else 0.0
        
        # Changeable variable on simulation
        self.est = 0.0 # Earliest start time
        self.eft = 0.0 # Earliest finish time
        self.lst = -1.0 # Latest start time
        self.lft = -1.0 # Latest finish time
        self.remaining_work_amount = self.default_work_amount * (1.0 - self.default_progress)
        self.actual_work_amount = self.default_work_amount * (1.0 - self.default_progress)
        self.state = BaseTaskState.NONE
        self.ready_time_list = []
        self.start_time_list = []
        self.finish_time_list = []
        self.additional_task_flag = False
        self.allocated_worker_list = []
    
    def __str__(self):
        return '{}'.format(self.name)

    def initialize(self, error_tol = 1e-10):
        self.est = 0.0 # Earliest start time
        self.eft = 0.0 # Earliest finish time
        self.lst = -1.0 # Latest start time
        self.lft = -1.0 # Latest finish time
        self.remaining_work_amount = self.default_work_amount * (1.0 - self.default_progress)
        self.actual_work_amount = self.default_work_amount * (1.0 - self.default_progress)
        self.state = BaseTaskState.NONE
        self.ready_time_list = []
        self.start_time_list = []
        self.finish_time_list = []
        self.additional_task_flag = False
        self.allocated_worker_list = []

        if not ( (0.00 - error_tol) < self.default_progress and self.default_progress < (0.00 + error_tol) ):
            self.state = BaseTaskState.READY
            self.ready_time_list.append(int(-1))
        elif self.default_progress >= (1.00 - error_tol):
            self.state = BaseTaskState.FINISHED
            self.ready_time_list.append(int(-1))
            self.start_time_list.append(int(-1))
            self.finish_time_list.append(int(-1))
        
        
    def perform(self, time:int):
        if self.state == BaseTaskState.WORKING:
            work_amount_progress = 0.0
            noErrorProbability = 1.0
            for worker in self.allocated_worker_list:
                work_amount_progress = work_amount_progress + worker.get_work_amount_skill_point(self.name)
                noErrorProbability = noErrorProbability - worker.get_quality_skill_point(self.name)
            
            self.remaining_work_amount = self.remaining_work_amount - work_amount_progress
            for component in self.target_component_list:
                component.update_error_value(noErrorProbability)
    
    def create_data_for_gantt_plotly(self, init_datetime, unit_timedelta, view_ready=False):
        df = []
        for ready_time,start_time,finish_time in zip(self.ready_time_list, self.start_time_list, self.finish_time_list):
            
            if view_ready:
                df.append(
                    dict(
                        Task=self.name,
                        Start=(init_datetime + ready_time * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                        Finish=(init_datetime + (start_time+0) * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                        State='READY',
                        Type='Task'
                        )
                )

            df.append(
                dict(
                    Task=self.name,
                    Start=(init_datetime + start_time * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                    Finish=(init_datetime + (finish_time+1) * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                    State='WORKING',
                    Type='Task'
                )
            )
        return df