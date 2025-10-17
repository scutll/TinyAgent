import json
import httpx
from openai import OpenAI
from utils.logging import log
from Memory.Container import MemoryContainer


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
    api_key=config["api_key"],
    base_url=config["base_url"]
)


def get_response_from_dsApi(input: str, Memory: MemoryContainer):
    Memory._add_user_message(input)
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=Memory(),
        stream=False,
    )
    result = response.choices[0].message.content
    Memory._add_assistant_message(str(result))
    log(result if result is not None else "Fail to generate response")
    log("======================================")
    return result if result is not None else "Failed to generate response!"
