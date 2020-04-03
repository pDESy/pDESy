#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_team import BaseTeam

class BaseOrganization(object, metaclass=abc.ABCMeta):
    
    def __init__(self, team_list:List[BaseTeam]):
        # Constraint variables on simulation
        self.team_list = team_list
    
    def __str__(self):
        return '{}'.format(list(map(lambda team: str(team), self.team_list)))
        
    def initialize(self):
        for team in self.team_list:
            team.initialize()
    
    def add_labor_cost(self,only_working=True):
        for team in self.team_list:
            team.add_labor_cost(only_working=True)
        