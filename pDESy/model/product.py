#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_component import BaseComponent
from .base_product import BaseProduct
from typing import List


class Product(BaseProduct):
    """BaseProduct
    Product class for expressing target product in a project.
    This class is implemented from BaseProduct.

    Args:
        component_list (List[BaseComponent]):
            List of BaseComponents
    """

    def __init__(self, component_list: List[BaseComponent]):
        super().__init__(component_list)
