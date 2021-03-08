#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_organization import BaseOrganization
from .base_team import BaseTeam
from typing import List


class Organization(BaseOrganization):
    """Organization
    Organization class for expressing organization in target project.
    This class is implemented from BaseOrganization.

    Args:
        team_list (List[BaseTeam]):
            Basic parameter.
            List of BaseTeam in this organization.
        workplace_list (List[BaseWorkplace]):
            Basic parameter.
            List of BaseWorkplace in this organization.
            Defaults to None -> []
        cost_list (List[float], optional):
            Basic variable.
            History or record of this organization's cost in simulation.
            Defaults to None -> [].
    """

    def __init__(self, team_list: List[BaseTeam], workplace_list=None, cost_list=None):
        super().__init__(team_list, workplace_list=workplace_list, cost_list=cost_list)
