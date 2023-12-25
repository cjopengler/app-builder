#!/usr/bin/env python 3
# -*- coding: utf-8 -*-

#
# Copyright (c) 2023 PanXu, Inc. All Rights Reserved
#
"""
brief

Authors: PanXu
Date:    2023/12/23 20:07:00
"""

from typing import Dict, List


class NL2SqlResult(object):

    def __init__(self, llm_result: str, sql: str):
        self.llm_result = llm_result
        self.sql = sql

    def to_json(self) -> Dict:
        return self.__dict__


class GBISessionRecord(object):
    """
    gbi session record
    """

    def __init__(self, query: str, answer: NL2SqlResult):
        """

        Args:
            query:
            answer:
        """
        self.query = query
        self.answer = answer

    def to_json(self) -> Dict:
        return {"query": self.query,
                "answer": self.answer.to_json()}


class GBILocalSession(object):

    def __init__(self, session_id: str):
        self.records: List[GBISessionRecord] = list()
        self.session_id = session_id


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
