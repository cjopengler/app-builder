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

from appbuilder.core.component import Component, ComponentArguments
from appbuilder.core.message import Message
from appbuilder.core._exception import AppBuilderServerException
from appbuilder.core.components.gbi.session import Session
from appbuilder.core.components.gbi.column import ColumnItem


class NL2SqlResult(object):

    def __init__(self, llm_result: str, sql: str):
        self.llm_result = llm_result
        self.sql = sql

    def to_json(self) -> Dict:
        return self.__dict__


class GBINL2Sql(Component):
    """
    gib nl2sql
    """

    def __init__(self, model_name: str, table_schemas: List[str], knowledge: Dict = None,
                 secret_key: Optional[str] = None,
                 gateway: str = ""):
        super().__init__(secret_key=secret_key, gateway=gateway)
        self.model_name = model_name
        self.server_sub_path = "gbi_nl2sql"
        self.prefix = "/v1/"
        self.table_schemas = table_schemas
        self.knowledge = knowledge or dict()

    def run(self,
            message: Message,
            session: Session,
            column_constraint: List[ColumnItem] = None) -> Message[NL2SqlResult]:
        """

        :param message:
        :param session:
        :param column_constraint:
        :return:
        """

        query = message.content
        session = session
        column_constraint = column_constraint or list()

        response = self._run_nl2sql(query=query, session=session, table_schemas=self.table_schemas,
                                    column_constraint=column_constraint, knowledge=self.knowledge,
                                    model_name=self.model_name,
                                    timeout=100,
                                    retry=2)

        rsp_data = response.json()
        nl2sql_result = NL2SqlResult(llm_result=rsp_data["llm_result"],
                                     sql=rsp_data["sql"])
        return Message(content=nl2sql_result)

    def _run_nl2sql(self, query: str, session: Session, table_schemas: List[str], knowledge: Dict[str, str],
                    column_constraint: List[ColumnItem],
                    model_name: str,
                    timeout: float = None, retry: int = 0):
        """
        使用给定的输入并返回语音识别的结果。

        参数:
            request (obj:`ShortSpeechRecognitionRequest`): 输入请求，这是一个必需的参数。
            timeout (float, 可选): 请求的超时时间。
            retry (int, 可选): 请求的重试次数。

        返回:
            obj:`ShortSpeechRecognitionResponse`: 接口返回的输出消息。
        """

        headers = self.auth_header()
        headers["Content_Type"] = "application/json"

        if retry != self.retry.total:
            self.retry.total = retry

        payload = {"query": query,
                   "table_schemas": table_schemas,
                   "session": list(),
                   "column_constraint": [column_item.to_json() for column_item in column_constraint],
                   "model_name": model_name,
                   "knowledge": knowledge}

        server_url = self.service_url(prefix=self.prefix, sub_path=self.server_sub_path)
        response = self.s.post(url=server_url, headers=headers,
                               json=payload, timeout=timeout)
        super().check_response_header(response)
        data = response.json()
        super().check_response_json(data)

        request_id = self.response_request_id(response)
        response.request_id = request_id
        return response
