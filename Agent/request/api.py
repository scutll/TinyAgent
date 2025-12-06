import json
from openai import OpenAI
from pydantic import BaseModel, Field
from volcenginesdkarkruntime import Ark
from Agent.utils.logging_ import log
from Agent.Memory.container import MemoryContainer
from typing import Any, Dict, Union
models = {
    "deepseek": "deepseek-chat",
    "deepseek-reasoner": "deepseek-reasoner",
    "Doubao-think": "doubao-seed-1-6-thinking-250715",
    "Doubao-flash": "doubao-seed-1-6-flash-250615"
}

# 从配置文件读取API配置
with open('config.json', 'r') as f:
    config = json.load(f)

ds_api_key = config["ds_api_key"] if "ds_api_key" in config else ""
ds_base_url = config["ds_base_url"] if "ds_base_url" in config else ""

doubao_api_key = config["doubao_api_key"] if "doubao_api_key" in config else ""
doubao_base_url = config["doubao_base_url"] if "doubao_base_url" in config else ""


client = OpenAI(
    api_key=ds_api_key,
    base_url=ds_base_url
)


def get_response_from_dsApi(input: str, Memory: MemoryContainer, Model="deepseek-chat"):
    """
    supporting Models:\n
    \t"deepseek-chat",\n
    \t"deepseek-reasoner",
    """

    Memory._add_user_message(input)
    log(f"[LLM request][{Model}]\n{input[:100]}...")
    response = client.chat.completions.create(
        model=Model,
        messages=Memory(),
        stream=False,
    )
    result = response.choices[0].message.content
    log(f"[LLM response][{Model}]\n{result}")

    if result:
        Memory._add_assistant_message(str(result))
    else:
        Memory._pop_message()  
    log("(deepseek): " + result if result is not None else "Fail to generate response")
    log("======================================")
    return result if result is not None else "Failed to generate response!"


def get_response_from_Doubao(input: Union[list, str], Memory: MemoryContainer, Model="doubao-seed-1-6-thinking-250715"):
    """
    supporting models:\n
    \t"doubao-seed-1-6-thinking-250715",
    \t"doubao-seed-1-6-flash-250615"
    """
    # 带图片的文本以List形式的参数给到input
    Memory._add_user_message(input)
    client = Ark(
        api_key=doubao_api_key,
        base_url=doubao_base_url
    )
    log(f"[LLM request][{Model}]\n{input[:100]}...")
    completion = client.chat.completions.create(
        model=Model,
        messages=Memory(),
        stream=False,
    )
    result = str(completion.choices[0].message.content) # type: ignore
    log(f"[LLM response][{Model}]\n{result}")
    if result:
        Memory._add_assistant_message(str(result))
    else:
        Memory._pop_message()  
    log("(Doubao): " + result if result is not None else "Fail to generate response")
    log("======================================")
    
    
    return result if result is not None else "Failed to generate response!"


class agentOutputFields(BaseModel):
    observation: str = Field(description="简单描述上一轮系统提供的信息，首轮为用户输入的摘要。")
    think: str = Field(description="你的内部思考过程, 包括对observation的分析和下一步应该如何做")
    response: str = Field( description="给用户的可见回答，简要说明情况或回答问题。")
    action: str = Field(description="本轮要执行的工具名称，或 'Finish'。")
    action_input: Dict[str, Any] = Field(default_factory=dict, description="传给工具的参数字典, 具体格式应该参照toolsyyyy, 或最终回答内容。")

def structured_response(input: Union[list, str], Memory: MemoryContainer, Model="doubao-seed-1-6-thinking-250715"):
    Memory._add_user_message(input)
    log(f"[structured request][{Model}]\n{input}")
    client = OpenAI(
        base_url='https://ark.cn-beijing.volces.com/api/v3',
        api_key=doubao_api_key,
    )
    response = client.responses.parse(
        model=Model, 
        input=Memory(),
        text_format=agentOutputFields
    )
    
    result = response.output_parsed
    log(f"[structured response][{Model}]\n{result}")
    if result:
        Memory._add_assistant_message(str(result))
    else:
        Memory._pop_message()
    
    return result if result is not None else "Failed to generate response!"

api = {
    "Doubao": get_response_from_Doubao,
    "Deepseek": get_response_from_dsApi
}