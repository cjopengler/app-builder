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

r"""Text2Image component.
"""
import time
import json

from appbuilder.core.component import Component
from appbuilder.core.message import Message
from appbuilder.core._exception import AppBuilderServerException
from appbuilder.core.components.text_to_image.model import Text2ImageSubmitRequest, Text2ImageQueryRequest, \
    Text2ImageQueryResponse, Text2ImageSubmitResponse, Text2ImageOutMessage, Text2ImageInMessage


class Text2Image(Component):
    r"""
    AI作画组件，即对于输入的文本，输出生成的图片url。

    Examples:

    .. code-block:: python

        import appbuilder
        text_to_image = appbuilder.Text2Image()
        os.environ["APPBUILDER_TOKEN"] = '...'
        inp = appbuilder.Message(content={"prompt": "上海的经典风景"})
        out = text_to_image.run(inp)
        # 打印生成结果
        print(out.content) # eg: {"img_urls": ["xxx"]}
    """

    def run(self, message: Message, width: int = 1024, height: int = 1024, image_num: int = 1,
            timeout: float = None, retry: int = 0):
        """
        输入文本并返回生成的图片url。

        参数:
            message (obj:`Message`): 输入消息，用于模型的主要输入内容。这是一个必需的参数。举例: Message(content={"prompt": "上海的经典风景"})
            width (int，可选): 图片宽度，支持：512x512、640x360、360x640、1024x1024、1280x720、720x1280、2048x2048、2560x1440、1440x2560。
            height (int， 可选): 图片高度，支持：512x512、640x360、360x640、1024x1024、1280x720、720x1280、2048x2048、2560x1440、1440x2560。
            image_num (int， 可选): 生成图片数量，默认一张，支持生成 1-8 张。
            timeout (float, 可选): 请求的超时时间。
            retry (int, 可选): 请求的重试次数。

        返回:
            obj:`Message`: 输出生成图片的url。举例: Message(content={"img_urls": ["xxx"]})。
        """
        inp = Text2ImageInMessage(**message.content)
        text2ImageSubmitRequest = Text2ImageSubmitRequest()
        text2ImageSubmitRequest.prompt = inp.prompt
        text2ImageSubmitRequest.width = width
        text2ImageSubmitRequest.height = height
        text2ImageSubmitRequest.image_num = image_num
        text2ImageSubmitResponse = self.submitText2ImageTask(text2ImageSubmitRequest)
        taskId = text2ImageSubmitResponse.data.primary_task_id
        if taskId is not None:
            while True:
                request = Text2ImageQueryRequest()
                request.task_id = taskId
                text2ImageQueryResponse = self.queryText2ImageData(request)
                if text2ImageQueryResponse.data.task_progress is not None:
                    task_progress = text2ImageQueryResponse.data.task_progress
                    if task_progress == 1:
                        break
                    time.sleep(0.2)
            img_urls = self.extract_img_urls(text2ImageQueryResponse)
            out = Text2ImageOutMessage(img_urls=img_urls)
            return Message(content=dict(out))

    def submitText2ImageTask(self, request: Text2ImageSubmitRequest, timeout: float = None,
                           retry: int = 0) -> Text2ImageSubmitResponse:

        """
        使用给定的输入并返回AI作画的任务信息。

        参数:
            request (obj:`Text2ImageSubmitRequest`): 输入请求，这是一个必需的参数。
            timeout (float, 可选): 请求的超时时间。
            retry (int, 可选): 请求的重试次数。

        返回:
            obj:`Text2ImageSubmitResponse`: 接口返回的输出消息。
        """
        url = self.service_url("/v1/bce/aip/ernievilg/v1/txt2imgv2")
        data = Text2ImageSubmitRequest.to_json(request)
        headers = self.auth_header()
        headers['content-type'] = 'application/json'
        if retry != self.retry.total:
            self.retry.total = retry
        response = self.s.post(url, data=data, headers=headers, timeout=timeout)
        super().check_response_header(response)
        data = response.json()
        super().check_response_json(data)
        self.__class__.check_service_error(data)
        request_id = response.headers.get('X-Appbuilder-Request-Id')
        response = Text2ImageSubmitResponse.from_json(payload=json.dumps(data))
        response.request_id = request_id
        return response

    def queryText2ImageData(self, request: Text2ImageQueryRequest, timeout: float = None,
                          retry: int = 0) -> Text2ImageQueryResponse:

        """
        使用给定的输入并返回AI作画的结果。

        参数:
            request (obj:`Text2ImageQueryRequest`): 输入请求，这是一个必需的参数。
            timeout (float, 可选): 请求的超时时间。
            retry (int, 可选): 请求的重试次数。

        返回:
            obj:`Text2ImageQueryResponse`: 接口返回的输出消息。
        """
        url = self.service_url("/v1/bce/aip/ernievilg/v1/getImgv2")
        data = {
            "task_id": request.task_id
        }
        headers = self.auth_header()
        headers['content-type'] = 'application/json'
        if retry != self.retry.total:
            self.retry.total = retry
        response = self.s.post(url, json=data, headers=headers, timeout=timeout)
        super().check_response_header(response)
        data = response.json()
        super().check_response_json(data)
        self.__class__.check_service_error(data)
        request_id = response.headers.get('X-Appbuilder-Request-Id')
        response = Text2ImageQueryResponse.from_json(payload=json.dumps(data))
        response.request_id = request_id
        return response

    def extract_img_urls(self, response: Text2ImageQueryResponse):
        """
        提取图片的url。

        参数:
            response (obj:`Text2ImageQueryResponse`): A作画生成的返回结果。
        返回:
            List[str]:`img_urls`: 从返回体中提取的图片url列表。
        """
        img_urls = []
        if response and response.data and response.data.sub_task_result_list:
            for sub_task_result in response.data.sub_task_result_list:
                if sub_task_result and sub_task_result.final_image_list:
                    for final_image in sub_task_result.final_image_list:
                        if final_image and final_image.img_url:
                            img_urls.append(final_image.img_url)

        return img_urls

    @staticmethod
    def check_service_error(data: dict):
        r"""个性化服务response参数检查

            参数:
                request (dict) : AI作画生成结果body返回
            返回：
                无
        """
        if "error_code" in data or "error_msg" in data:
            raise AppBuilderServerException(service_err_code=data.get("error_code"),
                                            service_err_message=data.get("error_msg"))