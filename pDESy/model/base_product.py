#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from typing import List
from .base_component import BaseComponent
import plotly
import plotly.figure_factory as ff

class BaseProduct(object, metaclass=abc.ABCMeta):
    
    def __init__(self, component_list:List[BaseComponent]):
        # Constraint variables on simulation
        self.component_list = component_list
        
    def initialize(self):
        for c in self.component_list:
            c.initialize()
    
    def __str__(self):
        return '{}'.format(list(map(lambda c: str(c), self.component_list)))
    
    def create_data_for_gantt_plotly(self, init_datetime, unit_timedelta):
        df = []
        for component in self.component_list:
            df.extend(component.create_data_for_gantt_plotly(init_datetime, unit_timedelta))
        return df
    
    def create_gantt_plotly(self, init_datetime, unit_timedelta, title='Gantt Chart', colors=None, index_col=None, showgrid_x=True, showgrid_y=True, group_tasks=True, show_colorbar=True, save_fig_path=''):
        colors = colors if colors is not None else dict(Component = 'rgb(246, 37, 105)')
        index_col = index_col if index_col is not None else 'Type'
        df = self.create_data_for_gantt_plotly(init_datetime, unit_timedelta)
        fig = ff.create_gantt(df, title=title, colors=colors, index_col=index_col, showgrid_x=showgrid_x, showgrid_y=showgrid_y, show_colorbar=show_colorbar, group_tasks=group_tasks)
        if save_fig_path != '': plotly.io.write_image(fig, save_fig_path)
        return fig