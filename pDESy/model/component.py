#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_component import BaseComponent


class Component(BaseComponent):
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
            error_tolerance=error_tolerance,
            child_component_list=child_component_list,
            parent_component_list=parent_component_list,
            targeted_task_list=targeted_task_list,
            error=error,
        )
