#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import datetime
import plotly
import plotly.figure_factory as ff
import networkx as nx

class BaseProject(object, metaclass=ABCMeta):
    
    def __init__(self, file_path='', init_datetime=None, unit_timedelta=None):
        
        # Constraint variables on simulation
        self.init_datetime = init_datetime if init_datetime is not None else datetime.datetime.now()
        self.unit_timedelta = unit_timedelta if unit_timedelta is not None else datetime.timedelta(minutes=1)
        
        # Changeable variables on simulation
        self.product = []
        self.organization = []
        self.workflow = []
        self.time = int(0)
    
    def __str__(self):
        return 'TIME: {}\nPRODUCT\n{}\n\nORGANIZATION\n{}\n\nWORKFLOW\n{}'.format(self.time, str(self.product), str(self.organization), str(self.workflow))
        
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def read_json(self,file_path:str):
        pass

    @abstractmethod
    def simulate(self, worker_perfoming_mode = 'single-task', task_performed_mode = 'multi-workers', error_tol = 1e-10, print_debug=False, weekend_working=True, max_time=10000):
        pass
    
    def is_business_time(self, datetime:datetime):
        if datetime.weekday() >= 5:
            return False
        else:
            return True

    def create_gantt_plotly(self, init_datetime, unit_timedelta, title='Gantt Chart', colors=None, index_col=None, showgrid_x=True, showgrid_y=True, group_tasks=False, show_colorbar=True, save_fig_path=''):
        colors = colors if colors is not None else dict(Component = 'rgb(246, 37, 105)', Task  = 'rgb(146, 237, 5)', Worker = 'rgb(46, 137, 205)', )
        index_col = index_col if index_col is not None else 'Type'
        df = []
        df.extend(
            self.product.create_data_for_gantt_plotly(init_datetime, unit_timedelta)
        )
        df.extend(
            self.workflow.create_data_for_gantt_plotly(init_datetime, unit_timedelta),
        )
        df.extend(
            self.organization.create_data_for_gantt_plotly(init_datetime, unit_timedelta)
        )
        fig = ff.create_gantt(df,title=title, colors=colors, index_col=index_col, showgrid_x=showgrid_x, showgrid_y=showgrid_y, show_colorbar=show_colorbar, group_tasks=group_tasks)
        if save_fig_path != '': plotly.io.write_image(fig, save_fig_path)
        return fig
    
    def get_networkx_graph(self):
        Gp = self.product.get_networkx_graph()
        Gw = self.workflow.get_networkx_graph()
        Go = self.organization.get_networkx_graph()
        G = nx.compose_all([Gp, Gw, Go])

        # add edge between product and workflow
        for c in self.product.component_list:
            for task in c.targeted_task_list:
                G.add_edge(c,task)
        
        # add edge between workflow and organization
        for team in self.organization.team_list:
            for task in team.targeted_task_list:
                G.add_edge(team,task)

        return G
    
    def draw_networkx(self, G=None, pos=None, arrows=True, with_labels=True, **kwds):
        G = G if G is not None else self.get_networkx_graph()
        pos = pos if pos is not None else nx.spring_layout(G)

        # Node
        nx.draw_networkx_nodes(G, pos, with_labels=with_labels, nodelist=self.product.component_list, node_color='orangered')
        nx.draw_networkx_nodes(G, pos, with_labels=with_labels, nodelist=self.workflow.task_list, node_color='lime')
        nx.draw_networkx_nodes(G, pos, with_labels=with_labels, nodelist=self.organization.team_list)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G,pos)