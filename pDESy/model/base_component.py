#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import uuid
from numpy.random import rand

class BaseComponent(object, metaclass=abc.ABCMeta):
    
    def __init__(self, name:str, ID=None, error_tolerance=None, depending_component_list=None, depended_component_list=None, targeted_task_list=None):
        
        # Constraint variables on simulation
        self.name = name
        self.ID = ID if ID is not None else str(uuid.uuid4())
        self.error_tolerance = error_tolerance if error_tolerance is not None else 0.0
        self.depending_component_list = depending_component_list if depending_component_list is not None else []
        self.depended_component_list = depended_component_list if depended_component_list is not None else []
        self.targeted_task_list = targeted_task_list if targeted_task_list is not None else []
        
        # Changeable variable on simulation
        self.error = int(0)
        
        # Changeable variable on simulation
        self.error = int(0)
        
    def initialize(self):
        self.error = int(0)
    
    def update_error_value(self, no_error_probability:float):
        if rand() >= no_error_probability:
            self.error = self.error + 1
    
    def __str__(self):
        return '{}, {}, {}'.format(self.ID, self.name, self.error_tolerance)
