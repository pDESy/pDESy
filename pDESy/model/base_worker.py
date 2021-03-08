#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_resource import BaseResource
from enum import IntEnum


class BaseWorkerState(IntEnum):
    """BaseWorkerState"""

    FREE = 0
    WORKING = 1


class BaseWorker(BaseResource):
    """BaseWorker
    BaseWorker class for expressing a worker.
    This class will be used as template.
    This class is implemented from BaseResource.

    Args:
        name (str):
            Basic parameter.
            Name of this worker.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        workplace_id (str, optional):
            Basic parameter.
            Workplace ID will be defined automatically on adding workplace.
            Defaults to None.
        cost_per_time (float, optional):
            Basic parameter.
            Cost of this worker per unit time.
            Defaults to 0.0.
        solo_working (bool, optional):
            Basic parameter.
            Flag whether this worker can work with other workers or not.
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
        state (BaseWorkerState, optional):
            Basic variable.
            State of this worker in simulation.
            Defaults to BaseWorkerState.FREE.
        state_record_list (List[BaseWorkerState], optional):
            Basic variable.
            Record list of state.
            Defaults to None -> [].
        cost_list (List[float], optional):
            Basic variable.
            History or record of his or her cost in simulation.
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
        state=BaseWorkerState.FREE,
        state_record_list=None,
        cost_list=None,
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
            state_record_list=state_record_list,
            cost_list=cost_list,
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

    def export_dict_json_data(self):
        """
        Export the information of this worker to JSON data.

        Returns:
            dict: JSON format data.
        """
        dict_json_data = {}
        dict_json_data.update(
            type="BaseWorker",
            name=self.name,
            ID=self.ID,
            team_id=self.team_id if self.team_id is not None else None,
            cost_per_time=self.cost_per_time,
            solo_working=self.solo_working,
            workamount_skill_mean_map=self.workamount_skill_mean_map,
            workamount_skill_sd_map=self.workamount_skill_sd_map,
            facility_skill_map=self.facility_skill_map,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            cost_list=self.cost_list,
            assigned_task_list=[t.ID for t in self.assigned_task_list],
            assigned_task_id_record=self.assigned_task_id_record,
        )
        return dict_json_data
