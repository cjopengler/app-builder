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


class GBISelectTable(Component):
    """
    gib nl2sql
    """

    def __init__(self, model_name: str, table_descriptions: Dict[str, str],
                 secret_key: Optional[str] = None,
                 gateway: str = ""):
        super().__init__(secret_key=secret_key, gateway=gateway)
        self.model_name = model_name
        self.server_sub_path = "gbi_select_table"
        self.prefix = "/v1/"
        self.table_descriptions = table_descriptions

    def run(self,
            message: Message,
            session: Session) -> Message[List[str]]:
        """

        :param message:
        :param session:
        :return:
        """

        query = message.content
        session = session

        response = self._run_select_table(query=query, session=session,
                                          table_descriptions=self.table_descriptions,
                                          model_name=self.model_name,
                                          timeout=60,
                                          retry=2)

        rsp_data = response.json()

        return Message(content=rsp_data)

    def _run_select_table(self, query: str, session: Session, table_descriptions: Dict[str, str],
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
                   "table_descriptions": table_descriptions,
                   "session": session.records,
                   "model_name": model_name}

        server_url = self.service_url(prefix=self.prefix, sub_path=self.server_sub_path)
        response = self.s.post(url=server_url, headers=headers,
                               json=payload, timeout=timeout)
        super().check_response_header(response)
        data = response.json()
        super().check_response_json(data)

        request_id = self.response_request_id(response)
        response.request_id = request_id
        return response
