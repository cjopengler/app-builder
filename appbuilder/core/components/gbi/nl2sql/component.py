# Copyright (c) 2023 Baidu, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""GBI nl2sql component.
"""
import uuid
import json
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from appbuilder.core.component import Component
from appbuilder.core.message import Message
from appbuilder.core.components.gbi.basic import GBISessionRecord
from appbuilder.core.components.gbi.basic import ColumnItem
from appbuilder.core.components.gbi.basic import NL2SqlResult
from appbuilder.core.components.gbi.basic import SUPPORTED_MODEL_NAME


class GBINL2Sql(Component):
    """
    gib nl2sql
    """

    def __init__(self, model_name: str, table_schemas: List[str], knowledge: Dict = None,
                 prompt_template: str = "",
                 secret_key: Optional[str] = None,
                 gateway: str = ""):
        """
        创建 gbi nl2sql 对象
        Args:
            model_name:  支持的模型名字 ERNIE-Bot 4.0, ERNIE-Bot-8K, ERNIE-Bot, ERNIE-Bot-turbo, EB-turbo-AppBuilder
            table_schemas: 表的 schema 列表，例如: ```
                            CREATE TABLE `mytable` (
                            `d_year` COMMENT '年度,2019,2020..2022..',
                            `industry` COMMENT '行业',
                            `project_name` COMMENT '项目名称',
                            `customer_name` COMMENT '客户名称')
                            ```"
            knowledge: 用于提供一些知识, 比如 {"毛利率": "毛收入-毛成本/毛成本"}
            prompt_template: prompt 模版, 必须包含的格式如下:
                  ***你的描述
                  {schema}
                  ***你的描述
                  {column_instrument}
                  ***你的描述
                  {kg}
                  ***你的描述
                  当前时间：{date}
                  ***你的描述
                  {history_instrument}
                  ***你的描述
                  当前问题：{query}
                  回答：
            secret_key: 用户创建的 key
            gateway: gateway 地址
        """
        super().__init__(secret_key=secret_key, gateway=gateway)

        if model_name not in SUPPORTED_MODEL_NAME:
            raise ValueError(f"model_name 错误， 请使用 {SUPPORTED_MODEL_NAME} 中的大模型")
        self.model_name = model_name
        self.server_sub_path = "/v1/ai_engine/gbi/v1/gbi_nl2sql"
        self.table_schemas = table_schemas
        self.knowledge = knowledge or dict()
        self.prompt_template = prompt_template

    def run(self,
            message: Message,
            session: List[GBISessionRecord],
            column_constraint: List[ColumnItem] = None) -> Message[NL2SqlResult]:
        """
        执行 nl2sql
        Args:
            message: message.content 是 query
            session: gbi session 的历史 列表
            column_constraint: 列选约束 参考 ColumnItem 具体定义
        Returns:
            NL2SqlResult 的 message
        """

        query = message.content
        session = session
        column_constraint = column_constraint or list()

        response = self._run_nl2sql(query=query, session=session, table_schemas=self.table_schemas,
                                    column_constraint=column_constraint, knowledge=self.knowledge,
                                    prompt_template=self.prompt_template,
                                    model_name=self.model_name,
                                    timeout=60,
                                    retry=2)

        rsp_data = response.json()
        nl2sql_result = NL2SqlResult(llm_result=rsp_data["llm_result"],
                                     sql=rsp_data["sql"])
        return Message(content=nl2sql_result)

    def _run_nl2sql(self, query: str, session: List[GBISessionRecord], table_schemas: List[str], knowledge: Dict[str, str],
                    prompt_template: str,
                    column_constraint: List[ColumnItem],
                    model_name: str,
                    timeout: float = None, retry: int = 0):
        """
        运行
        Args:
            query: query
            session: gbi session 的历史 列表
            table_schemas: 表的 schema 列表
            knowledge: 知识
            prompt_template: prompt 模版
            column_constraint: 列的限制
            model_name: 模型名字
            timeout: 超时时间
            retry:

        Returns:

        """

        headers = self.auth_header()
        headers["Content-Type"] = "application/json"

        if retry != self.retry.total:
            self.retry.total = retry

        payload = {"query": query,
                   "table_schemas": table_schemas,
                   "session": [session_record.to_json() for session_record in session],
                   "column_constraint": [column_item.to_json() for column_item in column_constraint],
                   "model_name": model_name,
                   "knowledge": knowledge,
                   "prompt_template": prompt_template}

        server_url = self.service_url(prefix="", sub_path=self.server_sub_path)
        response = self.s.post(url=server_url, headers=headers,
                               json=payload, timeout=timeout)
        super().check_response_header(response)
        data = response.json()
        super().check_response_json(data)

        request_id = self.response_request_id(response)
        response.request_id = request_id
        return response
