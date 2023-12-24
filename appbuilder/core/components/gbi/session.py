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


class Session(object):

    def __init__(self, session_id: str):
        self.records = list()
        self.session_id = session_id
