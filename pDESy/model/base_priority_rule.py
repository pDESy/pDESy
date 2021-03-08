#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


class ResourcePriorityRule(IntEnum):
    """ResourcePriorityRule"""

    SSP = 0


class TaskPriorityRule(IntEnum):
    """TaskPriorityRule"""

    TSLACK = 0
