#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""base_worker."""

from enum import IntEnum
import numpy as np

from .base_resource import BaseResource


class BaseWorkerState(IntEnum):
    """BaseWorkerState."""

    FREE = 0
    WORKING = 1
    ABSENCE = -1


class BaseWorker(BaseResource):
    """BaseWorker.

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
        team_id (str, optional):
            Basic parameter.
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
        absence_time_list (List[int], optional):
            List of absence time of simulation.
            Defaults to None -> [].
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
        quality_skill_mean_map (Dict[str, float], optional):
            Advanced parameter.
            Skill for expressing quality in unit time.
            Defaults to {}.
        quality_skill_sd_map (Dict[str, float], optional):
            Advanced parameter.
            Standard deviation of skill for expressing quality in unit time.
            Defaults to {}.
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
        absence_time_list=None,
        # Basic variables
        state=BaseWorkerState.FREE,
        state_record_list=None,
        cost_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
        # Advanced parameters for customized simulation
        quality_skill_mean_map={},
        quality_skill_sd_map={},
    ):
        """init."""
        super().__init__(
            name,
            ID=ID,
            team_id=team_id,
            cost_per_time=cost_per_time,
            solo_working=solo_working,
            workamount_skill_mean_map=workamount_skill_mean_map,
            workamount_skill_sd_map=workamount_skill_sd_map,
            absence_time_list=absence_time_list,
            state=state,
            state_record_list=state_record_list,
            cost_list=cost_list,
            assigned_task_list=assigned_task_list,
            assigned_task_id_record=assigned_task_id_record,
        )

        self.facility_skill_map = (
            facility_skill_map if facility_skill_map is not None else {}
        )

        # --
        # Advanced parameter for customized simulation
        self.quality_skill_mean_map = (
            quality_skill_mean_map if quality_skill_mean_map is not None else {}
        )
        self.quality_skill_sd_map = (
            quality_skill_sd_map if quality_skill_sd_map is not None else {}
        )

    def has_facility_skill(self, facility_name, error_tol=1e-10):
        """
        Check whether he or she has facility skill or not.

        By checking facility_skill_map.

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

    def has_quality_skill(self, task_name, error_tol=1e-10):
        """
        Check whether he or she has quality skill or not.

        By checking quality_skill_mean_map.

        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.

        Returns:
            bool: whether he or she has quality skill of task_name or not
        """
        if task_name in self.quality_skill_mean_map:
            if self.quality_skill_mean_map[task_name] > 0.0 + error_tol:
                return True
        return False

    def get_quality_skill_point(self, task_name, seed=None):
        """
        Get point of quality by his or her contribution in this time.

        Args:
            task_name (str):
                Task name
            error_tol (float, optional):
                Countermeasures against numerical error.
                Defaults to 1e-10.

        Returns:
            float: Point of quality by his or her contribution in this time
        """
        if seed is not None:
            np.random.seed(seed=seed)
        if not self.has_quality_skill(task_name):
            return 0.0
        skill_mean = self.quality_skill_mean_map[task_name]

        if task_name not in self.quality_skill_sd_map:
            skill_sd = 0
        else:
            skill_sd = self.quality_skill_sd_map[task_name]
        base_quality = np.random.normal(skill_mean, skill_sd)
        return base_quality  # / float(sum_of_working_task_in_this_time)

    def check_update_state_from_absence_time_list(self, step_time):
        """
        Check and Update state of all resources to ABSENCE or FREE or WORKING.

        Args:
            step_time (int):
                Target step time of checking and updating state of workers and facilities.
        """
        if step_time in self.absence_time_list:
            self.state = BaseWorkerState.ABSENCE
        else:
            if len(self.assigned_task_list) == 0:
                self.state = BaseWorkerState.FREE
            else:
                self.state = BaseWorkerState.WORKING

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
            absence_time_list=self.absence_time_list,
            state=int(self.state),
            state_record_list=[int(state) for state in self.state_record_list],
            cost_list=self.cost_list,
            assigned_task_list=[t.ID for t in self.assigned_task_list],
            assigned_task_id_record=self.assigned_task_id_record,
        )
        return dict_json_data
