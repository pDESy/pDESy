#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_component import BaseComponent
from .base_product import BaseProduct
from typing import List

class Product(BaseProduct):
    
    def __init__(self, component_list:List[BaseComponent]):
        super().__init__(component_list)