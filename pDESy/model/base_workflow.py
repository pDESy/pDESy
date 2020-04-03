#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_task import BaseTask, BaseTaskState
from .base_resource import BaseResourceState


import itertools

class BaseWorkflow(object, metaclass=abc.ABCMeta):
    
    def __init__(self, task_list:List[BaseTask]):
        # Constraint variables on simulation
        self.task_list = task_list
        self.critical_path_length = 0.0
    
    def __str__(self):
        return '{}'.format(list(map(lambda task: str(task), self.task_list)))
        
    def initialize(self):
        for task in self.task_list:
            task.initialize()
        self.critical_path_length = 0.0
        self.update_PERT_data(0)
        self.check_state(0, BaseTaskState.READY)
    
    def update_PERT_data(self, time:int):
        self.__set_est_eft_data(time)
        self.__set_lst_lft_criticalpath_data(time)

    def check_state(self, time:int, state:BaseTaskState):
        if state == BaseTaskState.READY:
            self.__check_ready(time)
        elif state == BaseTaskState.WORKING:
            self.__check_working(time)
        elif state == BaseTaskState.FINISHED:
            self.__check_finished(time)

    def __check_ready(self, time:int):
        none_task_list = list(filter(lambda task: task.state==BaseTaskState.NONE, self.task_list))
        for none_task in none_task_list:
            input_task_list = none_task.input_task_list
            if all(list(map(lambda task: task.state == BaseTaskState.FINISHED, input_task_list))): # change READY when input tasks are finished all or this task is head task
                none_task.state = BaseTaskState.READY
                none_task.ready_time_list.append(time)
    
    def __check_working(self, time:int):
        ready_and_assigned_task_list = list(filter(lambda task: task.state==BaseTaskState.READY and len(task.allocated_worker_list) > 0, self.task_list))
        for task in ready_and_assigned_task_list:
            task.state = BaseTaskState.WORKING
            task.start_time_list.append(time)
            for worker in task.allocated_worker_list:
                worker.state = BaseResourceState.WORKING
                worker.start_time_list.append(time)
                worker.assigned_task_list.append(task)

    def __check_finished(self, time:int, error_tol = 1e-10):
        working_and_zero_task_list = list(filter(lambda task: task.state==BaseTaskState.WORKING and task.remaining_work_amount < 0.0 + error_tol, self.task_list))
        for task in working_and_zero_task_list:
            task.state = BaseTaskState.FINISHED
            task.finish_time_list.append(time)
            task.remaining_work_amount = 0.0
            for worker in task.allocated_worker_list:
                if all(list(map(lambda task: task.state == BaseTaskState.FINISHED, worker.assigned_task_list))):
                    worker.state = BaseResourceState.FREE
                    worker.finish_time_list.append(time)
    
    def __set_est_eft_data(self,time:int):
        
        input_task_list = []

        # 1. Set the earliest finish time of head tasks.
        for task in self.task_list:
            task.est = time
            if len(task.input_task_list) == 0:
                task.eft = time + task.remaining_work_amount
                input_task_list.append(task)
        

        # 2. Calculate PERT information of all tasks
        while len(input_task_list) > 0:
            next_task_list = []
            for input_task in input_task_list:
                for next_task in input_task.output_task_list:
                    pre_est = next_task.est
                    est = input_task.est + input_task.remaining_work_amount
                    eft = est + next_task.remaining_work_amount
                    if est >= pre_est:
                        next_task.est = est
                        next_task.eft = eft
                    next_task_list.append(next_task)
            
            input_task_list = next_task_list
    
    def __set_lst_lft_criticalpath_data(self, time:int):
        
        # 1. Extract the list of tail tasks.
        output_task_list = list(filter(lambda task: len(task.output_task_list)==0 ,self.task_list))
        

        # 2. Update the information of critical path of this workflow.
        self.critical_path_length = max(output_task_list, key=lambda task: task.eft).eft
        for task in output_task_list:
            task.lft = self.critical_path_length
            task.lst = task.lft - task.remaining_work_amount

        # 3. Calculate PERT information of all tasks
        while len(output_task_list) > 0:
            
            prev_task_list = []
            for output_task in output_task_list:
                for prev_task in output_task.input_task_list:
                    pre_lft = prev_task.lft
                    lft = output_task.lst
                    lst = lft - prev_task.remaining_work_amount
                    if pre_lft < 0 or pre_lft >= lft:
                        prev_task.lst = lst
                        prev_task.lft = lft
                    prev_task_list.append(prev_task)
            
            output_task_list = prev_task_list
    
    def perform(self, time:int):
        for task in self.task_list:
            task.perform(time)



