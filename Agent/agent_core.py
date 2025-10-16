# the core agent part 
# it does not contains the model directly, but the pipeline does for it 
# the agent_core is deployed in user's system, and the Model deployed in the server. agent_core uploads input and gets reply streamly from server

import os
from openai import OpenAI


def read_file(path:str):
    """Read a text file and return its content.

    On error returns a string starting with "error in reading <path>: <error>".
    """
    try:
        with open(path, "r", encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"error in reading {path}: {e}"
    return content


client = OpenAI(
    api_key="sk-e601ccf83e2b414a82f301d4d0b7042b",
    base_url="https://api.deepseek.com"
)
def get_response_from_dsApi(input: str, conversation):
    conversation.append({"role":"user", "content": input})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=conversation,
        stream=False,
    )
    result = response.choices[0].message.content
    conversation.append({"role":"assistant", "content": result})
    return result if result is not None else "Failed to generate response!"

conversation = []
system_prompt = read_file("E:\D2L\Agent\TinyAgent\llmApi\Prompts\prompt_react.md")
conversation.append({"role": "system", "content": system_prompt})



from tools.Tools import ToolsContainer
from request.api import *
from utils.parser import parse_response
import tools.File_tools as ft
import tools.System_tools as st
tools = ToolsContainer()

tools.load_tool(ft.search_replace)
tools.load_tool(ft.create_file)
tools.load_tool(ft.read_file)
tools.load_tool(st.list_file)
tools.load_tool(st.tree_file)
tools.load_tool(st.get_absolute_cur_path)
tools.load_tool(st.change_dir)
tools.load_tool(st.delete_dir)
tools.load_tool(st.delete_file)



class AgentCore:
    def __init__(self):
        self.task = None
        self.cur_conv = None

    def set_task(self, task: str):
        self.task = task

    def run(self):
        if self.task is None:
            raise Exception("None task!")
        # self.cur_conv = new_conversation()
        # response = get_response(self.task, self.cur_conv)
        
        print("Model reasoning: ")
        response = get_response_from_dsApi(self.task, conversation)

        
        think, text, func_call, func_args = parse_response(response)
        print("my think: ", think)
        print("===========================================\ndeepseek: ", text)
        print("-------------------------------------------")
        
        while True:
            # print(f"calling {func_call} with {func_args}:\n y to confirm")
            # while input() != 'y':
            #     continue

            # call_func还没有搞定，也就是管理tools的工具，在Tools.py实现
            observation =  tools.call_func(func_call, func_args)

            # response = get_response(observation, self.cur_conv)
            
            # 这个observation可以以tool的身份返回，可以进行一下支持的修改，看看效果会不会好一点
            print("Model reasoning: ")
            response = get_response_from_dsApi(observation, conversation)

            think, text, func_call, func_args = parse_response(response)
            print("my think: ", think)
            print("===========================================\ndeepseek: ", text)
            print("-------------------------------------------")
            
            if func_call == "Finish":
                break
        
        
        
    