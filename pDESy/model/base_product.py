#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_component import BaseComponent

class BaseProduct(object, metaclass=abc.ABCMeta):
    
    def __init__(self, component_list:List[BaseComponent]):
        # Constraint variables on simulation
        self.component_list = component_list
        
    def initialize(self):
        for c in self.component_list:
            c.initialize()
    
    def __str__(self):
        return '{}'.format(list(map(lambda c: str(c), self.component_list)))