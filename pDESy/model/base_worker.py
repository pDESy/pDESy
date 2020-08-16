#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_resource import BaseResource, BaseResourceState


class BaseWorker(BaseResource):
    """BaseWorker
    BaseResource class for expressing a worker.
    This class will be used as template.
    This class is implemented from BaseResource.

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
        solo_working (bool, optional):
            Basic parameter.
            Flag whether this resource can work with other resources or not.
            Defaults to False.
        workamount_skill_mean_map (Dict[str, float], optional):
            Basic parameter.
            Skill for expressing progress in unit time.
            Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional):
            Basic parameter.
            Standard deviation of skill for expressing progress in unit time.
            Defaults to {}.
        facility_skill_map (Dict[str, float], optional):
            Basic parameter.
            Skill for operating facility in unit time.
            Defaults to {}.
        state (BaseResourceState, optional):
            Basic variable.
            State of this resource in simulation.
            Defaults to BaseResourceState.FREE.
        cost_list (List[float], optional):
            Basic variable.
            History or record of his or her cost in simulation.
            Defaults to None -> [].
        start_time_list (List[int], optional):
            Basic variable.
            History or record of his or her start time in simulation.
            Defaults to None -> [].
        finish_time_list (List[int], optional):
            Basic variable.
            History or record of his or her finish time in simulation.
            Defaults to None -> [].
        assigned_task_list (List[BaseTask], optional):
            Basic variable.
            State of his or her assigned tasks in simulation.
            Defaults to None -> [].
        assigned_task_id_record (List[List[str]], optional):
            Basic variable.
            Record of his or her assigned tasks' id in simulation.
            Defaults to None -> [].
    """

    def __init__(
        self,
        # Basic parameters
        name: str,
        ID=None,
        team_id=None,
        cost_per_time=0.0,
        solo_working=False,
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        facility_skill_map={},
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
            team_id=team_id,
            cost_per_time=cost_per_time,
            solo_working=solo_working,
            workamount_skill_mean_map=workamount_skill_mean_map,
            workamount_skill_sd_map=workamount_skill_sd_map,
            state=state,
            cost_list=cost_list,
            start_time_list=start_time_list,
            finish_time_list=finish_time_list,
            assigned_task_list=assigned_task_list,
            assigned_task_id_record=assigned_task_id_record,
        )

        self.facility_skill_map = (
            facility_skill_map if facility_skill_map is not None else {}
        )

    def has_facility_skill(self, facility_name, error_tol=1e-10):
        """
        Check whether he or she has facility skill or not
        by checking facility_skill_map.

        Args:
            facility_name (str):
                Facility name
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.

        Returns:
            bool: whether he or she has workamount skill of task_name or not
        """
        if facility_name in self.facility_skill_map:
            if self.facility_skill_map[facility_name] > 0.0 + error_tol:
                return True
        return False
