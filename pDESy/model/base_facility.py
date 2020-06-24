#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_resource import BaseResource, BaseResourceState


class BaseFacility(BaseResource):
    """BaseFacility
    BaseResource class for expressing a factory.
    This class will be used as template.
    This class is implemented from BaseResource.
    In pDESy, resource and facility have the same attributes.

    Args:
        name (str):
            Basic parameter. Name of this resource.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        factory_id (str, optional):
            Basic parameter.
            Factory ID will be defined automatically on adding factory.
            Defaults to None.
        cost_per_time (float, optional):
            Basic parameter.
            Cost of this resource per unit time.
            Defaults to 0.0.
        workamount_skill_mean_map (Dict[str, float], optional):
            Basic parameter.
            Skill for expressing progress in unit time.
            Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional):
            Basic parameter.
            Standard deviation of skill for expressing progress in unit time.
            Defaults to {}.
        state (BaseResourceState, optional):
            Basic variable.
            State of this resource in simulation.
            Defaults to BaseResourceState.FREE.
        cost_list (List[float], optional):
            Basic variable.
            History or record of his or her cost in simumation.
            Defaults to None -> [].
        start_time_list (List[int], optional):
            Basic variable.
            History or record of his or her start time in simumation.
            Defaults to None -> [].
        finish_time_list (List[int], optional):
            Basic variable.
            History or record of his or her finish time in simumation.
            Defaults to None -> [].
        assigned_task_list (List[BaseTask], optional):
            Basic variable.
            State of his or her assigned tasks in simumation.
            Defaults to None -> [].
        assigned_task_id_record (List[List[str]], optional):
            Basic variable.
            Record of his or her assigned tasks' id in simumation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        factory_id=None,
        cost_per_time=0.0,
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        # Basic variables
        state=BaseResourceState.FREE,
        cost_list=None,
        start_time_list=None,
        finish_time_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
    ):
        super().__init__(
            name,
            ID=ID,
            team_id=factory_id,
            cost_per_time=cost_per_time,
            workamount_skill_mean_map=workamount_skill_mean_map,
            workamount_skill_sd_map=workamount_skill_sd_map,
            state=state,
            cost_list=cost_list,
            start_time_list=start_time_list,
            finish_time_list=finish_time_list,
            assigned_task_list=assigned_task_list,
            assigned_task_id_record=assigned_task_id_record,
        )
