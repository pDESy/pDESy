#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta
import datetime
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
from .base_component import BaseComponent
from .base_task import BaseTask, BaseTaskState
from .base_team import BaseTeam
import itertools
from .base_resource import BaseResource, BaseResourceState
import json
from .base_product import BaseProduct
from .base_workflow import BaseWorkflow
from .base_organization import BaseOrganization


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
            Unit time of simulattion.
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
            History or record of this project's cost in simumation.
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

    # @abstractmethod
    # def read_pDES_json(self, file_path: str, encoding: str):
    #     "This abstract method should be implemented in your class"

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
        """
        Simulation funciton for simulate this BaseProject.

        Args:
            worker_perfoming_mode (str, optional):
                Mode of worker's performance in simulation.
                pDESy has the following options of this mode in simulation.

                - single-task
                - multi-task

                Defaults to "single-task".
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
                Whether prrint debug is inclde or not
                Defaults to False.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every timw.
            work_finish_hour (int, optional):
                Finish working hour in one day .
                Defaults to None. This means workers work every time.
            max_time (int, optional):
                Max time of simulation.
                Defaults to 10000.
        """
        # ----------------------------------------------------------------------------
        # Simulation mode check
        # Error check
        if not (
            worker_perfoming_mode == "single-task"
            or worker_perfoming_mode == "multi-task"
        ):
            raise Exception(
                "Please check "
                "worker_performing_mode"
                " which is equal to "
                "single-task"
                " or "
                "multi-task"
                ""
            )

        if not (
            task_performed_mode == "single-worker"
            or task_performed_mode == "multi-workers"
        ):
            raise Exception(
                "Please check "
                "task_performed_mode"
                " which is equal to "
                "single-worker"
                " or "
                "multi-workers"
                ""
            )

        # set simulation mode
        mode = 0
        if (
            worker_perfoming_mode == "single-task"
            and task_performed_mode == "single-worker"
        ):
            mode = 1  # TaskPerformedBySingleTaskWorker in pDES
        if (
            worker_perfoming_mode == "single-task"
            and task_performed_mode == "multi-workers"
        ):
            mode = 2  # TaskPerformedBySingleTaskWorkers in pDES
        if (
            worker_perfoming_mode == "multi-task"
            and task_performed_mode == "single-worker"
        ):
            mode = 3
        if (
            worker_perfoming_mode == "multi-task"
            and task_performed_mode == "multi-workers"
        ):
            mode = 4

        # check whether implementation or target mode simulation is finished or not
        if not (mode == 1 or mode == 2):
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
                print(self.time, now_date_time, working)

            if working:
                if mode == 1:
                    self.__perform_and_update_TaskPerformedBySingleTaskWorker(
                        print_debug=print_debug
                    )
                elif mode == 2:
                    self.__perform_and_update_TaskPerformedBySingleTaskWorkers(
                        print_debug=print_debug
                    )
            else:
                # not working time
                cost_this_time = self.organization.add_labor_cost(
                    add_zero_to_all_workers=True
                )
                self.cost_list.append(cost_this_time)

            self.time = self.time + 1

    def __perform_and_update_TaskPerformedBySingleTaskWorker(self, print_debug=False):
        # TaskPerformedBySingleTaskWorker in pDES

        # 2. Get ready task and free resources
        ready_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.READY, self.workflow.task_list
            )
        )

        if print_debug:
            print("Ready Task List")
            print(
                [(rtask.name, rtask.remaining_work_amount) for rtask in ready_task_list]
            )

        # Candidate allocating task list (auto_task=False)
        ready_task_list = list(filter(lambda task: not task.auto_task, ready_task_list))

        worker_list = list(
            itertools.chain.from_iterable(
                list(map(lambda team: team.worker_list, self.organization.team_list))
            )
        )
        free_worker_list = list(
            filter(lambda worker: worker.state == BaseResourceState.FREE, worker_list)
        )

        # 3. Sort ready task and free resources
        # Task: TSLACK (a task which Slack time(LS-ES) is lower has high priority)
        ready_task_list = sorted(ready_task_list, key=lambda task: task.lst - task.est)
        # Worker: SSP (a resource which amount of skillpoint is lower has high priority)
        free_worker_list = sorted(
            free_worker_list,
            key=lambda worker: sum(worker.workamount_skill_mean_map.values()),
        )

        # 4. Allocate ready tasks to free resources
        for task in ready_task_list:
            allocating_workers = list(
                filter(
                    lambda worker: worker.has_workamount_skill(task.name)
                    and self.__is_allocated(worker, task),
                    free_worker_list,
                )
            )
            if len(allocating_workers) > 0:
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

    def __perform_and_update_TaskPerformedBySingleTaskWorkers(self, print_debug=False):
        # TaskPerformedBySingleTaskWorkers in pDES

        # 2. Get ready task and free resources
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

        # 3. Sort ready task and free resources
        # Task: TSLACK (a task which Slack time(LS-ES) is lower has high priority)
        ready_and_working_task_list = sorted(
            ready_and_working_task_list, key=lambda task: task.lst - task.est
        )
        # Worker: SSP (a resource which amount of skillpoint is lower has high priority)
        free_worker_list = sorted(
            free_worker_list,
            key=lambda worker: sum(worker.workamount_skill_mean_map.values()),
        )

        # if print_debug:
        #     print("Ready & Working Task List")
        #     print(
        #         [
        #             (rtask.name, rtask.remaining_work_amount)
        #             for rtask in ready_and_working_task_list
        #         ]
        #     )

        # 4. Allocate ready tasks to free resources
        for task in ready_and_working_task_list:
            allocating_workers = list(
                filter(
                    lambda worker: worker.has_workamount_skill(task.name)
                    and self.__is_allocated(worker, task),
                    free_worker_list,
                )
            )
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
        team = list(
            filter(lambda team: team.ID == worker.team_id, self.organization.team_list)
        )[0]
        return task in team.targeted_task_list

    def is_business_time(
        self,
        target_datetime: datetime.datetime,
        weekend_working=True,
        work_start_hour=None,
        work_finish_hour=None,
    ):
        """
        Check whether target_datetime is business time or not in thip project.

        Args:
            target_datetime (datetime.datetime):
                Target datetime of checking business time or not.
            weekend_working (bool, optional):
                Whether worker works in weekend or not.
                Defaults to True.
            work_start_hour (int, optional):
                Starting working hour in one day .
                Defaults to None. This means workers work every timw.
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
        finish_margin=0.9,
        save_fig_path=None,
    ):
        """
        Method for creating Gantt chart by plotly.
        This method will be used after simulation.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulattion
            title (str, optional):
                Title of Gantt chart.
                Defaults to "Gantt Chart".
            colors (Dict[str, str], optional):
                Color setting of plotly Gantt chart.
                Defaults to None -> dict(Worker="rgb(46, 137, 205)").
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
                Defaults to 0.9.
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
        # if save_fig_path is not None:
        #     plotly.io.write_image(fig, save_fig_path)

        return fig

    def get_networkx_graph(self, view_workers=False):
        """
        Get the information of networkx graph.

        Args:
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
        Returns:
            G: networkx.Digraph()
        """
        Gp = self.product.get_networkx_graph()
        Gw = self.workflow.get_networkx_graph()
        Go = self.organization.get_networkx_graph(view_workers=view_workers)
        G = nx.compose_all([Gp, Gw, Go])

        # add edge between product and workflow
        for c in self.product.component_list:
            for task in c.targeted_task_list:
                G.add_edge(c, task)

        # add edge between workflow and organization
        for team in self.organization.team_list:
            for task in team.targeted_task_list:
                G.add_edge(team, task)

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        with_labels=True,
        view_workers=False,
        **kwds,
    ):
        """
        Draw networx

        Args:
            G (networkx.Digraph, optional):
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
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """

        G = G if G is not None else self.get_networkx_graph(view_workers=view_workers)
        pos = pos if pos is not None else nx.spring_layout(G)

        # Node
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.product.component_list,
            node_color="orangered",
        )
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=self.workflow.task_list,
            node_color="lime",
        )
        nx.draw_networkx_nodes(
            G, pos, with_labels=with_labels, nodelist=self.organization.team_list
        )
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)

    def get_node_and_edge_trace_for_ploty_network(self, G=None, pos=None, node_size=20):
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

        Returns:
            p_node_trace: BaseProduct nodes information of plotly network.
            o_node_trace: BaseOrganization nodes information of plotly network.
            w_node_trace: BaseWorkflow nodes information of plotly network.
            edge_trace: Edge information of plotly network.
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

        p_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(color="rgb(246, 37, 105)", size=node_size,),
        )

        w_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(color="rgb(146, 237, 5)", size=node_size,),
        )

        o_node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(color="rgb(46, 137, 205)", size=node_size,),
        )

        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0, color="#888"), hoverinfo="none", mode="lines"
        )

        for node in G.nodes:
            x, y = pos[node]
            if isinstance(node, BaseComponent):
                p_node_trace["x"] = p_node_trace["x"] + (x,)
                p_node_trace["y"] = p_node_trace["y"] + (y,)
                p_node_trace["text"] = p_node_trace["text"] + (node,)
            elif isinstance(node, BaseTask):
                w_node_trace["x"] = w_node_trace["x"] + (x,)
                w_node_trace["y"] = w_node_trace["y"] + (y,)
                w_node_trace["text"] = w_node_trace["text"] + (node,)
            elif isinstance(node, BaseTeam):
                o_node_trace["x"] = o_node_trace["x"] + (x,)
                o_node_trace["y"] = o_node_trace["y"] + (y,)
                o_node_trace["text"] = o_node_trace["text"] + (node,)

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace["x"] += (xposx, yposx)
            edge_trace["y"] += (xposy, yposy)

        return p_node_trace, w_node_trace, o_node_trace, edge_trace

    def draw_plotly_network(
        self,
        G=None,
        pos=None,
        title="Project",
        node_size=20,
        view_workers=False,
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
            view_workers (bool, optional):
                Including workers in networkx graph or not.
                Default to False.
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network

        TODO:
            Saving figure file is not implemented...
        """
        G = G if G is not None else self.get_networkx_graph(view_workers=view_workers)
        pos = pos if pos is not None else nx.spring_layout(G)
        (
            p_node_trace,
            w_node_trace,
            o_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_ploty_network(G, pos, node_size=node_size)
        fig = go.Figure(
            data=[edge_trace, p_node_trace, w_node_trace, o_node_trace],
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
        # if save_fig_path is not None:
        #     plotly.io.write_image(fig, save_fig_path)

        return fig

    def read_pDESy_web_json(self, file_path: str, encoding=None):
        """
        Read json file from pDESy.org.
        This method is not stable now.

        Args:
            file_path (str):
                file path by getting pDESy.org
            encoding ([type], optional):
                Defaults to None -> utf-8.
        TODO:
            pDESy.org for describing project in web browser should be developed...
        """
        encoding = encoding if encoding is not None else "utf-8"
        pdes_json = open(file_path, "r", encoding=encoding)
        data = json.load(pdes_json)

        # Get Product information including Components without dependency
        cd_list = list(filter(lambda node: node["type"] == "Component", data))
        component_list = [
            BaseComponent(
                cd["name"],
                ID=cd["id"],
                error_tolerance=float(cd["userData"]["errorTolerance"]),
            )
            for cd in cd_list
        ]

        # Get Workflow information including Tasks without dependency
        td_list = list(filter(lambda node: node["type"] == "Task", data))
        task_list = [
            BaseTask(
                td["name"],
                ID=td["id"],
                default_work_amount=float(td["userData"]["workAmount"]),
                default_progress=float(td["userData"]["progress"]),
                additional_work_amount=float(td["userData"]["additionalWorkAmount"]),
            )
            for td in td_list
        ]

        # Get Organization information including Teams without dependency
        team_list = []
        ted_list = list(filter(lambda node: node["type"] == "Team", data))
        for team_data in ted_list:
            worker_list = []
            worker_list_data = team_data["userData"]["WorkerList"]
            if type(worker_list_data["Worker"]) is dict:
                worker_list_data["Worker"] = [worker_list_data["Worker"]]
            for worker_data in worker_list_data["Worker"]:
                work_amount_skill_mean_info = {}
                work_amount_skill_sd_info = {}
                quality_skill_mean_info = {}
                # quality_skill_sd_info = {}
                if "WorkAmountSkill" in worker_data:
                    if type(worker_data["WorkAmountSkill"]) is list:
                        for skill_data in worker_data["WorkAmountSkill"]:
                            work_amount_skill_mean_info[skill_data["-name"]] = float(
                                skill_data["-value"]
                            )
                            work_amount_skill_sd_info[skill_data["-name"]] = float(
                                skill_data["-value_sd"]
                            )
                    elif type(worker_data["WorkAmountSkill"]) is dict:
                        work_amount_skill_mean_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value"])
                        work_amount_skill_sd_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
                # if "QualitySkill" in worker_data:
                #     if type(worker_data["QualitySkill"]) is list:
                #         for skill_data in worker_data["QualitySkill"]:
                #             quality_skill_mean_info[skill_data["-name"]] = float(
                #                 skill_data["-value"]
                #             )
                #             # quality_skill_sd_info[skill_data['-name']] =
                #             # float(skill_data['-value_sd'])
                #     elif type(worker_data["QualitySkill"]) is dict:
                #         quality_skill_mean_info[
                #             worker_data["QualitySkill"]["-name"]
                #         ] = float(worker_data["QualitySkill"]["-value"])
                #         # quality_skill_sd_info[worker_data['QualitySkill']['-name']]=
                #         # float(worker_data['QualitySkill']['-value_sd'])
                worker_list.append(
                    BaseResource(
                        worker_data["Name"],
                        team_id=team_data["id"],
                        cost_per_time=float(worker_data["Cost"]),
                        workamount_skill_mean_map=work_amount_skill_mean_info,
                        workamount_skill_sd_map=work_amount_skill_sd_info,
                        quality_skill_mean_map=quality_skill_mean_info,
                    )
                )
            team_list.append(
                BaseTeam(team_data["name"], ID=team_data["id"], worker_list=worker_list)
            )

        # Get Links information including
        # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
        l_list = list(filter(lambda node: node["type"] == "draw2d.Connection", data))
        for link in l_list:
            org_id = link["source"]["node"]
            org_type = list(filter(lambda node: node["id"] == org_id, data))[0]["type"]
            dst_id = link["target"]["node"]
            dst_type = list(filter(lambda node: node["id"] == dst_id, data))[0]["type"]
            if org_type == "Component" and dst_type == "Component":
                org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
                dst_c = list(filter(lambda c: c.ID == dst_id, component_list))[0]
                org_c.parent_component_list.append(dst_c)
                dst_c.child_component_list.append(org_c)
            elif org_type == "Task" and dst_type == "Task":
                org_task = list(filter(lambda c: c.ID == org_id, task_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_task.output_task_list.append(dst_task)
                dst_task.input_task_list.append(org_task)
            elif org_type == "Team" and dst_type == "Team":
                org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
                dst_team = list(filter(lambda c: c.ID == dst_id, team_list))[0]
                # org_task.output_task_id_list.append(dst_task.ID)
                dst_team.parent_team_id = org_team.ID
            elif org_type == "Component" and dst_type == "Task":
                org_c = list(filter(lambda c: c.ID == org_id, component_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_c.targeted_task_list.append(dst_task)
                dst_task.target_component_list.append(org_c)
            elif org_type == "Team" and dst_type == "Task":
                org_team = list(filter(lambda c: c.ID == org_id, team_list))[0]
                dst_task = list(filter(lambda c: c.ID == dst_id, task_list))[0]
                org_team.targeted_task_list.append(dst_task)
                dst_task.allocated_team_list.append(org_team)

        # Aggregate
        self.product = BaseProduct(component_list)
        self.workflow = BaseWorkflow(task_list)
        self.organization = BaseOrganization(team_list)

    def read_pDES_json(self, file_path: str, encoding=None):
        """
        Read json file converted from pDES file.
        This method is not stable now.

        Args:
            file_path (str):
                file path by getting pDES and converted to json
            encoding ([type], optional):
                Defaults to None -> utf-8.
        """
        encoding = encoding if encoding is not None else "utf-8"
        pdes_json = open(file_path, "r", encoding=encoding)
        data = json.load(pdes_json)

        # Get Product information including Components without dependency
        cd_list = data["ProjectDiagram"]["NodeElementList"]["ComponentNode"]
        component_list = [
            BaseComponent(
                cd["Name"], ID=cd["-id"],  # error_tolerance=float(cd["ErrorTolerance"])
            )
            for cd in cd_list
        ]

        # Get Workflow information including Tasks without dependency
        td_list = data["ProjectDiagram"]["NodeElementList"]["TaskNode"]
        task_list = [
            BaseTask(
                td["Name"],
                ID=td["-id"],
                default_work_amount=float(td["WorkAmount"]),
                default_progress=float(td["Progress"]),
                # additional_work_amount=float(td["AdditionalWorkAmount"]),
            )
            for td in td_list
        ]

        # Get Organization information including Teams without dependency
        team_list = []
        ted_list = data["ProjectDiagram"]["NodeElementList"]["TeamNode"]
        for team_data in ted_list:
            worker_list = []
            worker_list_data = team_data["WorkerList"]
            if type(worker_list_data["Worker"]) is dict:
                worker_list_data["Worker"] = [worker_list_data["Worker"]]
            for worker_data in worker_list_data["Worker"]:
                work_amount_skill_mean_info = {}
                work_amount_skill_sd_info = {}
                quality_skill_mean_info = {}
                # quality_skill_sd_info = {}
                if "WorkAmountSkill" in worker_data:
                    if type(worker_data["WorkAmountSkill"]) is list:
                        for skill_data in worker_data["WorkAmountSkill"]:
                            work_amount_skill_mean_info[skill_data["-name"]] = float(
                                skill_data["-value"]
                            )
                            work_amount_skill_sd_info[skill_data["-name"]] = float(
                                skill_data["-value_sd"]
                            )
                    elif type(worker_data["WorkAmountSkill"]) is dict:
                        work_amount_skill_mean_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value"])
                        work_amount_skill_sd_info[
                            worker_data["WorkAmountSkill"]["-name"]
                        ] = float(worker_data["WorkAmountSkill"]["-value_sd"])
                # if "QualitySkill" in worker_data:
                #     if type(worker_data["QualitySkill"]) is list:
                #         for skill_data in worker_data["QualitySkill"]:
                #             quality_skill_mean_info[skill_data["-name"]] = float(
                #                 skill_data["-value"]
                #             )
                #             # quality_skill_sd_info[skill_data['-name']]
                #             #  = float(skill_data['-value_sd'])
                #     elif type(worker_data["QualitySkill"]) is dict:
                #         quality_skill_mean_info[
                #             worker_data["QualitySkill"]["-name"]
                #         ] = float(worker_data["QualitySkill"]["-value"])
                #         # quality_skill_sd_info[worker_data['QualitySkill']['-name']]
                #         #  = float(worker_data['QualitySkill']['-value_sd'])
                worker_list.append(
                    BaseResource(
                        worker_data["Name"],
                        team_id=team_data["-id"],
                        cost_per_time=float(worker_data["Cost"]),
                        workamount_skill_mean_map=work_amount_skill_mean_info,
                        workamount_skill_sd_map=work_amount_skill_sd_info,
                        quality_skill_mean_map=quality_skill_mean_info,
                    )
                )
            team_list.append(
                BaseTeam(
                    team_data["Name"], ID=team_data["-id"], worker_list=worker_list
                )
            )
        self.organization = BaseOrganization(team_list)

        # Get Links information including
        # ComponentLink, TaskLink, TeamLink(yet), TargetComponentLink, AllocationLink
        l_list = data["ProjectDiagram"]["LinkList"]["Link"]
        for link in l_list:
            if link["-type"] == "ComponentLink":
                org_c = list(filter(lambda c: c.ID == link["-org"], component_list))[0]
                dst_c = list(filter(lambda c: c.ID == link["-dst"], component_list))[0]
                org_c.parent_component_list.append(dst_c)
                dst_c.child_component_list.append(org_c)
            elif link["-type"] == "TaskLink":
                org_task = list(filter(lambda c: c.ID == link["-org"], task_list))[0]
                dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
                org_task.output_task_list.append(dst_task)
                dst_task.input_task_list.append(org_task)
            elif link["-type"] == "TeamLink":
                org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
                dst_team = list(filter(lambda c: c.ID == link["-dst"], team_list))[0]
                # org_task.output_task_id_list.append(dst_task.ID)
                dst_team.get_work_amount_skill_progress_team_id = org_team.ID
            elif link["-type"] == "TargetComponentLink":
                org_c = list(filter(lambda c: c.ID == link["-org"], component_list))[0]
                dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
                org_c.targeted_task_list.append(dst_task)
                dst_task.target_component_list.append(org_c)
            elif link["-type"] == "AllocationLink":
                org_team = list(filter(lambda c: c.ID == link["-org"], team_list))[0]
                dst_task = list(filter(lambda c: c.ID == link["-dst"], task_list))[0]
                org_team.targeted_task_list.append(dst_task)
                dst_task.allocated_team_list.append(org_team)

        # Aggregate
        self.product = BaseProduct(component_list)
        self.workflow = BaseWorkflow(task_list)
        self.organization = BaseOrganization(team_list)
