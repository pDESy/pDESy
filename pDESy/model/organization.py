#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_organization import BaseOrganization
from .base_team import BaseTeam
from typing import List


class Organization(BaseOrganization):
    def __init__(self, team_list: List[BaseTeam]):
        super().__init__(team_list)
