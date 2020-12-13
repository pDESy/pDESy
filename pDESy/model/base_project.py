#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta
import datetime
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
from .base_component import BaseComponent
from .base_task import BaseTask, BaseTaskState, BaseTaskDependency
from .base_team import BaseTeam
from .base_worker import BaseWorker
import itertools
from .base_resource import BaseResourceState
from .base_factory import BaseFactory
from .base_facility import BaseFacility, BaseFacilityState


class BaseProject(object, metaclass=ABCMeta):
    """BaseProject
    BaseProject class for expressing target project
    including product, organization and workflow.
    This class will be used as template.

    Args:
        file_path (str, optional):
            File path of this project data for reading.
            Defaults to None. (New Project)
        init_datetime (datetime.datetime, optional):
            Start datetime of project.
            Defaults to None -> datetime.datetime.now().
        unit_timedelta (datetime.timedelta, optional):
            Unit time of simulation.
            Defaults to None -> datetime.timedelta(minutes=1).
        product (BaseProduct, optional):
            BaseProduct in this project.
            Defaults to None. (New Project)
        organization (BaseOrganization, optional):
            BaseOrganization in this project.
            Defaults to None. (New Project)
        workflow (BaseWorkflow, optional):
            BaseWorkflow in this project.
            Defaults to None. (New Project)
        time (int, optional):
            Simulation time executing this method.
            Defaults to 0.
        cost_list (List[float], optional):
            Basic variable.
            History or record of this project's cost in simulation.
            Defaults to None -> [].
    """

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
    ):

        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.init_datetime = (
            init_datetime if init_datetime is not None else datetime.datetime.now()
        )
        self.unit_timedelta = (
            unit_timedelta
            if unit_timedelta is not None
            else datetime.timedelta(minutes=1)
        )

        # Changeable variable on simulation
        # --
        # Basic variables
        if product is not None:
            self.product = product
        else:
            self.product = None

        if organization is not None:
            self.organization = organization
        else:
            self.organization = None

        if workflow is not None:
            self.workflow = workflow
        else:
            self.workflow = None

        if time != int(0):
            self.time = time
        else:
            self.time = int(0)

        if cost_list is not None:
            self.cost_list = cost_list
        else:
            self.cost_list = []

    def __str__(self):
        """
        Returns:
            str: time and name lists of product, organization and workflow.
        """
        return "TIME: {}\nPRODUCT\n{}\n\nORGANIZATION\n{}\n\nWORKFLOW\n{}".format(
            self.time, str(self.product), str(self.organization), str(self.workflow)
        )

    def initialize(self):
        """
        Initialize the changeable variables of this BaseProject.

        - time
        - cost_list
        - changeable variables of product
        - changeable variables of organization
        - changeable variables of workflow

        """
        self.time = 0
        self.cost_list = []
        self.product.initialize()
        self.organization.initialize()
        self.workflow.initialize()

    def simulate(
        self,
        task_performed_mode="multi-workers",
        error_tol=1e-10,
        print_debug=False,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
        max_time=10000,
        unit_time=1,
    ):
        """
        Simulation function for simulate this BaseProject.

        Args:
            task_performed_mode (str, optional):
                Mode of performed task in simulation.
                pDESy has the following options of this mode in simulation.

                - multi-workers

                Defaults to "multi-workers".
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            print_debug (bool, optional):
                Whether print debug is include or not
                Defaults to False.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every time.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.
            max_time (int, optional):
                Max time of simulation.
                Defaults to 10000.
            unit_time (int, optional):
                Unit time of simulation.
                Defaults to 1.
        """

        if not (task_performed_mode == "multi-workers"):
            raise Exception(
                "Please check "
                "task_performed_mode"
                " which is equal to "
                "multi-workers"
                ""
            )

        # set simulation mode
        mode = 0
        if task_performed_mode == "multi-workers":
            mode = 1  # TaskPerformedBySingleTaskWorkers in pDES

        # check whether implementation or target mode simulation is finished or not
        if not (mode == 1):
            raise Exception("Sorry. This simulation mode is not yet implemented.")
        # -----------------------------------------------------------------------------

        self.initialize()

        while True:

            # 1. Check finished or not
            state_list = list(map(lambda task: task.state, self.workflow.task_list))
            if all(state == BaseTaskState.FINISHED for state in state_list):
                return

            # Error check
            if self.time >= max_time:
                raise Exception(
                    "Time Over! Please check your simulation model or increase "
                    "max_time"
                    " value"
                )

            # check now is business time or not
            working = True
            now_date_time = ""

            if (
                not weekend_working
                or work_start_hour is not None
                or work_finish_hour is not None
            ):
                now_date_time = self.init_datetime + self.time * self.unit_timedelta
                working = self.is_business_time(
                    now_date_time, weekend_working, work_start_hour, work_finish_hour
                )

            if print_debug:
                print("---")
                print(self.time, now_date_time, working)

            # 2. Allocate free resources to READY tasks
            if working:
                self.__allocate_single_task_workers(print_debug=print_debug)

            # 3. Pay cost to all resources in this time
            if working:
                cost_this_time = self.organization.add_labor_cost(only_working=True)
            else:
                cost_this_time = self.organization.add_labor_cost(
                    add_zero_to_all_workers=True, add_zero_to_all_facilities=True
                )
            self.cost_list.append(cost_this_time)

            # 4, Perform
            if working:
                if mode == 1:
                    self.__perform(print_debug=print_debug)

            # 5. Record
            self.__record(print_debug=print_debug)
            # 6. Update
            self.__update(print_debug=print_debug)

            self.time = self.time + unit_time

    def backward_simulate(
        self,
        task_performed_mode="multi-workers",
        error_tol=1e-10,
        print_debug=False,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
        max_time=10000,
        unit_time=-1,
        considering_due_time_of_tail_tasks=False,
        update_time_information_for_forward=True,
    ):
        """
        Backward Simulation function for simulate this BaseProject.

        Args:
            task_performed_mode (str, optional):
                Mode of performed task in simulation.
                pDESy has the following options of this mode in simulation.

                - single-worker
                - multi-workers

                Defaults to "multi-workers".
            error_tol (float, optional):
                Measures against numerical error.
                Defaults to 1e-10.
            print_debug (bool, optional):
                Whether print debug is include or not
                Defaults to False.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every time.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.
            max_time (int, optional):
                Max time of simulation.
                Defaults to 10000.
            unit_time (int, optional):
                Unit time of simulation.
                Defaults to -1.
            considering_due_time_of_tail_tasks (bool, optional):
                Consider due_time of tail tasks or not.
                Default to False.
            update_time_information_for_forward (bool, optional):
                Update time information for forward simulation after this simulation.
                Defaults to True.

        Note:
            This function is only for research and still in progress.
            Especially, this function is not suitable for simulation considering rework.
        """

        self.workflow.reverse_dependencies()

        autotask_removing_after_simulation = []
        try:
            if considering_due_time_of_tail_tasks:
                # Add dummy task for considering the difference of due_time
                tail_task_list = list(
                    filter(
                        lambda task: len(task.input_task_list) == 0,
                        self.workflow.task_list,
                    )
                )
                max_due_time = max([task.due_time for task in tail_task_list])
                for tail_task in tail_task_list:
                    if tail_task.due_time < max_due_time:
                        auto_task = BaseTask(
                            "auto",
                            auto_task=True,
                            default_work_amount=max_due_time - tail_task.due_time,
                        )
                        tail_task.append_input_task(
                            auto_task, task_dependency_mode=BaseTaskDependency.FS
                        )
                        autotask_removing_after_simulation.append(auto_task)
                        self.workflow.task_list.append(auto_task)
            if print_debug:
                print(autotask_removing_after_simulation)

            self.simulate(
                task_performed_mode=task_performed_mode,
                error_tol=error_tol,
                print_debug=print_debug,
                weekend_working=weekend_working,
                work_start_hour=work_start_hour,
                work_finish_hour=work_finish_hour,
                max_time=max_time,
                unit_time=unit_time,
            )

            if update_time_information_for_forward:
                # Change reverse result to normal result
                final_step = -self.time
                if considering_due_time_of_tail_tasks:
                    final_step = max_due_time

                # Task
                for task in self.workflow.task_list:
                    # Change start_time_list to finish_time_list
                    # finish_time_list to start_time_list
                    tmp = task.start_time_list
                    task.start_time_list = task.finish_time_list
                    task.finish_time_list = tmp
                    del tmp

                    # add (-final_step) to all time information
                    task.start_time_list = list(
                        map(lambda time: time + (final_step - 1), task.start_time_list)
                    )
                    task.finish_time_list = list(
                        map(lambda time: time + (final_step - 1), task.finish_time_list)
                    )

                # TODO we have to check and update this information
                min_start_time = 0
                if considering_due_time_of_tail_tasks:
                    min_start_time = float("inf")
                    for task in self.workflow.task_list:
                        tmp = min(task.start_time_list)
                        if tmp < min_start_time:
                            min_start_time = tmp
                for task in self.workflow.task_list:
                    task.ready_time_list = []
                    max_finish_time = min_start_time - 1
                    if len(task.output_task_list) > 0:  # still reverse in this line..
                        finish_time_list = []
                        for output_task in task.output_task_list:
                            finish_time_list.append(output_task[0].finish_time_list)
                        max_finish_time = max(finish_time_list)[0]
                    task.ready_time_list = [max_finish_time]

                # Team
                for team in self.organization.team_list:
                    # Worker
                    for worker in team.worker_list:
                        # Change start_time_list to finish_time_list
                        # finish_time_list to start_time_list
                        tmp = worker.start_time_list
                        worker.start_time_list = worker.finish_time_list
                        worker.finish_time_list = tmp
                        del tmp

                        # add (-final_step) to all time information
                        worker.start_time_list = list(
                            map(
                                lambda time: time + (final_step - 1),
                                worker.start_time_list,
                            )
                        )
                        worker.start_time_list.sort()
                        worker.finish_time_list = list(
                            map(
                                lambda time: time + (final_step - 1),
                                worker.finish_time_list,
                            )
                        )
                        worker.finish_time_list.sort()

                for factory in self.organization.factory_list:
                    # Facility
                    for resource in factory.facility_list:
                        # Change start_time_list to finish_time_list
                        # finish_time_list to start_time_list
                        tmp = resource.start_time_list
                        resource.start_time_list = resource.finish_time_list
                        resource.finish_time_list = tmp
                        del tmp

                        # add (-final_step) to all time information
                        resource.start_time_list = list(
                            map(
                                lambda time: time + (final_step - 1),
                                resource.start_time_list,
                            )
                        )
                        resource.start_time_list.sort()
                        resource.finish_time_list = list(
                            map(
                                lambda time: time + (final_step - 1),
                                resource.finish_time_list,
                            )
                        )
                        resource.finish_time_list.sort()

        except Exception as e:
            print(e)
        finally:
            for autotask in autotask_removing_after_simulation:
                for task, dependency in autotask.output_task_list:
                    task.input_task_list.remove([autotask, dependency])
                self.workflow.task_list.remove(autotask)
            self.workflow.reverse_dependencies()

    def __perform(self, print_debug=False):
        if print_debug:
            print("Allocation result in this time")
            worker_list = list(
                itertools.chain.from_iterable(
                    list(
                        map(lambda team: team.worker_list, self.organization.team_list)
                    )
                )
            )
            facility_list = list(
                itertools.chain.from_iterable(
                    list(
                        map(
                            lambda factory: factory.facility_list,
                            self.organization.factory_list,
                        )
                    )
                )
            )
            for worker in worker_list:
                print(
                    worker.name,
                    ":",
                    [assigned_task.name for assigned_task in worker.assigned_task_list],
                )
            for facility in facility_list:
                print(
                    facility.name,
                    ":",
                    [
                        assigned_task.name
                        for assigned_task in facility.assigned_task_list
                    ],
                )
            print("PERFORM")
        self.workflow.perform(self.time)

    def __record(self, print_debug=False):
        if print_debug:
            print("RECORD")
        self.workflow.record_allocated_workers_facilities_id()
        self.organization.record()
        self.product.record_placed_factory_id()

    def __update(self, print_debug=False):
        if print_debug:
            print("UPDATE")
        self.workflow.check_state(self.time, BaseTaskState.FINISHED)
        self.product.check_removing_placed_factory()
        self.workflow.check_state(self.time, BaseTaskState.READY)
        self.workflow.update_PERT_data(self.time)

    def __allocate_single_task_workers(self, print_debug=False):

        # Check free factory before setting components
        if print_debug:
            print("ALLOCATE")
            print("Factory - Component before setting components in this time")
            for factory in self.organization.factory_list:
                print(
                    factory.name
                    + ":"
                    + str([c.name for c in factory.placed_component_list])
                )

        target_factory_id_list = [f.ID for f in self.organization.factory_list]

        # A. Extract READY components
        ready_component_list = list(
            filter(lambda c: c.is_ready() is True, self.product.component_list)
        )
        if print_debug:
            print("Ready Component list before allocating")
            print([c.name for c in ready_component_list])

        # C. Decide which factory put each ready component
        # TODO component sorting or task sorting
        for ready_component in ready_component_list:
            ready_task_list = list(
                filter(
                    lambda task: task.state == BaseTaskState.READY,
                    ready_component.targeted_task_list,
                )
            )
            for ready_task in ready_task_list:
                for factory in ready_task.allocated_factory_list:
                    if factory.ID in target_factory_id_list:
                        if (
                            factory.can_put(ready_component)
                            and factory.get_total_workamount_skill(ready_task.name)
                            > 1e-10
                        ):
                            # move ready_component from None to factory
                            pre_factory = ready_component.placed_factory
                            if pre_factory is not None:
                                ready_component.set_placed_factory(None)
                                pre_factory.remove_placed_component(ready_component)
                            ready_component.set_placed_factory(factory)
                            factory.set_placed_component(ready_component)
                            break
                else:
                    continue
                break

        # Check free factory after setting components
        if print_debug:
            print("Factory - Component after setting components in this time")
            for factory in self.organization.factory_list:
                print(
                    factory.name
                    + ":"
                    + str([c.name for c in factory.placed_component_list])
                )
        # ---------------------------------------------------------------

        # 1. Get ready task and free resources
        ready_and_working_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.READY
                or task.state == BaseTaskState.WORKING,
                self.workflow.task_list,
            )
        )

        if print_debug:
            print("Ready & Working Task List")
            print(
                [
                    (rtask.name, rtask.remaining_work_amount)
                    for rtask in ready_and_working_task_list
                ]
            )

        # Candidate allocating task list (auto_task=False)
        ready_and_working_task_list = list(
            filter(lambda task: not task.auto_task, ready_and_working_task_list)
        )

        worker_list = list(
            itertools.chain.from_iterable(
                list(map(lambda team: team.worker_list, self.organization.team_list))
            )
        )

        free_worker_list = list(
            filter(lambda worker: worker.state == BaseResourceState.FREE, worker_list)
        )

        # 2. Sort ready task and free resources
        # Task: TSLACK (a task which Slack time(LS-ES) is lower has high priority)
        ready_and_working_task_list = sorted(
            ready_and_working_task_list, key=lambda task: task.lst - task.est
        )

        # 3. Allocate ready tasks to free resources
        for task in ready_and_working_task_list:

            # Worker: SSP
            # a resource which amount of skillpoint is lower has high priority
            free_worker_list = sorted(
                free_worker_list,
                key=lambda worker: sum(worker.workamount_skill_mean_map.values()),
            )

            allocating_workers = list(
                filter(
                    lambda worker: worker.has_workamount_skill(task.name)
                    and self.__is_allocated_worker(worker, task),
                    free_worker_list,
                )
            )

            if task.need_facility:

                # Search candidate facilities from the list of placed_factory
                placed_factory = task.target_component.placed_factory

                if placed_factory is not None:

                    free_facility_list = list(
                        filter(
                            lambda facility: facility.state == BaseFacilityState.FREE,
                            placed_factory.facility_list,
                        )
                    )

                    # Facility sorting
                    # SSP: Resource which amount of point is lower has high priority
                    free_facility_list = sorted(
                        free_facility_list,
                        key=lambda facility: sum(
                            facility.workamount_skill_mean_map.values()
                        ),
                    )

                    # candidate facilities
                    allocating_facilities = list(
                        filter(
                            lambda facility: facility.has_workamount_skill(task.name)
                            and self.__is_allocated_facility(facility, task),
                            free_facility_list,
                        )
                    )

                    for facility in allocating_facilities:
                        for worker in allocating_workers:
                            if task.can_add_resources(worker=worker, facility=facility):
                                task.allocated_worker_list.append(worker)
                                task.allocated_facility_list.append(facility)
                                allocating_workers.remove(worker)
                                free_worker_list = [
                                    w for w in free_worker_list if w.ID != worker.ID
                                ]
                                allocating_facilities.remove(facility)
                                break

            else:
                for worker in allocating_workers:
                    if task.can_add_resources(worker=worker):
                        task.allocated_worker_list.append(worker)
                        free_worker_list.remove(worker)

        # 4. Update state of task newly allocated resources (READY -> WORKING)
        self.workflow.check_state(self.time, BaseTaskState.WORKING)

    def __is_allocated_worker(self, worker, task):
        team = list(
            filter(lambda team: team.ID == worker.team_id, self.organization.team_list)
        )[0]
        return task in team.targeted_task_list

    def __is_allocated_facility(self, facility, task):
        factory = list(
            filter(
                lambda factory: factory.ID == facility.factory_id,
                self.organization.factory_list,
            )
        )[0]
        return task in factory.targeted_task_list

    def is_business_time(
        self,
        target_datetime: datetime.datetime,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
    ):
        """
        Check whether target_datetime is business time or not in this project.

        Args:
            target_datetime (datetime.datetime):
                Target datetime of checking business time or not.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every time.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.

        Returns:
            bool: whether target_datetime is business time or not.
        """
        if not weekend_working:
            if target_datetime.weekday() >= 5:
                return False
            else:
                if work_start_hour is not None and work_finish_hour is not None:
                    if (
                        target_datetime.hour >= work_start_hour
                        and target_datetime.hour <= work_finish_hour
                    ):
                        return True
                    else:
                        return False
                else:
                    return True

        else:
            if work_start_hour is not None and work_finish_hour is not None:
                if (
                    target_datetime.hour >= work_start_hour
                    and target_datetime.hour <= work_finish_hour
                ):
                    return True
                else:
                    return False
            else:
                return True

    def create_gantt_plotly(
        self,
        title="Gantt Chart",
        colors=None,
        index_col=None,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=False,
        show_colorbar=True,
        finish_margin=1.0,
        save_fig_path=None,
    ):
        """
        Method for creating Gantt chart by plotly.
        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            title (str, optional):
                Title of Gantt chart.
                Defaults to "Gantt Chart".
            colors (Dict[str, str], optional):
                Color setting of plotly Gantt chart.
                Defaults to None -> dict(Component="rgb(246, 37, 105)",Task="rgb(146, 237, 5)"
                ,Worker="rgb(46, 137, 205)"
                ,Facility="rgb(46, 137, 205)",).
            index_col (str, optional):
                index_col of plotly Gantt chart.
                Defaults to None -> "Type".
            showgrid_x (bool, optional):
                showgrid_x of plotly Gantt chart.
                Defaults to True.
            showgrid_y (bool, optional):
                showgrid_y of plotly Gantt chart.
                Defaults to True.
            group_tasks (bool, optional):
                group_tasks of plotly Gantt chart.
                Defaults to True.
            show_colorbar (bool, optional):
                show_colorbar of plotly Gantt chart.
                Defaults to True.
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a gantt chart

        TODO:
            Saving figure file is not implemented...
        """
        colors = (
            colors
            if colors is not None
            else dict(
                Component="rgb(246, 37, 105)",
                Task="rgb(146, 237, 5)",
                Worker="rgb(46, 137, 205)",
                Facility="rgb(46, 137, 205)",
            )
        )
        index_col = index_col if index_col is not None else "Type"
        df = []
        df.extend(
            self.product.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            )
        )
        df.extend(
            self.workflow.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            ),
        )
        df.extend(
            self.organization.create_data_for_gantt_plotly(
                self.init_datetime, self.unit_timedelta, finish_margin=finish_margin
            )
        )
        fig = ff.create_gantt(
            df,
            title=title,
            colors=colors,
            index_col=index_col,
            showgrid_x=showgrid_x,
            showgrid_y=showgrid_y,
            show_colorbar=show_colorbar,
            group_tasks=group_tasks,
        )
        if save_fig_path is not None:
            print("--- Sorry, save fig is not implemented now.---")
        #     plotly.io.write_image(fig, save_fig_path)

        return fig

    def get_networkx_graph(self, view_workers=False, view_facilities=False):
        """
        Get the information of networkx graph.

        Args:
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
        Returns:
            G: networkx.Digraph()
        """
        Gp = self.product.get_networkx_graph()
        Gw = self.workflow.get_networkx_graph()
        Go = self.organization.get_networkx_graph(
            view_workers=view_workers, view_facilities=view_facilities
        )
        G = nx.compose_all([Gp, Gw, Go])

        # add edge between product and workflow
        for c in self.product.component_list:
            for task in c.targeted_task_list:
                G.add_edge(c, task)

        # add edge between workflow and team in organization
        for team in self.organization.team_list:
            for task in team.targeted_task_list:
                G.add_edge(team, task)

        if view_workers:
            for team in self.organization.team_list:
                for w in team.worker_list:
                    # G.add_node(w)
                    G.add_edge(team, w)

        # add edge between workflow and factory in organization
        for factory in self.organization.factory_list:
            for task in factory.targeted_task_list:
                G.add_edge(factory, task)

        if view_facilities:
            for factory in self.organization.factory_list:
                for w in factory.facility_list:
                    # G.add_node(w)
                    G.add_edge(factory, w)

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        with_labels=True,
        component_node_color="#FF6600",
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        view_facilities=False,
        factory_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        **kwds,
    ):
        """
        Draw networkx

        Args:
            G (networkx.SDigraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
            arrows (bool, optional):
                Digraph or Graph(no arrows).
                Defaults to True.
            with_labels (bool, optional):
                Label is describing or not.
                Defaults to True.
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
            factory_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """

        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)

        # Product
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.product.component_list,
            node_color=component_node_color,
        )
        # Workflow
        normal_task_list = [
            task for task in self.workflow.task_list if not task.auto_task
        ]
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=normal_task_list,
            node_color=task_node_color,
        )
        auto_task_list = [task for task in self.workflow.task_list if task.auto_task]
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=auto_task_list,
            node_color=auto_task_node_color,
        )
        # Organization - Team
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.organization.team_list,
            node_color=team_node_color,
            # **kwds,
        )
        if view_workers:

            worker_list = []
            for team in self.organization.team_list:
                worker_list.extend(team.worker_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                with_labels=with_labels,
                nodelist=worker_list,
                node_color=worker_node_color,
                # **kwds,
            )

        # Organization - Factory
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.organization.factory_list,
            node_color=factory_node_color,
            # **kwds,
        )
        if view_facilities:

            facility_list = []
            for factory in self.organization.factory_list:
                facility_list.extend(factory.facility_list)

            nx.draw_networkx_nodes(
                G,
                pos,
                with_labels=with_labels,
                nodelist=facility_list,
                node_color=facility_node_color,
                # **kwds,
            )

        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)

    def get_node_and_edge_trace_for_plotly_network(
        self,
        G=None,
        pos=None,
        node_size=20,
        component_node_color="#FF6600",
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        factory_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        view_facilities=False,
    ):
        """
        Get nodes and edges information of plotly network.

        Args:
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            factory_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.

        Returns:
            component_node_trace: component nodes information of plotly network.
            task_node_trace: task nodes information of plotly network.
            auto_task_node_trace: auto task nodes information of plotly network.
            team_node_trace: team nodes information of plotly network.
            worker_node_trace: resource nodes information of plotly network.
            factory_node_trace: Factory Node information of plotly network.
            facility_node_trace: Facility Node information of plotly network.
            edge_trace: Edge information of plotly network.
        """
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)

        component_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=component_node_color,
                size=node_size,
            ),
        )

        task_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=task_node_color,
                size=node_size,
            ),
        )

        auto_task_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=auto_task_node_color,
                size=node_size,
            ),
        )

        team_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=team_node_color,
                size=node_size,
            ),
        )

        worker_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=worker_node_color,
                size=node_size,
            ),
        )

        factory_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=factory_node_color,
                size=node_size,
            ),
        )

        facility_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color=facility_node_color,
                size=node_size,
            ),
        )

        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0, color="#888"), hoverinfo="none", mode="lines"
        )

        for node in G.nodes:
            x, y = pos[node]
            if isinstance(node, BaseComponent):
                component_node_trace["x"] = component_node_trace["x"] + (x,)
                component_node_trace["y"] = component_node_trace["y"] + (y,)
                component_node_trace["text"] = component_node_trace["text"] + (node,)
            elif isinstance(node, BaseTask):
                if not node.auto_task:
                    task_node_trace["x"] = task_node_trace["x"] + (x,)
                    task_node_trace["y"] = task_node_trace["y"] + (y,)
                    task_node_trace["text"] = task_node_trace["text"] + (node,)
                elif node.auto_task:
                    auto_task_node_trace["x"] = auto_task_node_trace["x"] + (x,)
                    auto_task_node_trace["y"] = auto_task_node_trace["y"] + (y,)
                    auto_task_node_trace["text"] = auto_task_node_trace["text"] + (
                        node,
                    )
            elif isinstance(node, BaseFactory):
                factory_node_trace["x"] = factory_node_trace["x"] + (x,)
                factory_node_trace["y"] = factory_node_trace["y"] + (y,)
                factory_node_trace["text"] = factory_node_trace["text"] + (node,)
            elif isinstance(node, BaseFacility):
                facility_node_trace["x"] = facility_node_trace["x"] + (x,)
                facility_node_trace["y"] = facility_node_trace["y"] + (y,)
                facility_node_trace["text"] = facility_node_trace["text"] + (node,)
            elif isinstance(node, BaseTeam):
                team_node_trace["x"] = team_node_trace["x"] + (x,)
                team_node_trace["y"] = team_node_trace["y"] + (y,)
                team_node_trace["text"] = team_node_trace["text"] + (node,)
            elif isinstance(node, BaseWorker):
                worker_node_trace["x"] = worker_node_trace["x"] + (x,)
                worker_node_trace["y"] = worker_node_trace["y"] + (y,)
                worker_node_trace["text"] = worker_node_trace["text"] + (node,)

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace["x"] += (xposx, yposx)
            edge_trace["y"] += (xposy, yposy)

        return (
            component_node_trace,
            task_node_trace,
            auto_task_node_trace,
            team_node_trace,
            worker_node_trace,
            factory_node_trace,
            facility_node_trace,
            edge_trace,
        )

    def draw_plotly_network(
        self,
        G=None,
        pos=None,
        title="Project",
        node_size=20,
        component_node_color="#FF6600",
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        team_node_color="#0099FF",
        worker_node_color="#D9E5FF",
        view_workers=False,
        factory_node_color="#0099FF",
        facility_node_color="#D9E5FF",
        view_facilities=False,
        save_fig_path=None,
    ):
        """
        Draw plotly network

        Args:
            G (networkx.Digraph, optional):
                The information of networkx graph.
                Defaults to None -> self.get_networkx_graph().
            pos (networkx.layout, optional):
                Layout of networkx.
                Defaults to None -> networkx.spring_layout(G).
            title (str, optional):
                Figure title of this network.
                Defaults to "Project".
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            component_node_color (str, optional):
                Node color setting information.
                Defaults to "#FF6600".
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            team_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            worker_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            factory_node_color (str, optional):
                Node color setting information.
                Defaults to "#0099FF".
            facility_node_color (str, optional):
                Node color setting information.
                Defaults to "#D9E5FF".
            view_facilities (bool, optional):
                Including facilities in networkx graph or not.
                Default to False.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network

        TODO:
            Saving figure file is not implemented...
        """
        G = (
            G
            if G is not None
            else self.get_networkx_graph(
                view_workers=view_workers, view_facilities=view_facilities
            )
        )
        pos = pos if pos is not None else nx.spring_layout(G)
        (
            component_node_trace,
            task_node_trace,
            auto_task_node_trace,
            team_node_trace,
            worker_node_trace,
            factory_node_trace,
            facility_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(G, pos, node_size=node_size)
        fig = go.Figure(
            data=[
                edge_trace,
                component_node_trace,
                task_node_trace,
                auto_task_node_trace,
                team_node_trace,
                worker_node_trace,
                factory_node_trace,
                facility_node_trace,
            ],
            layout=go.Layout(
                title=title,
                showlegend=False,
                #         hovermode='closest',
                #         margin=dict(b=20,l=5,r=5,t=40),
                annotations=[
                    dict(
                        ax=edge_trace["x"][index * 2],
                        ay=edge_trace["y"][index * 2],
                        axref="x",
                        ayref="y",
                        x=edge_trace["x"][index * 2 + 1],
                        y=edge_trace["y"][index * 2 + 1],
                        xref="x",
                        yref="y",
                        showarrow=True,
                        arrowhead=5,
                    )
                    for index in range(0, int(len(edge_trace["x"]) / 2))
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        if save_fig_path is not None:
            print("--- Sorry, save fig is not implemented now.---")
        #     plotly.io.write_image(fig, save_fig_path)

        return fig

    # ---
    # READ FUNCTION
    # ---

    # def read_pDESy_web_json(self, file_path: str, encoding=None):
    #     """
    #     Read json file from pDESy.org.
    #     This method is not stable now.

    #     Args:
    #         file_path (str):
    #             file path by getting pDESy.org
    #         encoding ([type], optional):
    #             Defaults to None -> utf-8.
    #     TODO:
    #         pDESy.org for describing project in web browser should be developed...
    #     """
    #     encoding = encoding if encoding is not None else "utf-8"
    #     pdes_json = open(file_path, "r", encoding=encoding)
    #     data = json.load(pdes_json)

    #     # Get Product information including Components without dependency
    #     cd_list = list(filter(lambda node: node["type"] == "Component", data))
    #     component_list = [
    #         BaseComponent(
    #             cd["name"],
    #             ID=cd["id"],
    #             error_tolerance=float(cd["userData"]["errorTolerance"]),
    #         )
    #         for cd in cd_list
    #     ]

    #     # Get Workflow information including Tasks without dependency
    #     td_list = list(filter(lambda node: node["type"] == "Task", data))
    #     task_list = [
    #         BaseTask(
    #             td["name"],
    #             ID=td["id"],
    #             default_work_amount=float(td["userData"]["workAmount"]),
    #             default_progress=float(td["userData"]["progress"]),
    #             additional_work_amount=float(td["userData"]["additionalWorkAmount"]),
    #         )
    #         for td in td_list
    #     ]

    #     # Get Organization information including Teams without dependency
    #     team_list = []
    #     ted_list = list(filter(lambda node: node["type"] == "Team", data))
    #     for team_data in ted_list:
    #         worker_list = []
    #         worker_list_data = team_data["userData"]["WorkerList"]
    #         if type(worker_list_data["Worker"]) is dict:
    #             worker_list_data["Worker"] = [worker_list_data["Worker"]]
    #         for worker_data in worker_list_data["Worker"]:
    #             work_amount_skill_mean_info = {}
    #             work_amount_skill_sd_info = {}
    #             quality_skill_mean_info = {}
    #             # quality_skill_sd_info = {}
    #             if "WorkAmountSkill" in worker_data:
    #                 if type(worker_data["WorkAmountSkill"]) is list:
    #                     for skill_data in worker_data["WorkAmountSkill"]:
    #                         work_amount_skill_mean_info[skill_data["-name"]] = float(
    #                             skill_data["-value"]
    #                         )
    #                         work_amount_skill_sd_info[skill_data["-name"]] = float(
    #                             skill_data["-value_sd"]
    #                         )
    #                 elif type(worker_data["WorkAmountSkill"]) is dict:
    #                     work_amount_skill_mean_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value"])
    #                     work_amount_skill_sd_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
    #             # if "QualitySkill" in worker_data:
    #             #     if type(worker_data["QualitySkill"]) is list:
    #             #         for skill_data in worker_data["QualitySkill"]:
    #             #             quality_skill_mean_info[skill_data["-name"]] = float(
    #             #                 skill_data["-value"]
    #             #             )
    #             #             # quality_skill_sd_info[skill_data['-name']] =
    #             #             # float(skill_data['-value_sd'])
    #             #     elif type(worker_data["QualitySkill"]) is dict:
    #             #         quality_skill_mean_info[
    #             #             worker_data["QualitySkill"]["-name"]
    #             #         ] = float(worker_data["QualitySkill"]["-value"])
    #             worker_list.append(
    #                 BaseResource(
    #                     worker_data["Name"],
    #                     team_id=team_data["id"],
    #                     cost_per_time=float(worker_data["Cost"]),
    #                     workamount_skill_mean_map=work_amount_skill_mean_info,
    #                     workamount_skill_sd_map=work_amount_skill_sd_info,
    #                     quality_skill_mean_map=quality_skill_mean_info,
    #                 )
    #             )
    #         team_list.append(
    #             BaseTeam(team_data["name"],ID=team_data["id"],worker_list=worker_list)
    #         )

    #     # Get Links information including
    #     # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
    #     l_list = list(filter(lambda node: node["type"] == "draw2d.Connection", data))
    #     for link in l_list:
    #         org_id = link["source"]["node"]
    #         org_type = list(filter(lambda node: node["id"]==org_id, data))[0]["type"]
    #         dst_id = link["target"]["node"]
    #         dst_type = list(filter(lambda node: node["id"]==dst_id, data))[0]["type"]
    #         if org_type == "Component" and dst_type == "Component":
    #             org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
    #             dst_c = list(filter(lambda c: c.ID == dst_id, component_list))[0]
    #             org_c.parent_component_list.append(dst_c)
    #             dst_c.child_component_list.append(org_c)
    #         elif org_type == "Task" and dst_type == "Task":
    #             org_task = list(filter(lambda c: c.ID == org_id, task_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
    #             org_task.output_task_list.append(dst_task)
    #             dst_task.input_task_list.append(org_task)
    #         elif org_type == "Team" and dst_type == "Team":
    #             org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
    #             dst_team = list(filter(lambda c: c.ID == dst_id, team_list))[0]
    #             # org_task.output_task_id_list.append(dst_task.ID)
    #             dst_team.parent_team_id = org_team.ID
    #         elif org_type == "Component" and dst_type == "Task":
    #             org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
    #             org_c.targeted_task_list.append(dst_task)
    #             dst_task.target_component_list.append(org_c)
    #         elif org_type == "Team" and dst_type == "Task":
    #             org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
    #             org_team.targeted_task_list.append(dst_task)
    #             dst_task.allocated_team_list.append(org_team)

    #     # Aggregate
    #     self.product = BaseProduct(component_list)
    #     self.workflow = BaseWorkflow(task_list)
    #     self.organization = BaseOrganization(team_list)

    # def read_pDES_json(self, file_path: str, encoding=None):
    #     """
    #     Read json file converted from pDES file.
    #     This method is not stable now.

    #     Args:
    #         file_path (str):
    #             file path by getting pDES and converted to json
    #         encoding ([type], optional):
    #             Defaults to None -> utf-8.
    #     """
    #     encoding = encoding if encoding is not None else "utf-8"
    #     pdes_json = open(file_path, "r", encoding=encoding)
    #     data = json.load(pdes_json)

    #     # Get Product information including Components without dependency
    #     cd_list = data["ProjectDiagram"]["NodeElementList"]["ComponentNode"]
    #     component_list = [
    #         BaseComponent(
    #             cd["Name"], ID=cd["-id"],
    #         )
    #         for cd in cd_list
    #     ]

    #     # Get Workflow information including Tasks without dependency
    #     td_list = data["ProjectDiagram"]["NodeElementList"]["TaskNode"]
    #     task_list = [
    #         BaseTask(
    #             td["Name"],
    #             ID=td["-id"],
    #             default_work_amount=float(td["WorkAmount"]),
    #             default_progress=float(td["Progress"]),
    #             # additional_work_amount=float(td["AdditionalWorkAmount"]),
    #         )
    #         for td in td_list
    #     ]

    #     # Get Organization information including Teams without dependency
    #     team_list = []
    #     ted_list = data["ProjectDiagram"]["NodeElementList"]["TeamNode"]
    #     for team_data in ted_list:
    #         worker_list = []
    #         worker_list_data = team_data["WorkerList"]
    #         if type(worker_list_data["Worker"]) is dict:
    #             worker_list_data["Worker"] = [worker_list_data["Worker"]]
    #         for worker_data in worker_list_data["Worker"]:
    #             work_amount_skill_mean_info = {}
    #             work_amount_skill_sd_info = {}
    #             quality_skill_mean_info = {}
    #             # quality_skill_sd_info = {}
    #             if "WorkAmountSkill" in worker_data:
    #                 if type(worker_data["WorkAmountSkill"]) is list:
    #                     for skill_data in worker_data["WorkAmountSkill"]:
    #                         work_amount_skill_mean_info[skill_data["-name"]] = float(
    #                             skill_data["-value"]
    #                         )
    #                         work_amount_skill_sd_info[skill_data["-name"]] = float(
    #                             skill_data["-value_sd"]
    #                         )
    #                 elif type(worker_data["WorkAmountSkill"]) is dict:
    #                     work_amount_skill_mean_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value"])
    #                     work_amount_skill_sd_info[
    #                         worker_data["WorkAmountSkill"]["-name"]
    #                     ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
    #             # if "QualitySkill" in worker_data:
    #             #     if type(worker_data["QualitySkill"]) is list:
    #             #         for skill_data in worker_data["QualitySkill"]:
    #             #             quality_skill_mean_info[skill_data["-name"]] = float(
    #             #                 skill_data["-value"]
    #             #             )
    #             #             # quality_skill_sd_info[skill_data['-name']]
    #             #             #  = float(skill_data['-value_sd'])
    #             #     elif type(worker_data["QualitySkill"]) is dict:
    #             #         quality_skill_mean_info[
    #             #             worker_data["QualitySkill"]["-name"]
    #             #         ] = float(worker_data["QualitySkill"]["-value"])
    #             worker_list.append(
    #                 BaseResource(
    #                     worker_data["Name"],
    #                     team_id=team_data["-id"],
    #                     cost_per_time=float(worker_data["Cost"]),
    #                     workamount_skill_mean_map=work_amount_skill_mean_info,
    #                     workamount_skill_sd_map=work_amount_skill_sd_info,
    #                     quality_skill_mean_map=quality_skill_mean_info,
    #                 )
    #             )
    #         team_list.append(
    #             BaseTeam(
    #                 team_data["Name"], ID=team_data["-id"], worker_list=worker_list
    #             )
    #         )
    #     self.organization = BaseOrganization(team_list)

    #     # Get Links information including
    #     # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
    #     l_list = data["ProjectDiagram"]["LinkList"]["Link"]
    #     for link in l_list:
    #         if link["-type"] == "ComponentLink":
    #             org_c = list(filter(lambda c: c.ID==link["-org"], component_list))[0]
    #             dst_c = list(filter(lambda c: c.ID==link["-dst"], component_list))[0]
    #             org_c.parent_component_list.append(dst_c)
    #             dst_c.child_component_list.append(org_c)
    #         elif link["-type"] == "TaskLink":
    #             org_task = list(filter(lambda c: c.ID == link["-org"], task_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
    #             org_task.output_task_list.append(dst_task)
    #             dst_task.input_task_list.append(org_task)
    #         elif link["-type"] == "TeamLink":
    #             org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
    #             dst_team = list(filter(lambda c: c.ID == link["-dst"], team_list))[0]
    #             # org_task.output_task_id_list.append(dst_task.ID)
    #             dst_team.get_work_amount_skill_progress_team_id = org_team.ID
    #         elif link["-type"] == "TargetComponentLink":
    #             org_c = list(filter(lambda c: c.ID==link["-org"], component_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
    #             org_c.targeted_task_list.append(dst_task)
    #             dst_task.target_component_list.append(org_c)
    #         elif link["-type"] == "AllocationLink":
    #             org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
    #             dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
    #             org_team.targeted_task_list.append(dst_task)
    #             dst_task.allocated_team_list.append(org_team)

    #     # Aggregate
    #     self.product = BaseProduct(component_list)
    #     self.workflow = BaseWorkflow(task_list)
    #     self.organization = BaseOrganization(team_list)
