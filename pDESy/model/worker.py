#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_resource import BaseResource


class Worker(BaseResource):
    def __init__(
        self,
        name: str,
        team_id: str,
        cost_per_time=None,
        workamount_skill_mean_map=None,
        workamount_skill_sd_map=None,
        quality_skill_mean_map=None,
    ):
        super().__init__(
            name,
            team_id,
            cost_per_time=cost_per_time,
            workamount_skill_mean_map=workamount_skill_mean_map,
            workamount_skill_sd_map=workamount_skill_sd_map,
            quality_skill_mean_map=quality_skill_mean_map,
        )
