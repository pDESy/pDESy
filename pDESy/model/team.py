#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_team import BaseTeam


class Team(BaseTeam):
    """Team
    Team class for expressing team in a project.
    This class is implemented from BaseTeam.

    Args:
        name (str):
            Basic parameter.
            Name of this team.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        worker_list (List[BaseWorker], optional):
            Basic parameter.
            List of BaseWorker who belong to this team.
            Defaults to None -> [].
        targeted_task_list (List[BaseTask], optional):
            Basic parameter.
            List of targeted BaseTasks.
            Defaults to None -> [].
        parent_team (BaseTeam, optional):
            Basic parameter.
            Parent team of this team.
            Defaults to None.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this team's cost in simulation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        worker_list=None,
        targeted_task_list=None,
        parent_team=None,
        # Basic variables
        cost_list=None,
    ):
        super().__init__(
            name,
            ID=ID,
            worker_list=worker_list,
            targeted_task_list=targeted_task_list,
            parent_team=parent_team,
            cost_list=cost_list,
        )
