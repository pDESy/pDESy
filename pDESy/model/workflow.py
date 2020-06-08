#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_task import BaseTask
from .base_workflow import BaseWorkflow
from typing import List


class Workflow(BaseWorkflow):
    """Workflow
    Workflow class for expressing workflow in a project.
    This class is implemented from BaseWorkflow.

    Args:
        task_list (List[BaseTask]):
            Basic parameter.
            List of BaseTask in this BaseWorkflow.
        critical_path_length (float, optional):
            Basic variable.
            Critical path length of PERT/CPM.
            Defaults to 0.0.
    """

    def __init__(self, task_list: List[BaseTask]):
        super().__init__(task_list)
