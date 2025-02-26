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

r"""text to speech component."""
from typing import Literal
from urllib.parse import quote_plus

from appbuilder.core.component import Component
from appbuilder.core.message import Message
from appbuilder.core._exception import AppBuilderServerException
from appbuilder.core.components.tts.model import *


class TTS(Component):
    r"""
      文本转语音组件，即输入一段文本将其转为一段语音

      Examples:

      .. code-block:: python

        import appbuilder
        os.environ["APPBUILDER_TOKEN"] = '...'
        tts = appbuilder.TTS()

        # 默认使用baidu-tts模型, 默认返回MP3格式
        inp = appbuilder.Message(content={"text": "欢迎使用语音合成"})
        out = tts.run(inp)
        with open("sample.mp3", "wb") as f:
            f.write(out.content["audio_binary"])

        # 使用paddlespeech-tts模型，目前只支持返回WAV格式
        inp = appbuilder.Message(content={"text": "欢迎使用语音合成"})
        out = tts.run(inp, model="paddlespeech-tts", audio_type="wav")
        with open("sample.wav", "wb") as f:
            f.write(out.content["audio_binary"])
    """
    Baidu_TTS = "baidu-tts"
    PaddleSpeech_TTS = "paddlespeech-tts"

    def __init__(self, *args, **kwargs):
        r"""初始化语音识别实例

            参数:
                *args (any, 可选): 位置参数
                **kwargs(any, 可选)： 关键字参数
            返回:
                无
           """
        r""""implement __init__ method"""
        super().__init__(*args, **kwargs)
        self.model = ""

    def run(self,
            message: Message,
            model: Literal["baidu-tts", "paddlespeech-tts"] = "baidu-tts",
            speed: int = 5,
            pitch: int = 5,
            volume: int = 5,
            person: int = 0,
            audio_type: Literal["mp3", "wav"] = "mp3",
            timeout: float = None,
            retry: int = 0
            ) -> Message:
        r"""执行文本转语音

            参数：
                message (obj: `Message`): 待转为语音的文本. 举例: Message(content={"text": "欢迎使用百度语音"})
                如果选择`baidu-tts`模型，`text`最大文本长度为1024 GBK编码长度, 如果选择`paddlespeech-tts`模型, `text`最大文本长度是510个字符.
                model (str, 可选): 默认是`baidu-tts`模型，可设置为`paddlespeech-tts`
                speed(int, 可选): 语音语速，默认是5中等语速，取值范围在0~15之间，如果选择模型为paddlespeech-tts，参数自动失效
                pitch(int, 可选): 语音音调，默认是5中等音调，取值范围在0~15之间，如果选择模型为paddlespeech-tts，参数自动失效
                volume(int, 音量): 语音音量，默认是5中等音量，取值范围在0~15之间，如果选择模型为paddlespeech-tts，参数自动失效
                person(int, 可选): 语音人物特征，默认是0,可选值包括度小宇=1 度小美=0 度逍遥（基础）=3 度丫丫=4 度逍遥（精品）=5003
                度小鹿=5118 度博文=106 度小童=110 度小萌=111 度米朵=103 度小娇=5，如果选择模型为paddlespeech-tts，参数自动失效
                audio_type(str, 可选): 音频文件格式，默认是`mp3`, 如果选择`paddlespeech-tts`模型，参数只能设为`wav`
                timeout (float, 可选): HTTP超时时间
                retry (int, 可选)： HTTP重试次数

              返回:
                 message (obj: `Message`): 文本转语音结果. 举例: Message(content={"audio_binary": b"xxx", "audio_type": "mp3"})
        """
        if model != self.Baidu_TTS and model != self.PaddleSpeech_TTS:
            raise ValueError("unsupported model {}".format(model))
        self.model = model
        inp = TTSInMsg(**message.content)
        if len(inp.text) == 0:
            raise ValueError("text field is empty")

        if model == self.Baidu_TTS and audio_type != "mp3" and audio_type != "wav":
            raise ValueError("invalid audio type")
        elif model == self.PaddleSpeech_TTS and audio_type != "wav":
            raise ValueError("invalid audio type")
        request = TTSRequest()
        request.tex = inp.text
        request.spd = speed
        request.pit = pitch
        request.vol = volume
        request.per = person
        if audio_type == "mp3":
            request.aue = 3
        elif audio_type == "wav":
            request.aue = 6
        response = self.__synthesis(request, timeout, retry)
        out = TTSOutMsg(audio_binary=response.binary, audio_type=audio_type)
        return Message(content=dict(out))

    def __synthesis(self,
                    request: TTSRequest,
                    timeout: float = None,
                    retry: int = 0) -> TTSResponse:
        r"""调用底层接口进行语音合成

            参数:
                request (obj: `[PaddleTTSRequest, TTSRequest]`) : 语音合成输入参数

            返回：
                response (obj: `TTSResponse`): 语音合成输出参数
        """
        request.ctp = "1"
        request.lan = "zh"
        request.cuid = "1"
        if self.model == self.Baidu_TTS:
            request.tex = quote_plus(request.tex)
            request.validate_baidu_tts()
            url = self.service_url("/v1/bce/aip_speech/tts_online")
        elif self.model == self.PaddleSpeech_TTS:
            request.tp_project_id = "paddlespeech"
            request.tp_per_id = "100001"
            request.validate_paddle_speech_tts()
            url = self.service_url("/v1/bce/paddle_speech/text2audio")
        else:
            raise ValueError("model '{}' is not supported".format(self.model))
        if retry != self.retry.total:
            self.retry.total = retry
        auth_header = self.auth_header()
        if self.model == self.Baidu_TTS:
            response = self.s.post(url, data=TTSRequest.to_dict(request), timeout=timeout, headers=auth_header)
        elif self.model == self.PaddleSpeech_TTS:
            auth_header = self.auth_header()
            auth_header['Content-type'] = "application/json"
            response = self.s.post(url, json=TTSRequest.to_dict(request), timeout=timeout, headers=auth_header)
        super().check_response_header(response)
        content_type = response.headers.get("Content-Type", "application/json")
        if content_type.find("application/json") != -1:
            data = response.json()
            super().check_response_json(data)
            self.__class__.__check_service_error(data)
        return TTSResponse(
            binary=response.content,
            request_id=self.response_request_id(response),
            aue=request.aue
        )

    @staticmethod
    def __check_service_error(data: dict):
        r"""个性化服务response检查

              参数:
                  request (dict) : 文本转语音body返回
              返回：
                  无
          """

        if "err_no" in data or "err_msg" in data or 'sn' in data or 'idx' in data:
            raise AppBuilderServerException(
                service_err_code=data.get("err_no", 0),
                service_err_message="{} . {} . {}]".
                format(data.get("err_msg", ""),
                       data.get("sn", ""),
                       data.get("idx", ""))
            )
