#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""product."""

from typing import List

from .base_component import BaseComponent
from .base_product import BaseProduct


class Product(BaseProduct):
    """BaseProduct.

    Product class for expressing target product in a project.
    This class is implemented from BaseProduct.

    Args:
        component_list (List[BaseComponent]):
            List of BaseComponents
    """

    def __init__(self, component_list: List[BaseComponent]):
        """init."""
        super().__init__(component_list)
