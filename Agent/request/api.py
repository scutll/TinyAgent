import json
import httpx
from openai import OpenAI
from volcenginesdkarkruntime import Ark
from Agent.utils.logging import log
from Agent.Memory.Container import MemoryContainer
from typing import Dict

def get_response(*args, **kwargs):
    pass

def new_conversation(*args, **kwargs)->str:
    return ""

def switch_conversation(*args, **kwargs)->str:
    return ""

def delete_conversation(*args, **kwargs):
    pass

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


def get_response_from_dsApi(input, Memory: MemoryContainer):
    
    input = str(input)
    Memory._add_user_message(input)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=Memory(),
        stream=False,
    )
    result = response.choices[0].message.content
    Memory._add_assistant_message(str(result))
    log("(deepseek): " + result if result is not None else "Fail to generate response")
    log("======================================")
    return result if result is not None else "Failed to generate response!"


def get_response_from_Doubao(input, Memory: MemoryContainer):
    # 带图片的文本以List形式的参数给到input
    if isinstance(input,dict):
        input = input["text"]
    
    Memory._add_user_message(input)
    client = Ark(
        api_key=doubao_api_key,
        base_url=doubao_base_url
    )
    completion = client.chat.completions.create(
        model="doubao-seed-1-6-vision-250815",
        messages=Memory(),
        stream=False,
    )
    result = str(completion.choices[0].message.content)
    Memory._add_assistant_message(str(result))
    log("(Doubao): " + result if result is not None else "Fail to generate response")
    log("======================================")
    return result if result is not None else "Failed to generate response!"


api = {
    "Doubao": get_response_from_Doubao,
    "Deepseek": get_response_from_dsApi
}