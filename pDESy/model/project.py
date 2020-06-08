#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_project import BaseProject


class Project(BaseProject):
    def __init__(
        self,
        file_path=None,
        # Basic parameters
        init_datetime=None,
        unit_timedelta=None,
        # Basic variables
        product=None,
        organization=None,
        workflow=None,
        time=0,
        cost_list=None,
        # For this class
        encoding=None,
    ):
        super().__init__(
            file_path=file_path,
            init_datetime=init_datetime,
            unit_timedelta=unit_timedelta,
            product=product,
            organization=organization,
            workflow=workflow,
            time=time,
            cost_list=cost_list,
        )
        if file_path is not None:
            self.read_pDES_json(file_path, encoding=encoding)

    def initialize(self):
        super().initialize()

    def simulate(
        self,
        worker_perfoming_mode="single-task",
        task_performed_mode="multi-workers",
        error_tol=1e-10,
        print_debug=False,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
        max_time=10000,
    ):
        super().simulate(
            worker_perfoming_mode=worker_perfoming_mode,
            task_performed_mode=task_performed_mode,
            error_tol=error_tol,
            print_debug=print_debug,
            weekend_working=weekend_working,
            work_start_hour=work_start_hour,
            work_finish_hour=work_finish_hour,
            max_time=max_time,
        )
