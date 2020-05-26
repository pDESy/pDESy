#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_component import BaseComponent


class Component(BaseComponent):
    def __init__(
        self,
        name: str,
        ID=None,
        error_tolerance=None,
        depending_component_list=None,
        depended_component_list=None,
        targeted_task_list=None,
    ):
        super().__init__(
            name,
            ID=ID,
            error_tolerance=error_tolerance,
            depending_component_list=depending_component_list,
            depended_component_list=depended_component_list,
            targeted_task_list=targeted_task_list,
        )
