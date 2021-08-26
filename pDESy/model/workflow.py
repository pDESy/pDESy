#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""workflow."""

from typing import List

from .base_task import BaseTask
from .base_workflow import BaseWorkflow


class Workflow(BaseWorkflow):
    """Workflow.

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
        """init."""
        super().__init__(task_list)

    def perform(self, time: int, seed=None, increase_component_error=1.0):
        """
        Perform Task in task_list in simulation.

        @override BaseWorkflow.perform()

        Args:
            time (int):
                Simulation time.
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
        for task in self.task_list:
            task.perform(
                time, seed=seed, increase_component_error=increase_component_error
            )
