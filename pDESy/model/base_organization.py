#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_team import BaseTeam
import plotly
import plotly.figure_factory as ff
import networkx as nx

class BaseOrganization(object, metaclass=abc.ABCMeta):
    
    def __init__(self, team_list:List[BaseTeam]):
        # Constraint variables on simulation
        self.team_list = team_list
    
    def __str__(self):
        return '{}'.format(list(map(lambda team: str(team), self.team_list)))
        
    def initialize(self):
        for team in self.team_list:
            team.initialize()
    
    def add_labor_cost(self,only_working=True):
        for team in self.team_list:
            team.add_labor_cost(only_working=True)
    
    def create_data_for_gantt_plotly(self, init_datetime, unit_timedelta):
        df = []
        for team in self.team_list:
            df.extend(team.create_data_for_gantt_plotly(init_datetime, unit_timedelta))
        return df
    
    def create_gantt_plotly(self, init_datetime, unit_timedelta, title='Gantt Chart', colors=None, index_col=None, showgrid_x=True, showgrid_y=True, group_tasks=True, show_colorbar=True, save_fig_path=''):
        colors = colors if colors is not None else dict(Worker = 'rgb(46, 137, 205)')
        index_col = index_col if index_col is not None else 'Type'
        df = self.create_data_for_gantt_plotly(init_datetime, unit_timedelta)
        fig = ff.create_gantt(df, title=title, colors=colors, index_col=index_col, showgrid_x=showgrid_x, showgrid_y=showgrid_y, show_colorbar=show_colorbar, group_tasks=group_tasks)
        if save_fig_path != '': plotly.io.write_image(fig, save_fig_path)
        return fig
    
    def get_networkx_graph(self, view_workers=False):
        G = nx.DiGraph()
        
        # 1. add all nodes
        for team in self.team_list:
            G.add_node(team)
        
        # 2. add all edges
        for team in self.team_list:
            if team.superior_team != '': G.add_edge(team.superior_team, team)

        if view_workers:
            for team in self.team_list:
                for w in team.worker_list:
                    G.add_node(w)
                    G.add_edge(team, w)
                    
        return G
    
    def draw_networkx(self, G=None, pos=None, view_workers=False, arrows=True, with_labels=True, **kwds):
        G = G if G is not None else self.get_networkx_graph(view_workers)
        pos = pos if pos is not None else nx.spring_layout(G)
        nx.draw_networkx(G, pos=pos, arrows=arrows, with_labels=with_labels, **kwds)
