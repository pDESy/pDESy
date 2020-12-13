#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_task import BaseTask, BaseTaskState, BaseTaskDependency
from .base_resource import BaseResourceState
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go
import datetime
import matplotlib.pyplot as plt


class BaseWorkflow(object, metaclass=abc.ABCMeta):
    """BaseWorkflow
    BaseWorkflow class for expressing workflow in a project.
    BaseWorkflow is consist of multiple BaseTasks.
    This class will be used as template.

    Args:
        task_list (List[BaseTask]):
            Basic parameter.
            List of BaseTask in this BaseWorkflow.
        critical_path_length (float, optional):
            Basic variable.
            Critical path length of PERT/CPM.
            Defaults to 0.0.
    """

    def __init__(
        self,
        # Basic parameters
        task_list: List[BaseTask],
        # Basic variables
        critical_path_length=0.0,
    ):
        # ----
        # Constraint parameter on simulation
        # --
        # Basic parameter
        self.task_list = task_list

        # ----
        # Changeable variable on simulation
        # --
        # Basic variables
        self.critical_path_length = (
            critical_path_length if critical_path_length != 0.0 else 0.0
        )

    def __str__(self):
        """
        Returns:
            str: name list of BaseTask
        Examples:
            >>> w = BaseWorkflow([BaseTask('t1')])
            >>> print([t.name for t in w.task_list])
            ['t1']
        """
        return "{}".format(list(map(lambda task: str(task), self.task_list)))

    def initialize(self):
        """
        Initialize the changeable variables of BaseWorkflow including PERT calculation.

        - changeable variables of BaseTask in task_list
        - critical_path_length
        """
        for task in self.task_list:
            task.initialize()
        self.critical_path_length = 0.0
        self.update_PERT_data(0)
        self.check_state(-1, BaseTaskState.READY)

    def record_allocated_workers_facilities_id(self):
        for task in self.task_list:
            task.record_allocated_workers_facilities_id()

    def update_PERT_data(self, time: int):
        """
        Update PERT data (est,eft,lst,lft) of each BaseTask in task_list

        Args:
            time (int):
                Simulation time.
        """
        self.__set_est_eft_data(time)
        self.__set_lst_lft_criticalpath_data(time)

    def check_state(self, time: int, state: BaseTaskState):
        """
        Check state of all BaseTasks in task_list

        Args:
            time (int):
                Simulation time
            state (BaseTaskState):
                Check target state.
                Search and update all tasks which can change only target state.
        """
        if state == BaseTaskState.READY:
            self.__check_ready(time)
        elif state == BaseTaskState.WORKING:
            self.__check_working(time)
        elif state == BaseTaskState.FINISHED:
            self.__check_finished(time)

    def __check_ready(self, time: int):
        none_task_list = list(
            filter(lambda task: task.state == BaseTaskState.NONE, self.task_list)
        )
        for none_task in none_task_list:
            input_task_list = none_task.input_task_list

            # check READY condition by each dependency
            # FS: if input task is finished
            # SS: if input task is started
            # ...or this is head task
            ready = True
            for input_task, dependency in input_task_list:
                if dependency == BaseTaskDependency.FS:
                    if input_task.state == BaseTaskState.FINISHED:
                        ready = True
                    else:
                        ready = False
                        break
                elif dependency == BaseTaskDependency.SS:
                    if input_task.state == BaseTaskState.WORKING:
                        ready = True
                    else:
                        ready = False
                        break
                elif dependency == BaseTaskDependency.SF:
                    pass
                elif dependency == BaseTaskDependency.FF:
                    pass
            if ready:
                none_task.state = BaseTaskState.READY
                none_task.ready_time_list.append(time)

    def __check_working(self, time: int):
        ready_and_assigned_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.READY
                and len(task.allocated_worker_list) > 0,
                self.task_list,
            )
        )

        ready_auto_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.READY and task.auto_task,
                self.task_list,
            )
        )

        working_and_assigned_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.WORKING
                and len(task.allocated_worker_list) > 0,
                self.task_list,
            )
        )

        target_task_list = []
        target_task_list.extend(ready_and_assigned_task_list)
        target_task_list.extend(ready_auto_task_list)
        target_task_list.extend(working_and_assigned_task_list)

        for task in target_task_list:
            if task.state == BaseTaskState.READY:
                task.state = BaseTaskState.WORKING
                task.start_time_list.append(time)
                for worker in task.allocated_worker_list:
                    worker.state = BaseResourceState.WORKING
                    worker.start_time_list.append(time)
                    worker.assigned_task_list.append(task)
                if task.need_facility:
                    for facility in task.allocated_facility_list:
                        facility.state = BaseResourceState.WORKING
                        facility.start_time_list.append(time)
                        facility.assigned_task_list.append(task)

            elif task.state == BaseTaskState.WORKING:
                for worker in task.allocated_worker_list:
                    if worker.state == BaseResourceState.FREE:
                        worker.state = BaseResourceState.WORKING
                        worker.start_time_list.append(time)
                        worker.assigned_task_list.append(task)
                    if task.need_facility:
                        for facility in task.allocated_facility_list:
                            if facility.state == BaseResourceState.FREE:
                                facility.state = BaseResourceState.WORKING
                                facility.start_time_list.append(time)
                                facility.assigned_task_list.append(task)

    def __check_finished(self, time: int, error_tol=1e-10):
        working_and_zero_task_list = list(
            filter(
                lambda task: task.state == BaseTaskState.WORKING
                and task.remaining_work_amount < 0.0 + error_tol,
                self.task_list,
            )
        )
        for task in working_and_zero_task_list:
            # check FINISH condition by each dependency
            # SF: if input task is working
            # FF: if input task is finished
            finished = True
            for input_task, dependency in task.input_task_list:
                if dependency == BaseTaskDependency.FS:
                    pass
                elif dependency == BaseTaskDependency.SS:
                    pass
                elif dependency == BaseTaskDependency.SF:
                    if input_task.state == BaseTaskState.WORKING:
                        finished = True
                    else:
                        finished = False
                        break
                elif dependency == BaseTaskDependency.FF:
                    if input_task.state == BaseTaskState.FINISHED:
                        finished = True
                    else:
                        finished = False
                        break
            if finished:
                task.state = BaseTaskState.FINISHED
                task.finish_time_list.append(time)
                task.remaining_work_amount = 0.0

                for worker in task.allocated_worker_list:
                    if all(
                        list(
                            map(
                                lambda task: task.state == BaseTaskState.FINISHED,
                                worker.assigned_task_list,
                            )
                        )
                    ):
                        worker.state = BaseResourceState.FREE
                        worker.finish_time_list.append(time)
                        worker.assigned_task_list.remove(task)
                task.allocated_worker_list = []

                if task.need_facility:
                    for facility in task.allocated_facility_list:
                        if all(
                            list(
                                map(
                                    lambda task: task.state == BaseTaskState.FINISHED,
                                    facility.assigned_task_list,
                                )
                            )
                        ):
                            facility.state = BaseResourceState.FREE
                            facility.finish_time_list.append(time)
                            facility.assigned_task_list.remove(task)

                    task.allocated_facility_list = []

    def __set_est_eft_data(self, time: int):

        input_task_list = []

        # 1. Set the earliest finish time of head tasks.
        for task in self.task_list:
            task.est = time
            if len(task.input_task_list) == 0:
                task.eft = time + task.remaining_work_amount
                input_task_list.append(task)

        # 2. Calculate PERT information of all tasks
        while len(input_task_list) > 0:
            next_task_list = []
            for input_task in input_task_list:
                for next_task, dependency in input_task.output_task_list:
                    pre_est = next_task.est
                    est = 0
                    eft = 0
                    if dependency == BaseTaskDependency.FS:
                        est = input_task.est + input_task.remaining_work_amount
                        eft = est + next_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.SS:
                        est = input_task.est + 0
                        eft = est + next_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.FF:
                        est = input_task.est + 0
                        eft = est + next_task.remaining_work_amount
                        if input_task.eft > eft:
                            eft = input_task.eft
                    elif dependency == BaseTaskDependency.SF:
                        est = input_task.est + 0
                        eft = est + next_task.remaining_work_amount
                        if input_task.est > eft:
                            eft = input_task.est
                    else:
                        est = input_task.est + input_task.remaining_work_amount
                        eft = est + next_task.remaining_work_amount
                    if est >= pre_est:
                        next_task.est = est
                        next_task.eft = eft
                    next_task_list.append(next_task)

            input_task_list = next_task_list

    def __set_lst_lft_criticalpath_data(self, time: int):

        # 1. Extract the list of tail tasks.
        output_task_list = list(
            filter(lambda task: len(task.output_task_list) == 0, self.task_list)
        )

        # 2. Update the information of critical path of this workflow.
        self.critical_path_length = max(output_task_list, key=lambda task: task.eft).eft
        for task in output_task_list:
            task.lft = self.critical_path_length
            task.lst = task.lft - task.remaining_work_amount

        # 3. Calculate PERT information of all tasks
        while len(output_task_list) > 0:

            prev_task_list = []
            for output_task in output_task_list:
                for prev_task, dependency in output_task.input_task_list:
                    pre_lft = prev_task.lft
                    lst = 0
                    lft = 0
                    if dependency == BaseTaskDependency.FS:
                        lft = output_task.lst
                        lst = lft - prev_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.SS:
                        lst = output_task.lst
                        lft = lst + prev_task.remaining_work_amount
                    elif dependency == BaseTaskDependency.FF:
                        lst = output_task.lst
                        lft = lst + prev_task.remaining_work_amount
                        if output_task.lft < lft:
                            lft = output_task.lft
                    elif dependency == BaseTaskDependency.SF:
                        lst = output_task.lst
                        lft = lst + prev_task.remaining_work_amount
                        if output_task.lft < lst:
                            lst = output_task.lft
                    else:
                        lft = output_task.lst
                        lst = lft - prev_task.remaining_work_amount
                    if pre_lft < 0 or pre_lft >= lft:
                        prev_task.lst = lst
                        prev_task.lft = lft
                    prev_task_list.append(prev_task)

            output_task_list = prev_task_list

    def reverse_dependencies(self):
        """
        Reverse all task dependencies in task_list.

        Note:
            This method is developed only for backward simulation.
        """
        # 1.
        # Register the input_task_list to dummy_output_task_list
        # Register the output_task_list to dummy_input_task_list
        for task in self.task_list:
            task.dummy_output_task_list = task.input_task_list
            task.dummy_input_task_list = task.output_task_list

        # 2.
        # Register the dummy_output_task_list to output_task_list
        # Register the dummy_input_task_list to input_task_list
        # Delete the dummy_output_task_list, dummy_input_task_list
        for task in self.task_list:
            task.output_task_list = task.dummy_output_task_list
            task.input_task_list = task.dummy_input_task_list
            del task.dummy_output_task_list, task.dummy_input_task_list

    def perform(self, time: int, seed=None):
        """
        Perform BaseTask in task_list in simulation.

        Args:
            time (int):
                Simulation time.
            seed (int, optional):
                Random seed for describing deviation of progress.
                If workamount
                Defaults to None.
        Note:
            This method includes advanced code of custom simulation.
            We have to separete basic code and advanced code in the future.
        """
        for task in self.task_list:
            task.perform(time, seed=seed)

    def create_simple_gantt(
        self,
        finish_margin=1.0,
        view_auto_task=False,
        view_ready=False,
        task_color="#00EE00",
        auto_task_color="#005500",
        ready_color="#C0C0C0",
        save_fig_path=None,
    ):
        """

        Method for creating Gantt chart by matplotlib.
        In this Gantt chart, datetime information is not included.
        This method will be used after simulation.

        Args:
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            view_auto_task (bool, optional):
                View auto_task or not.
                Defaults to False.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.
            task_color (str, optional):
                Task color setting information.
                Defaults to "#00EE00".
            auto_task_color (str, optional):
                Auto Task color setting information.
                Defaults to "#005500".
            ready_color (str, optional):
                Ready Task color setting information.
                Defaults to "#C0C0C0".
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            fig: fig in plt.subplots()
            gnt: gnt in plt.subplots()
        """
        fig, gnt = plt.subplots()
        gnt.set_xlabel("step")
        gnt.grid(True)

        target_task_list = list(filter(lambda task: not task.auto_task, self.task_list))
        if view_auto_task:
            target_task_list = self.task_list

        yticks = [10 * (n + 1) for n in range(len(target_task_list))]
        yticklabels = [task.name for task in target_task_list]

        gnt.set_yticks(yticks)
        gnt.set_yticklabels(yticklabels)

        for ttime in range(len(target_task_list)):
            task = target_task_list[ttime]
            wlist = []  # time list from start to finish+finish_margin
            rlist = []  # time list from ready to start
            for wtime in range(len(task.start_time_list)):
                wlist.append(
                    (
                        task.start_time_list[wtime],
                        task.finish_time_list[wtime]
                        - task.start_time_list[wtime]
                        + finish_margin,
                    )
                )
                rlist.append(
                    (
                        task.ready_time_list[wtime] + finish_margin,
                        task.start_time_list[wtime] - task.ready_time_list[wtime],
                    )
                )
            if task.auto_task:
                if view_ready:
                    gnt.broken_barh(
                        rlist, (yticks[ttime] - 5, 9), facecolors=(ready_color)
                    )
                gnt.broken_barh(
                    wlist, (yticks[ttime] - 5, 9), facecolors=(auto_task_color)
                )
            else:
                if view_ready:
                    gnt.broken_barh(
                        rlist, (yticks[ttime] - 5, 9), facecolors=(ready_color)
                    )
                gnt.broken_barh(wlist, (yticks[ttime] - 5, 9), facecolors=(task_color))

        if save_fig_path is not None:
            plt.savefig(save_fig_path)

        return fig, gnt

    def create_data_for_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        finish_margin=1.0,
        view_ready=False,
    ):
        """
        Create data for gantt plotly
        from task_list.

        Args:
            init_datetime (datetime.datetime):
                Start datetime of project
            unit_timedelta (datetime.timedelta):
                Unit time of simulation
            finish_margin (float, optional):
                Margin of finish time in Gantt chart.
                Defaults to 1.0.
            view_ready (bool, optional):
                View READY time or not.
                Defaults to False.

        Returns:
            list[dict]: Gantt plotly information of this BaseWorkflow
        """
        df = []
        for task in self.task_list:
            df.extend(
                task.create_data_for_gantt_plotly(
                    init_datetime,
                    unit_timedelta,
                    finish_margin=finish_margin,
                    view_ready=view_ready,
                )
            )
        return df

    def create_gantt_plotly(
        self,
        init_datetime: datetime.datetime,
        unit_timedelta: datetime.timedelta,
        title="Gantt Chart",
        colors=None,
        index_col=None,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=True,
        show_colorbar=True,
        finish_margin=1.0,
        view_ready=False,
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
                Defaults to None ->
                dict(WORKING="rgb(146, 237, 5)", READY="rgb(107, 127, 135)").
            index_col (str, optional):
                index_col of plotly Gantt chart.
                Defaults to None -> "State".
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
            else dict(WORKING="rgb(146, 237, 5)", READY="rgb(107, 127, 135)")
        )
        index_col = index_col if index_col is not None else "State"
        df = self.create_data_for_gantt_plotly(
            init_datetime,
            unit_timedelta,
            finish_margin=finish_margin,
            view_ready=view_ready,
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

    def get_networkx_graph(self):
        """
        Get the information of networkx graph.

        Returns:
            G: networkx.Digraph()
        """
        G = nx.DiGraph()

        # 1. add all nodes
        for task in self.task_list:
            G.add_node(task)

        # 2. add all edges
        for task in self.task_list:
            for input_task, dependency in task.input_task_list:
                G.add_edge(input_task, task)

        return G

    def draw_networkx(
        self,
        G=None,
        pos=None,
        arrows=True,
        with_labels=True,
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
        **kwds,
    ):
        """
        Draw networkx

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
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            **kwds:
                another networkx settings.
        Returns:
            figure: Figure for a network
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)
        # nx.draw_networkx(G, pos=pos, arrows=arrows, with_labels=with_labels, **kwds)

        # normal task
        normal_task_list = [task for task in self.task_list if not task.auto_task]
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=normal_task_list,
            node_color=task_node_color,
            # **kwds,
        )

        # auto task
        auto_task_list = [task for task in self.task_list if task.auto_task]
        nx.draw_networkx_nodes(
            G,
            pos,
            with_labels=with_labels,
            nodelist=auto_task_list,
            node_color=auto_task_node_color,
            # **kwds,
        )

        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)

    def get_node_and_edge_trace_for_plotly_network(
        self,
        G=None,
        pos=None,
        node_size=20,
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
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
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".

        Returns:
            task_node_trace: Normal Task Node information of plotly network.
            auto_task_node_trace: Auto Task Node information of plotly network.
            edge_trace: Edge information of plotly network.
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

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

        for node in G.nodes:
            x, y = pos[node]
            if not node.auto_task:
                task_node_trace["x"] = task_node_trace["x"] + (x,)
                task_node_trace["y"] = task_node_trace["y"] + (y,)
                task_node_trace["text"] = task_node_trace["text"] + (node,)
            elif node.auto_task:
                auto_task_node_trace["x"] = auto_task_node_trace["x"] + (x,)
                auto_task_node_trace["y"] = auto_task_node_trace["y"] + (y,)
                auto_task_node_trace["text"] = auto_task_node_trace["text"] + (node,)

        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=1, color="#888"), hoverinfo="none", mode="lines"
        )

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace["x"] += (xposx, yposx)
            edge_trace["y"] += (xposy, yposy)

        return task_node_trace, auto_task_node_trace, edge_trace

    def draw_plotly_network(
        self,
        G=None,
        pos=None,
        title="Workflow",
        node_size=20,
        task_node_color="#00EE00",
        auto_task_node_color="#005500",
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
                Defaults to "Workflow".
            node_size (int, optional):
                Node size setting information.
                Defaults to 20.
            task_node_color (str, optional):
                Node color setting information.
                Defaults to "#00EE00".
            auto_task_node_color (str, optional):
                Node color setting information.
                Defaults to "#005500".
            save_fig_path (str, optional):
                Path of saving figure.
                Defaults to None.

        Returns:
            figure: Figure for a network

        TODO:
            Saving figure file is not implemented...
        """
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)
        (
            task_node_trace,
            auto_task_node_trace,
            edge_trace,
        ) = self.get_node_and_edge_trace_for_plotly_network(
            G,
            pos,
            node_size=node_size,
            task_node_color=task_node_color,
            auto_task_node_color=auto_task_node_color,
        )
        fig = go.Figure(
            data=[edge_trace, task_node_trace, auto_task_node_trace],
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
