# Copyright (c) 2023 Baidu, Inc. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from appbuilder.core.components.llms.base import CompletionBaseComponent
from appbuilder.core.message import Message
from appbuilder.core.component import ComponentArguments
from pydantic import BaseModel, Field


class TagExtractionArgs(ComponentArguments):
    """标签抽取配置"""
    message: Message = Field(...,
                             variable_name="query",
                             description="""输入消息，用于模型的主要输入内容，例如'本实用新型公开了一种可利用热能的太阳能光伏光热一体化组件，
                             包括太阳能电池，还包括有吸热板，太阳能电池粘附在吸热板顶面，吸热板内嵌入有热电材料制成的内芯，吸热板底面设置有蛇形管。
                             本实用新型结构紧凑，安装方便，能充分利用太阳能电池散发的热能，具有较高的热能利用率。'""")


class TagExtraction(CompletionBaseComponent):
    """
    标签抽取组件，基于生成式大模型进行关键标签的抽取。

    Examples:

        .. code-block:: python

            import appbuilder
            os.environ["APPBUILDER_TOKEN"] = '...'

            tag_extraction = appbuilder.TagExtraction(model="ernie-bot-4")
            answer = tag_extraction(appbuilder.Message("从这段文本中抽取关键标签"))

    """

    name = "tag_extraction"
    version = "v1"
    meta = TagExtractionArgs

    def __init__(self, model=None):
        """初始化TagExtraction模型。
        
        Args:
            model (str|None): 模型名称，用于指定要使用的千帆模型。

        Returns:
            None
        
        """
        super().__init__(TagExtractionArgs, model=model)

    def run(self, message, stream=False, temperature=1e-10):
        """
        使用给定的输入运行模型并返回结果。

        Args:
            message (obj:`Message`，必选): 输入消息，用于模型的主要输入内容。
            stream (bool, 可选): 指定是否以流式形式返回响应。默认为 False。
            temperature (float, 可选): 模型配置的温度参数，用于调整模型的生成概率。取值范围为 0.0 到 1.0，其中较低的值使生成更确定性，较高的值使生成更多样性。默认值为 1e-10。

        返回:
            obj:`Message`: 模型运行后的输出消息。
        """
        return super().run(message=message, stream=stream, temperature=temperature)
