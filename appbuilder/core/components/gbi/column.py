#!/usr/bin/env python 3
# -*- coding: utf-8 -*-

#
# Copyright (c) 2023 PanXu, Inc. All Rights Reserved
#
"""
brief

Authors: PanXu
Date:    2023/12/23 20:43:00
"""
from typing import Dict


class ColumnItem(object):
    """
    column item
    """

    def __init__(self, ori_value: str, column_name: str, column_value: str,  table_name: str,
                 is_like: bool = False):
        """

        :param column_name:
        :param column_value:
        :param ori_value:
        :param is_like:
        """
        self.column_name = column_name
        self.column_value = column_value
        self.ori_value = ori_value
        self.table_name = table_name
        self.is_like = is_like

    def to_json(self) -> Dict:
        return self.__dict__



