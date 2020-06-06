#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_component import BaseComponent


class Component(BaseComponent):
    def __init__(
        self,
        name: str,
        ID=None,
        error_tolerance=None,
        child_component_list=None,
        parent_component_list=None,
        targeted_task_list=None,
    ):
        super().__init__(
            name,
            ID=ID,
            error_tolerance=error_tolerance,
            child_component_list=child_component_list,
            parent_component_list=parent_component_list,
            targeted_task_list=targeted_task_list,
        )
