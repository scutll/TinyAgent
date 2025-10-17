# the core agent part 
# it does not contains the model directly, but the pipeline does for it 
# the agent_core is deployed in user's system, and the Model deployed in the server. agent_core uploads input and gets reply streamly from server

import os
from request.api import get_response_from_dsApi
from prompts.prompt_react import prompt_react
from prompts.tools_prompt import tools_prompt

# 创建日志目录和文件
os.makedirs("logs", exist_ok=True)

from tools.Tools import ToolsContainer
from Memory.Container import MemoryContainer
from request.api import *
from utils.parser import parse_response
import tools.File_tools as ft
import tools.System_tools as st


# 初始化conversation(Memory)
system_prompt = prompt_react + tools_prompt
Memory = MemoryContainer()
Memory._add_prompt(system_prompt)



# 导入工具
tools = ToolsContainer()
Tools = [ft.search_replace, ft.create_file, ft.read_file, st.list_file, st.tree_file, st.get_absolute_cur_path, st.change_dir, st.delete_dir, st.delete_file]
tools.load_tool(Tools)


class AgentCore:
    def __init__(self):
        self.task = None

    def set_task(self, task: str):
        self.task = task

    def run(self):
        if self.task is None:
            raise Exception("None task!")
        # self.cur_conv = new_conversation()
        # response = get_response(self.task, self.cur_conv)
        
        print("Model reasoning: ")
        response = get_response_from_dsApi(self.task, Memory)


        think, text, func_call, func_args = parse_response(response)
        print('-' * 27, "\nmy think: ", think)
        print('-' * 27, "\ndeepseek: ", text)
        print('-' * 27)
        if func_call == "Finish":
            return
        
        
        while True:
            # print(f"calling {func_call} with {func_args}:\n y to confirm")
            # while input() != 'y':
            #     continue

            if func_call == "ParseFailure":
                observation = "你上次生成的回答格式有问题导致Agent无法成功解释，请查阅system_prompt，严格按照要求的输出格式重新输出"
            else:
                observation =  tools.call_func(func_call, func_args)
            
            # 这个observation可以以tool的身份返回，可以进行一下支持的修改，看看效果会不会好一点
            print("Model reasoning: ")
            response = get_response_from_dsApi(observation, Memory)

            think, text, func_call, func_args = parse_response(response)
            
            print("my think: ", think)
            print('-' * 27, "\ndeepseek: ", text)
            print('-' * 27)
            
            if func_call == "Finish":
                break
        
        