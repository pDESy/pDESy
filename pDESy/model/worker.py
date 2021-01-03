#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_worker import BaseWorker, BaseWorkerState
import numpy as np


class Worker(BaseWorker):
    """Worker
    Worker class for expressing a team.
    This class is implemented from BaseWorker.

    Args:
        name (str):
            Basic parameter. Name of this worker.
        ID (str, optional):
            Basic parameter.
            ID will be defined automatically.
            Defaults to None.
        team_id (str, optional):
            Basic parameter.
            Team ID will be defined automatically on adding team.
            Defaults to None.
        cost_per_time (float, optional):
            Basic parameter.
            Cost of this worker per unit time.
            Defaults to 0.0.
        workamount_skill_mean_map (Dict[str, float], optional):
            Basic parameter.
            Skill for expressing progress in unit time.
            Defaults to {}.
        workamount_skill_sd_map (Dict[str, float], optional):
            Basic parameter.
            Standard deviation of skill for expressing progress in unit time.
            Defaults to {}.
        quality_skill_mean_map (Dict[str, float], optional):
            Advanced parameter.
            Skill for expressing quality in unit time.
            Defaults to {}.
        quality_skill_sd_map (Dict[str, float], optional):
            Advanced parameter.
            Standard deviation of skill for expressing quality in unit time.
            Defaults to {}.
        state (BaseWorkerState, optional):
            Basic variable.
            State of this worker in simulation.
            Defaults to BaseWorkerState.FREE.
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
        workamount_skill_mean_map={},
        workamount_skill_sd_map={},
        facility_skill_map={},
        # Basic variables
        state=BaseWorkerState.FREE,
        cost_list=None,
        assigned_task_list=None,
        assigned_task_id_record=None,
        # Advanced parameters for customized simulation
        quality_skill_mean_map={},
        quality_skill_sd_map={},
    ):
        super().__init__(
            name,
            ID=ID,
            team_id=team_id,
            cost_per_time=cost_per_time,
            workamount_skill_mean_map=workamount_skill_mean_map,
            workamount_skill_sd_map=workamount_skill_sd_map,
            facility_skill_map=facility_skill_map,
            state=state,
            cost_list=cost_list,
            assigned_task_list=assigned_task_list,
            assigned_task_id_record=assigned_task_id_record,
        )
        # --
        # Advanced parameter for customized simulation
        self.quality_skill_mean_map = (
            quality_skill_mean_map if quality_skill_mean_map is not None else {}
        )
        self.quality_skill_sd_map = (
            quality_skill_sd_map if quality_skill_sd_map is not None else {}
        )

    def has_quality_skill(self, task_name, error_tol=1e-10):
        """
        Check whether he or she has quality skill or not
        by checking quality_skill_mean_map.

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
