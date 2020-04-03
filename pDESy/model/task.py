#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_task import BaseTask

class Task(BaseTask):
    
    def __init__(self, name:str, ID=None, default_work_amount=None, input_task_list=None, output_task_list=None, due_date=None, allocated_team_list=None, target_component_list=None, default_progress=None, additional_work_amount=None):
        super().__init__(name, ID=ID, default_work_amount=default_work_amount, default_progress=default_progress, additional_work_amount=additional_work_amount)