#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_project import BaseProject
from .component import Component
from .product import Product
from .task import Task
from .base_task import BaseTaskState
from .base_resource import BaseResourceState
from .workflow import Workflow
from .worker import Worker
from .team import Team
from .organization import Organization

import json
import itertools

class Project(BaseProject):
    
    def __init__(self, file_path=''):
        super().__init__(file_path)
        if file_path != '':
            self.read_json(file_path)

    def initialize(self):
        self.time = 0
        self.product.initialize()
        self.organization.initialize()
        self.workflow.initialize()
    
    def read_json(self,file_path:str):
        pdes_json = open('sample.json', 'r')
        data = json.load(pdes_json)
        
        # Get Product information including Components without dependency
        cd_list = data['ProjectDiagram']['NodeElementList']['ComponentNode']
        component_list = [Component(cd['Name'], cd['-id'], float(cd['ErrorTolerance']))for cd in cd_list]
        
        # Get Workflow information including Tasks without dependency
        td_list = data['ProjectDiagram']['NodeElementList']['TaskNode']
        task_list = [Task(td['Name'], td['-id'], float(td['WorkAmount']), float(td['Progress']), float(td['AdditionalWorkAmount'])) for td in td_list]
        
        # Get Organization information including Teams without dependency
        team_list = []
        ted_list = data['ProjectDiagram']['NodeElementList']['TeamNode']
        for team_data in ted_list:
            worker_list = []
            worker_list_data = team_data['WorkerList']
            for worker_data in worker_list_data['Worker']:
                work_amount_skill_mean_info = {}
                work_amount_skill_sd_info = {}
                quality_skill_mean_info = {}
                # quality_skill_sd_info = {}
                if 'WorkAmountSkill' in worker_data:
                    if type(worker_data['WorkAmountSkill']) is list:
                        for skill_data in worker_data['WorkAmountSkill']:
                            work_amount_skill_mean_info[skill_data['-name']] = float(skill_data['-value'])
                            work_amount_skill_sd_info[skill_data['-name']] = float(skill_data['-value_sd'])
                    elif type(worker_data['WorkAmountSkill']) is dict:
                        work_amount_skill_mean_info[worker_data['WorkAmountSkill']['-name']] = float(worker_data['WorkAmountSkill']['-value'])
                        work_amount_skill_sd_info[worker_data['WorkAmountSkill']['-name']] = float(worker_data['WorkAmountSkill']['-value_sd'])
                if 'QualitySkill' in worker_data:
                    if type(worker_data['QualitySkill']) is list:
                        for skill_data in worker_data['QualitySkill']:
                            quality_skill_mean_info[skill_data['-name']] = float(skill_data['-value'])
                            # quality_skill_sd_info[skill_data['-name']] = float(skill_data['-value_sd'])
                    elif type(worker_data['QualitySkill']) is dict:
                        quality_skill_mean_info[worker_data['QualitySkill']['-name']] = float(worker_data['QualitySkill']['-value'])
                        # quality_skill_sd_info[worker_data['QualitySkill']['-name']] = float(worker_data['QualitySkill']['-value_sd'])
                worker_list.append(Worker(worker_data['Name'], team_data['-id'], float(worker_data['Cost']), work_amount_skill_mean_info, work_amount_skill_sd_info, quality_skill_mean_info))
            team_list.append(Team(team_data['Name'], team_data['-id'], worker_list)) 
        self.organization = Organization(team_list)
        
        # Get Links information including ComponentLink, TaskLink, TeamLink(not yet), TargetComponentLink, AllocationLink
        l_list = data['ProjectDiagram']['LinkList']['Link']
        for link in l_list:
            if link['-type'] == 'ComponentLink':
                org_c = list(filter(lambda c: c.ID == link['-org'], component_list))[0]
                dst_c = list(filter(lambda c: c.ID == link['-dst'], component_list))[0]
                org_c.depended_component_list.append(dst_c)
                dst_c.depending_component_list.append(org_c)
            elif link['-type'] == 'TaskLink':
                org_task = list(filter(lambda c: c.ID == link['-org'], task_list))[0]
                dst_task = list(filter(lambda c: c.ID == link['-dst'], task_list))[0]
                org_task.output_task_list.append(dst_task)
                dst_task.input_task_list.append(org_task)
            elif link['-type'] == 'TeamLink':
                org_team = list(filter(lambda c: c.ID == link['-org'], team_list))[0]
                dst_team = list(filter(lambda c: c.ID == link['-dst'], team_list))[0]
                # org_task.output_task_id_list.append(dst_task.ID)
                dst_team.superior_team_id = org_team.ID
            elif link['-type'] == 'TargetComponentLink':
                org_c = list(filter(lambda c: c.ID == link['-org'], component_list))[0]
                dst_task = list(filter(lambda c: c.ID == link['-dst'], task_list))[0]
                org_c.targeted_task_list.append(dst_task)
                dst_task.target_component_list.append(org_c)
            elif link['-type'] == 'AllocationLink':
                org_team = list(filter(lambda c: c.ID == link['-org'], team_list))[0]
                dst_task = list(filter(lambda c: c.ID == link['-dst'], task_list))[0]
                org_team.targeted_task_list.append(dst_task)
                dst_task.allocated_team_list.append(org_team)
            

        # Aggregate
        self.product = Product(component_list)
        self.workflow = Workflow(task_list)
        self.organization = Organization(team_list)
    
    def simulate(self, error_tol = 1e-10, print_debug=False):
        
        self.initialize()

        while True:
            if print_debug: print(self)
            
            # 1. Check finished or not
            state_list = list(map(lambda task:task.state, self.workflow.task_list))
            if all(state == BaseTaskState.FINISHED for state in state_list):
                return
            
            # 2. Get ready task and free resources
            ready_and_working_task_list = list(filter(lambda task:task.state == BaseTaskState.READY or task.state == BaseTaskState.WORKING, self.workflow.task_list))
            worker_list = list(itertools.chain.from_iterable(list(map(lambda team:team.worker_list, self.organization.team_list))))
            free_worker_list = list(filter(lambda worker:worker.state == BaseResourceState.FREE, worker_list))

            # 3. Sort ready task and free resources
            ready_and_working_task_list = sorted(ready_and_working_task_list, key=lambda task: task.lst - task.est) # Task: TSLACK (a task which Slack time(LS-ES) is lower has high priority)
            free_worker_list = sorted(free_worker_list, key=lambda worker: sum(worker.workamount_skill_mean_map.values())) # Worker: SSP (a resource which amount of skill point is lower has high priority)
            
            # 4. Allocate ready tasks to free resources
            for task in ready_and_working_task_list:
                allocating_workers = list(filter(lambda worker: worker.has_skill(task.name) and self.__is_allocated(worker, task), free_worker_list))
                task.allocated_worker_list.extend([worker for worker in allocating_workers])
                for w in allocating_workers:
                    free_worker_list.remove(w)
            
            # 5. Perform and Update workflow and organization
            self.workflow.check_state(self.time, BaseTaskState.WORKING)
            self.organization.add_labor_cost(only_working=True)
            self.workflow.perform(self.time)
            self.workflow.check_state(self.time, BaseTaskState.FINISHED)
            self.workflow.check_state(self.time, BaseTaskState.READY)
            self.workflow.update_PERT_data(self.time)

            self.time = self.time + 1


    def __is_allocated(self, worker, task):
        team = list(filter(lambda team: team.ID == worker.team_id, self.organization.team_list))[0]
        return task in team.targeted_task_list