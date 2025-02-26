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

"""
ernie bot embedding
"""

from typing import Union, List

from appbuilder.core.message import Message
from appbuilder.core.components.embeddings.base import EmbeddingBaseComponent
from appbuilder.core.component import ComponentArguments

from appbuilder.core._exception import AppBuilderServerException


class EmbeddingArgs(ComponentArguments):
    """ernie bot embedding配置"""

    text: Union[Message[str], str]


class Embedding(EmbeddingBaseComponent):
    """
    Embedding

    Embedding-V1是基于百度文心大模型技术的文本表示模型，将文本转化为用数值表示的向量形式，用于文本检索、信息推荐、知识挖掘等场景。

    Examples:

        .. code-block:: python

            import appbuilder
            from appbuilder import Message

            os.environ["APPBUILDER_TOKEN"] = '...'

            embedding = appbuilder.Embedding()

            embedding_single = embedding(Message("hello world!"))

            embedding_batch = embedding.batch(Message(["hello", "world"]))
    """

    name: str = "embedding"
    version: str = "v1"

    meta = EmbeddingArgs

    base_url: str = "/v1/bce/wenxinworkshop/ai_custom/v1/embeddings/"

    def __init__(self, type='embedding-v1'):
        """Embedding"""
        self.base_url = self.base_url + type

        super().__init__(self.meta)

    def _check_response_json(self, data: dict):
        """
        check_response_json for embedding
        """

        self.check_response_json(data)
        if "error_code" in data and "error_msg" in data:
            raise AppBuilderServerException(
                service_err_code=data['error_code'],
                service_err_message=data['error_msg'],
            )

    def _request(self, payload: dict) -> dict:
        """
        request to gateway
        """

        resp = self.s.post(
            url=self.service_url(self.base_url),
            headers={
                "X-Appbuilder-Authorization": f"{self.secret_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        self.check_response_header(resp)
        self._check_response_json(resp.json())

        return resp.json()

    def _batchify(self, texts: List[str], batch_size: int = 16) -> List[List[str]]:
        """
        batchify input text list
        """

        if batch_size > 16:
            raise ValueError(f"The max Embedding batch_size is 16, but got {batch_size}")

        return [
            texts[i : i + batch_size] for i in range(0, len(texts), batch_size)
        ]

    def _batch(self, texts: List[str]) -> Message[List[List[float]]]:
        """
        batch run implement
        """

        batches = self._batchify(texts)
        results = []
        for batch in batches:
            result = self._request({"input": batch})
            results.extend(result['data'])
        results = Message([result['embedding'] for result in results])

        return results

    def run(self, text: Union[Message[str], str]) -> Message[List[float]]:
        """
        run
        """
    
        _text = text if isinstance(text, str) else text.content

        return Message(self._batch([_text]).content[0])

    def batch(self, texts: Union[Message[List[str]], List[str]]) -> Message[List[List[float]]]:
        """
        batch run
        """

        _texts = texts if isinstance(texts, list) else texts.content

        return self._batch(_texts)
