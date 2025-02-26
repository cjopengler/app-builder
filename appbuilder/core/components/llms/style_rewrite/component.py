"""StyleRewrite"""
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


""" """
from appbuilder.core.components.llms.base import CompletionBaseComponent
from appbuilder.core.message import Message

from appbuilder.core.component import ComponentArguments

from pydantic import BaseModel, Field
from enum import Enum


class StyleChoices(Enum):
    """"""
    YINGXIAO = "营销话术"
    JIAOXUE = "教学话术"
    JILI = "激励话术"
    KEFU = "客服话术"
    ZHIBO = "直播话术"

    def to_chinese(self):
        """
        将StyleChoices枚举类中的值转换为中文描述。
        
        Args:
            无参数
        
        Returns:
            返回一个字典，键是StyleChoices枚举类的成员，值为对应的中文描述字符串。
        
        """
        descriptions = {
            StyleChoices.YINGXIAO: "营销话术",
            StyleChoices.JIAOXUE: "教学话术",
            StyleChoices.JILI: "激励话术",
            StyleChoices.KEFU: "客服话术",
            StyleChoices.ZHIBO: "直播话术"
        }
        return descriptions[self]


class StyleRewriteArgs(ComponentArguments):
    """文本风格转写配置"""
    message: Message = Field(...,
                             variable_name="query",
                             description="需要改写的文本，该字段为必须字段。")
    style: StyleChoices = Field(...,
                                variable_name
                                ="style",
                                description="想要转换的文本风格，目前有营销、客服、直播、激励及教学五种话术可选")


class StyleRewrite(CompletionBaseComponent):
    """
    文本风格转写大模型组件， 基于生成式大模型对文本的风格进行改写，支持有营销、客服、直播、激励及教学五种话术。

    Examples:

        .. code-block:: python

            import os
            import appbuilder
            os.environ["APPBUILDER_TOKEN"] = '...'

            style_rewrite = appbuilder.StyleRewrite(model="ernie-bot-4")
            answer = style_rewrite(appbuilder.Message("文心大模型发布新版本"), style="激励话术")

    """
    name = "style_rewrite"
    version = "v1"
    meta = StyleRewriteArgs

    def __init__(self, model=None):
        """初始化StyleRewrite模型。
        
        Args:
            model (str|None): 模型名称，用于指定要使用的千帆模型。

        Returns:
            None
        
        """
        super().__init__(StyleRewriteArgs, model=model)

    def run(self, message, style="营销话术", stream=False, temperature=1e-10):
        """
        使用给定的输入运行模型并返回结果。
        
        Args:
            message (obj:`Message`): 输入消息，用于模型的主要输入内容。这是一个必需的参数。
            style (str, optional): 想要转换的文本风格，目前有营销、客服、直播、激励及教学五种话术可选. 默认是"营销话术".
            stream (bool, optional): 指定是否以流式形式返回响应。默认为 False。
            temperature(float, optional): 模型配置的温度参数，用于调整模型的生成概率。取值范围为 0.0 到 1.0，其中较低的值使生成更确定性，较高的值使生成更多样性。默认值为 1e-10。
        Returns:
            obj:`Message`: 模型运行后的输出消息。
        
        """
        return super().run(message=message, style=style, stream=stream, temperature=temperature)
