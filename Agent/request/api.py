import httpx
from openai import OpenAI
from agent_core import log
from Memory.Container import MemoryContainer



def get_response(*args, **kwargs):
    pass

def new_conversation(*args, **kwargs)->str:
    return ""

def switch_conversation(*args, **kwargs)->str:
    return ""

def delete_conversation(*args, **kwargs):
    pass


client = OpenAI(
    api_key="sk-e601ccf83e2b414a82f301d4d0b7042b",
    base_url="https://api.deepseek.com"
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
