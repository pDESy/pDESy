#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_component import BaseComponent


class Component(BaseComponent):
    def __init__(self, name: str, ID=None, error_tolerance=None):
        super().__init__(name, ID=ID, error_tolerance=error_tolerance)
