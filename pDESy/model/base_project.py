#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .base_product import BaseProduct
from .base_workflow import BaseWorkflow
from .base_organization import BaseOrganization

class BaseProject(object, metaclass=ABCMeta):
    
    def __init__(self, file_path=''):
        # Constraint variables on simulation
        self.product = []
        self.organization = []
        self.workflow = []

        self.time = 0
    
    def __str__(self):
        return 'TIME: {}\nPRODUCT\n{}\n\nORGANIZATION\n{}\n\nWORKFLOW\n{}'.format(self.time, str(self.product), str(self.organization), str(self.workflow))
        
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def read_json(self,file_path:str):
        pass

    @abstractmethod
    def simulate(self,file_path:str):
        pass
