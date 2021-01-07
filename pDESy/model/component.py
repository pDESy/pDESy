#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_component import BaseComponent
import numpy as np


class Component(BaseComponent):
    """Component
    Component class for expressing target product.
    This class is implemented from BaseComponent.

    Args:
        name (str):
            Basic parameter.
            Name of this component.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        parent_component_list(List[BaseComponent], optional):
            Basic parameter.
            List of parent BaseComponents. Defaults to None.
        child_component_list (List[BaseComponent], optional):
            Basic parameter.
            List of child BaseComponents.
            Defaults to None.
        targeted_task_list (List[BaseTask], optional):
            Basic parameter.
            List of targeted tasks.
            Defaults to None.
        error_tolerance (float, optional):
            Advanced parameter.
        error (float, optional):
            Advanced variables.
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        parent_component_list=None,
        child_component_list=None,
        targeted_task_list=None,
        # Advanced parameters for customized simulation
        error_tolerance=None,
        # Advanced variables for customized simulation
        error=None,
    ):
        super().__init__(
            name,
            ID=ID,
            child_component_list=child_component_list,
            parent_component_list=parent_component_list,
            targeted_task_list=targeted_task_list,
        )
        # --
        # Advanced parameter for customized simulation
        if error_tolerance is not None:
            self.error_tolerance = error_tolerance
        else:
            self.error_tolerance = 0.0
        # Advanced variables for customized simulation
        if error is not None:
            self.error = error
        else:
            self.error = 0.0

    def initialize(self, state_info=True, log_info=True):
        """
        Initialize the following changeable variables of Component

        If `state_info` is True, the following attributes are initialized
        in addition to 'BaseComponent.initialize()'.

          - error

        Args:
            state_info (bool):
                State information are initialized or not.
                Defaluts to True.
            log_info (bool):
                Log information are initialized or not.
                Defaults to True.
        """
        super().initialize(state_info=True, log_info=True)
        if state_info:
            self.error = 0.0

    def update_error_value(
        self, no_error_prob: float, error_increment: float, seed=None
    ):
        """
        Update error value randomly
        (If no_error_prob >=1.0, error = error + error_increment)

        Args:
            no_error_prob (float): Probability of no error (0.0~1.0)
            error_increment (float): Increment of error variables if error has occurred.
            seed (int, optional): seed of creating random.rand(). Defaults to None.
        Examples:
            >>> c = Component("c")
            >>> c.update_error_value(0.9, 1.0, seed=32)
            >>> print(c.error)
            0.0
            >>> c.update_error_value(0.4, 1.0, seed=32)
            >>> print(c.error) # Random 1.0 or 0.0
            1.0
        Note:
            This method is developed for customized simulation.
        """
        if seed is not None:
            np.random.seed(seed=seed)
        if np.random.rand() > no_error_prob:
            self.error = self.error + error_increment
