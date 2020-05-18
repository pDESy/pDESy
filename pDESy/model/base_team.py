#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from typing import List
from .base_resource import BaseResource, BaseResourceState
import plotly.graph_objects as go

class BaseTeam(object, metaclass=abc.ABCMeta):
    
    def __init__(self, name:str, ID=None, worker_list=None, targeted_task_list=None, superior_team=None):
        
        # Constraint variables on simulation
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.worker_list = worker_list if worker_list is not None else []
        self.targeted_task_list = targeted_task_list if targeted_task_list is not None else []
        self.superior_team = superior_team if superior_team is not None else ''

        # Changeable variables on simulation
        self.cost_list = []
    
    def set_superior_team(self, superior_team):
        self.superior_team = superior_team
    
    def extend_targeted_task_list(self, targeted_task_list):
        self.targeted_task_list.extend(targeted_task_list)
        for child_t in targeted_task_list:
            child_t.allocated_team_list.append(self)
    
    def append_targeted_task(self, targeted_task):
        self.targeted_task_list.append(targeted_task)
        targeted_task.allocated_team_list.append(self)

    def initialize(self):
        self.cost_list = []
        for w in self.worker_list:
            w.initialize()
        
    def add_labor_cost(self, only_working=True):
        cost_this_time = 0.0

        if only_working :
            for worker in self.worker_list:
                if worker.state == BaseResourceState.WORKING:
                    worker.cost_list.append(worker.cost_per_time)
                    cost_this_time += worker.cost_per_time
                else:
                    worker.cost_list.append(0.0)
        
        else:
            for worker in self.worker_list:
                worker.cost_list.append(worker.cost_per_time)
                cost_this_time += worker.cost_per_time


        self.cost_list.append(cost_this_time)
        return cost_this_time
    
    def __str__(self):
        return '{}'.format(self.name)
    
    def create_data_for_gantt_plotly(self, init_datetime, unit_timedelta):
        df = []
        for worker in self.worker_list:
            for start_time,finish_time in zip(worker.start_time_list, worker.finish_time_list):
                df.append(
                    dict(
                        Task=self.name + ': ' + worker.name,
                        Start=(init_datetime + start_time * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                        Finish=(init_datetime + (finish_time) * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S'),
                        Type='Worker'
                        )
                    )
        return df
    
    def create_data_for_cost_history_plotly(self, init_datetime, unit_timedelta):
        data = []
        x = [(init_datetime + time * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S') for time in range(len(self.cost_list))]
        for worker in self.worker_list:
            data.append(go.Bar(name=worker.name, x=x, y=worker.cost_list))
        return data
    
    def create_cost_history_plotly(self, init_datetime, unit_timedelta, title='Cost Chart'):
        x = [(init_datetime + time * unit_timedelta).strftime('%Y-%m-%d %H:%M:%S') for time in range(len(self.cost_list))]
        data = self.create_data_for_cost_history_plotly(init_datetime, unit_timedelta)
        fig = go.Figure(data)
        fig.update_layout(barmode='stack', title=title)
        return fig