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
        factory_list (List[BaseFactory]):
            Basic parameter.
            List of BaseFactory in this organization.
            Defaults to None -> []
        cost_list (List[float], optional):
            Basic variable.
            History or record of this organization's cost in simulation.
            Defaults to None -> [].
    """

    def __init__(self, team_list: List[BaseTeam], factory_list=None, cost_list=None):
        super().__init__(team_list, factory_list=factory_list, cost_list=cost_list)
