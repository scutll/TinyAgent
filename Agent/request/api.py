import json
import httpx
from openai import OpenAI
from volcenginesdkarkruntime import Ark
from Agent.utils.logging import log
from Agent.Memory.Container import MemoryContainer


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


client = OpenAI(
    api_key=config["ds_api_key"],
    base_url=config["ds_base_url"]
)


def get_response_from_dsApi(input, Memory: MemoryContainer):
    input = str(input["text"])
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
    # 后面可以添加图片
    input = input["text"]
    Memory._add_user_message(input)
    
    client = Ark(
        api_key=config["doubao_api_key"],
        base_url=config["doubao_base_url"]
    )
    completion = client.chat.completions.create(
        model="doubao-seed-1-6-vision-250815",
        messages=Memory(),
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