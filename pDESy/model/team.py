#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_team import BaseTeam


class Team(BaseTeam):
    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        worker_list=None,
        targeted_task_list=None,
        parent_team=None,
        # Advanced parameters for customized simulation
        # Basic variables
        cost_list=None,
        # Advanced parameters for customized simulation
    ):
        super().__init__(
            name,
            ID=ID,
            worker_list=worker_list,
            targeted_task_list=targeted_task_list,
            parent_team=parent_team,
            cost_list=cost_list,
        )
