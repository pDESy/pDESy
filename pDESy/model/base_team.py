#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from typing import List
from .base_resource import BaseResource, BaseResourceState

class BaseTeam(object, metaclass=abc.ABCMeta):
    
    def __init__(self, name:str, ID=None, worker_list=None, targeted_task_list=None, superior_team=None):
        
        # Constraint variables on simulation
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.worker_list = worker_list if worker_list is not None else []
        self.targeted_task_list = targeted_task_list if targeted_task_list is not None else []
        self.superior_team = superior_team if superior_team is not None else ''
        
    def initialize(self):
        for w in self.worker_list:
            w.initialize()
        
    def add_labor_cost(self, only_working=True):
        target_worker_list = self.worker_list
        if only_working:
            target_worker_list = list(filter(lambda worker: worker.state == BaseResourceState.WORKING, self.worker_list))
        for worker in target_worker_list:
            worker.total_cost = worker.total_cost + worker.cost_per_time
    
    def __str__(self):
        return '{}, {}, {}'.format(self.ID, self.name, list(map(lambda worker: str(worker), self.worker_list)))
    
    def create_data_for_gantt_plotly(self, init_datetime, unit_timedelta):
        df = []
        for worker in self.worker_list:
            for start_time,finish_time in zip(worker.start_time_list, worker.finish_time_list):
                df.append(
                    dict(
                        Task=self.name + ': ' + worker.name,
                        Start=(init_datetime + start_time * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                        Finish=(init_datetime + (finish_time+1) * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                        Type='Worker'
                        )
                    )
        return df