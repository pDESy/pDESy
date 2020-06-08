#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_resource import BaseResource, BaseResourceState


class Worker(BaseResource):
    def __init__(
        self,
        # Basic parameters
        name: str,
        team_id=None,
        cost_per_time=0.0,
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        # Advanced parameters for customized simulation
        quality_skill_mean_map={},
        quality_skill_sd_map={},
        # Basic variables
        state=BaseResourceState.FREE,
        cost_list=None,
        start_time_list=None,
        finish_time_list=None,
        assigned_task_list=None,
        # Advanced parameters for customized simulation
    ):
        super().__init__(
            name,
            team_id=team_id,
            cost_per_time=cost_per_time,
            workamount_skill_mean_map=workamount_skill_mean_map,
            workamount_skill_sd_map=workamount_skill_sd_map,
            quality_skill_mean_map=quality_skill_mean_map,
            quality_skill_sd_map=quality_skill_sd_map,
            state=state,
            cost_list=cost_list,
            start_time_list=start_time_list,
            finish_time_list=finish_time_list,
            assigned_task_list=assigned_task_list,
        )
