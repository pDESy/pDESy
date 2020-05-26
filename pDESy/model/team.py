#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_team import BaseTeam


class Team(BaseTeam):
    def __init__(
        self,
        name,
        ID=None,
        worker_list=None,
        targeted_task_list=None,
        superior_team=None,
    ):
        super().__init__(
            name,
            ID=ID,
            worker_list=worker_list,
            targeted_task_list=targeted_task_list,
            superior_team=superior_team,
        )
