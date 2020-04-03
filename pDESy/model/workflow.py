#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_task import BaseTask
from .base_workflow import BaseWorkflow
from typing import List

class Workflow(BaseWorkflow):
    
    def __init__(self, task_list:List[BaseTask]):
        super().__init__(task_list)