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
    
    def __init__(self, file_path='', init_datetime=None, unit_timedelta=None ,encoding=None):
        super().__init__(file_path, init_datetime=init_datetime, unit_timedelta=unit_timedelta)
        if file_path != '':
            self.read_json(file_path,encoding=encoding)

    def initialize(self):
        self.time = 0
        self.cost_list = []
        self.product.initialize()
        self.organization.initialize()
        self.workflow.initialize()

    def read_pdesy_web_json(self,file_path:str, encoding=None):
        encoding = encoding if encoding is not None else 'utf-8'
        pdes_json = open(file_path, 'r', encoding=encoding)
        data = json.load(pdes_json)

        # Get Product information including Components without dependency
        cd_list = list(filter(lambda node: node['type']=='Component', data))
        component_list = [Component(cd['name'], cd['id'], float(cd['userData']['errorTolerance']))for cd in cd_list]

        # Get Workflow information including Tasks without dependency
        td_list = list(filter(lambda node: node['type']=='Task', data))
        task_list = [Task(td['name'], td['id'], float(td['userData']['workAmount']), float(td['userData']['progress']), float(td['userData']['additionalWorkAmount'])) for td in td_list]
        
        # Get Organization information including Teams without dependency
        team_list = []
        ted_list = list(filter(lambda node: node['type']=='Team', data))
        for team_data in ted_list:
            worker_list = []
            worker_list_data = team_data['userData']['WorkerList']
            if type(worker_list_data['Worker']) is dict:
                worker_list_data['Worker'] = [worker_list_data['Worker']]
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
                worker_list.append(Worker(worker_data['Name'], team_data['id'], float(worker_data['Cost']), work_amount_skill_mean_info, work_amount_skill_sd_info, quality_skill_mean_info))
            team_list.append(Team(team_data['name'], team_data['id'], worker_list))
        
        # Get Links information including ComponentLink, TaskLink, TeamLink(not yet), TargetComponentLink, AllocationLink
        l_list = list(filter(lambda node: node['type']=='draw2d.Connection', data))
        for l in l_list:
            org_id = l['source']['node']
            org_type = list(filter(lambda node: node['id']==org_id, data))[0]['type']
            dst_id = l['target']['node']
            dst_type = list(filter(lambda node: node['id']==dst_id, data))[0]['type']
            if org_type == 'Component' and dst_type == 'Component':
                org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
                dst_c = list(filter(lambda c: c.ID == dst_id, component_list))[0]
                org_c.depended_component_list.append(dst_c)
                dst_c.depending_component_list.append(org_c)
            elif org_type == 'Task' and dst_type == 'Task':
                org_task = list(filter(lambda c: c.ID == org_id, task_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_task.output_task_list.append(dst_task)
                dst_task.input_task_list.append(org_task)
            elif org_type == 'Team' and dst_type == 'Team':
                org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
                dst_team = list(filter(lambda c: c.ID == dst_id, team_list))[0]
                # org_task.output_task_id_list.append(dst_task.ID)
                dst_team.superior_team_id = org_team.ID
            elif org_type == 'Component' and dst_type == 'Task':
                org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_c.targeted_task_list.append(dst_task)
                dst_task.target_component_list.append(org_c)
            elif org_type == 'Team' and dst_type == 'Task':
                org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_team.targeted_task_list.append(dst_task)
                dst_task.allocated_team_list.append(org_team)

        # Aggregate
        self.product = Product(component_list)
        self.workflow = Workflow(task_list)
        self.organization = Organization(team_list)

    def read_json(self,file_path:str, encoding=None):
        encoding = encoding if encoding is not None else 'utf-8'
        pdes_json = open(file_path, 'r', encoding=encoding)
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
            if type(worker_list_data['Worker']) is dict:
                worker_list_data['Worker'] = [worker_list_data['Worker']]
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
    
    def simulate(self, worker_perfoming_mode = 'single-task', task_performed_mode = 'multi-workers', error_tol = 1e-10, print_debug=False, weekend_working=True, max_time=10000):
        
        # ----------------------------------------------------------------------------
        # Simulation mode check
        ## Error check
        if not (worker_perfoming_mode == 'single-task' or worker_perfoming_mode == 'multi-task'):
            raise Exception('Please check ''worker_performing_mode'' which is equal to ''single-task'' or ''multi-task''')
            return
        
        if not (task_performed_mode == 'single-worker' or task_performed_mode == 'multi-workers'):
            raise Exception('Please check ''task_performed_mode'' which is equal to ''single-worker'' or ''multi-workers''')
            return

        ## set simulation mode
        mode = 0
        if worker_perfoming_mode == 'single-task' and task_performed_mode == 'single-worker':  mode = 1 # TaskPerformedBySingleTaskWorker in pDES
        if worker_perfoming_mode == 'single-task' and task_performed_mode == 'multi-workers':  mode = 2 # TaskPerformedBySingleTaskWorkers in pDES
        if worker_perfoming_mode == 'multi-task' and task_performed_mode == 'single-worker':  mode = 3
        if worker_perfoming_mode == 'multi-task' and task_performed_mode == 'multi-workers':  mode = 4

        ## check whether implementation or target mode simulation is finished or not
        if not(mode==1 or mode == 2):
            raise Exception('Sorry. This simulation mode is not yet implemented.')
            return
        # -----------------------------------------------------------------------------

        self.initialize()

        while True:
            
            # 1. Check finished or not
            state_list = list(map(lambda task:task.state, self.workflow.task_list))
            if all(state == BaseTaskState.FINISHED for state in state_list):
                return
            
            # Error check
            if self.time >= max_time:
                raise Exception('Time Over! Please check your simulation model or increase ''max_time'' value')
            
            # check now is business time or not
            working = True
            now_date_time = ''
            if not weekend_working:
                now_date_time = self.init_datetime + self.time * self.unit_timedelta
                working = self.is_business_time(now_date_time)
            
            if print_debug: print(self.time, now_date_time, working)
            
            if working:
                if mode==1: self.__perform_and_update_TaskPerformedBySingleTaskWorker(print_debug=print_debug)
                elif mode==2: self.__perform_and_update_TaskPerformedBySingleTaskWorkers(print_debug=print_debug)

            self.time = self.time + 1

    def __perform_and_update_TaskPerformedBySingleTaskWorker(self, print_debug=False):
        # TaskPerformedBySingleTaskWorker in pDES
    
        # 2. Get ready task and free resources
        ready_task_list = list(filter(lambda task:task.state == BaseTaskState.READY, self.workflow.task_list))
        worker_list = list(itertools.chain.from_iterable(list(map(lambda team:team.worker_list, self.organization.team_list))))
        free_worker_list = list(filter(lambda worker:worker.state == BaseResourceState.FREE, worker_list))
        
        # 3. Sort ready task and free resources
        ready_task_list = sorted(ready_task_list, key=lambda task: task.lst - task.est) # Task: TSLACK (a task which Slack time(LS-ES) is lower has high priority)
        free_worker_list = sorted(free_worker_list, key=lambda worker: sum(worker.workamount_skill_mean_map.values())) # Worker: SSP (a resource which amount of skill point is lower has high priority)

        if print_debug:
            print('Ready Task List')
            print([(rtask.name, rtask.remaining_work_amount) for rtask in ready_task_list])

        # 4. Allocate ready tasks to free resources
        for task in ready_task_list:
            allocating_workers = list(filter(lambda worker: worker.has_skill(task.name) and self.__is_allocated(worker, task), free_worker_list))
            if len(allocating_workers)>0:
                task.allocated_worker_list.append(allocating_workers[0])
                free_worker_list.remove(allocating_workers[0])
        
        # 5. Perform and Update workflow and organization
        self.workflow.check_state(self.time, BaseTaskState.WORKING)
        cost_this_time = self.organization.add_labor_cost(only_working=True)
        self.cost_list.append(cost_this_time)
        self.workflow.perform(self.time)
        self.workflow.check_state(self.time, BaseTaskState.FINISHED)
        self.workflow.check_state(self.time, BaseTaskState.READY)
        self.workflow.update_PERT_data(self.time)

    
    def __perform_and_update_TaskPerformedBySingleTaskWorkers(self,print_debug=False):
        # TaskPerformedBySingleTaskWorkers in pDES

        # 2. Get ready task and free resources
        ready_and_working_task_list = list(filter(lambda task:task.state == BaseTaskState.READY or task.state == BaseTaskState.WORKING, self.workflow.task_list))
        worker_list = list(itertools.chain.from_iterable(list(map(lambda team:team.worker_list, self.organization.team_list))))
        free_worker_list = list(filter(lambda worker:worker.state == BaseResourceState.FREE, worker_list))
        
        # 3. Sort ready task and free resources
        ready_and_working_task_list = sorted(ready_and_working_task_list, key=lambda task: task.lst - task.est) # Task: TSLACK (a task which Slack time(LS-ES) is lower has high priority)
        free_worker_list = sorted(free_worker_list, key=lambda worker: sum(worker.workamount_skill_mean_map.values())) # Worker: SSP (a resource which amount of skill point is lower has high priority)
        
        if print_debug:
            print('Ready & Working Task List')
            print([(rtask.name, rtask.remaining_work_amount) for rtask in ready_and_working_task_list])
        
        # 4. Allocate ready tasks to free resources
        for task in ready_and_working_task_list:
            allocating_workers = list(filter(lambda worker: worker.has_skill(task.name) and self.__is_allocated(worker, task), free_worker_list))
            task.allocated_worker_list.extend([worker for worker in allocating_workers])
            for w in allocating_workers:
                free_worker_list.remove(w)
                
        # 5. Perform and Update workflow and organization
        self.workflow.check_state(self.time, BaseTaskState.WORKING)
        cost_this_time = self.organization.add_labor_cost(only_working=True)
        self.cost_list.append(cost_this_time)
        self.workflow.perform(self.time)
        self.workflow.check_state(self.time, BaseTaskState.FINISHED)
        self.workflow.check_state(self.time, BaseTaskState.READY)
        self.workflow.update_PERT_data(self.time)


    def __is_allocated(self, worker, task):
        team = list(filter(lambda team: team.ID == worker.team_id, self.organization.team_list))[0]
        return task in team.targeted_task_list
    

