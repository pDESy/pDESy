#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_team import BaseTeam
import plotly
import plotly.figure_factory as ff
import networkx as nx
import plotly.graph_objects as go

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
        cost_this_time = 0.0
        for team in self.team_list:
            cost_this_time += team.add_labor_cost(only_working=True)
        return cost_this_time
    
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
    
    def get_node_and_edge_trace_for_ploty_network(self, G, pos, node_size=20, node_color='rgb(46, 137, 205)'):
        node_trace = go.Scatter(
                    x = [],
                    y = [],
                    text = [],
                    mode = 'markers',
                    hoverinfo = 'text',
                    marker=dict(
                        color=node_color,
                        size=node_size,
                    )
                )

        for node in G.nodes:
            x, y = pos[node]
            node_trace['x'] = node_trace['x'] + (x,)
            node_trace['y'] = node_trace['y'] + (y,)
            node_trace['text'] = node_trace['text'] + (node,)

        edge_trace = go.Scatter(
            x = [],
            y = [],
            line = dict(width=1,color='#888'),
            hoverinfo='none',
            mode = 'lines'
        )

        for edge in G.edges:
            x = edge[0]
            y = edge[1]
            xposx, xposy = pos[x]
            yposx, yposy = pos[y]
            edge_trace['x'] += (xposx, yposx)
            edge_trace['y'] += (xposy, yposy)
        return node_trace, edge_trace

    def draw_plotly_network(self, G=None, pos=None, title='Organization', node_size=20, node_color='rgb(46, 137, 205)',view_workers=False, save_fig_path=''):
        G = G if G is not None else self.get_networkx_graph(view_workers=view_workers)
        pos = pos if pos is not None else nx.spring_layout(G)
        node_trace, edge_trace = self.get_node_and_edge_trace_for_ploty_network(G, pos ,node_size=node_size, node_color=node_color)
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=title,
                showlegend=False,
        #         hovermode='closest',
        #         margin=dict(b=20,l=5,r=5,t=40),
                annotations=[
                    dict(ax=edge_trace['x'][index*2], ay=edge_trace['y'][index*2], axref='x', ayref='y',
                        x=edge_trace['x'][index*2+1], y=edge_trace['y'][index*2+1], xref='x', yref='y',
                        showarrow=True, arrowhead=5,) for index in range(0, int(len(edge_trace['x']) / 2 ))
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        if save_fig_path != '': plotly.io.write_image(fig, save_fig_path)
        return fig
