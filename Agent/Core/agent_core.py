# the core agent part 
# it does not contains the model directly, but the pipeline does for it 
# the agent_core is deployed in user's system, and the Model deployed in the server. agent_core uploads input and gets reply streamly from server

import os
from Agent.request.api import api
from Agent.prompts.prompt_react import prompt_react
from Agent.prompts.tools_prompt import *

# 创建日志目录和文件
os.makedirs("logs", exist_ok=True)

from Agent.Memory.Container import MemoryContainer
from Agent.request.api import *
from Agent.utils.parser import parse_response
from Agent.utils.logging import log


# 导入工具
from Agent.tools.Tools import ToolsContainer
import Agent.tools.File_tools as ft
import Agent.tools.System_tools as st
import Agent.tools.Web_tools as wt
import Agent.tools.docs_tools as dt
import Agent.tools.inquery_tool as it
from Agent.prompts.tools_prompt import Finish_prompt 
tools = ToolsContainer()
Tools = [it.inquery_user(),
         ft.create_file(), ft.read_file(), ft.search_replace(),
         st.delete_dir(), st.delete_file(), st.get_absolute_cur_path(), st.tree_file(), st.execute_command(),
         dt.read_word_document(), dt.extract_info_from_docx_table(),
         wt.fetch_webpage_with_selector(), wt.fetch_webpage()]
tools.load_tool(Tools)


# 初始化conversation(Memory)

system_prompt = prompt_react + tools.prompt_all_tools + Finish_prompt


class AgentCore:
    def __init__(self, model: str = "doubao-seed-1-6-thinking-250715"):
        self.task = None
        self.model = model
        self.UseModel = "Doubao" if "doubao" in model.lower() else "Deepseek"
        self.Memory = MemoryContainer()
        self.Memory._add_prompt(system_prompt)

    def set_task(self, task: str):
        self.task = task
        
    def reset_memory__(self):
        self.Memory.reset__()
        self.Memory._add_prompt(system_prompt)
        print("memory reset!")

    def run(self):
        if self.task is None:
            raise Exception("None task!")
        # self.cur_conv = new_conversation()
        # response = get_response(self.task, self.cur_conv)
        
        print("Model reasoning: ")
        # response = get_response_from_dsApi(self.task, Memory)
        input = self.task
        response = api[self.UseModel](input, self.Memory)

        think, text, func_call, func_args = parse_response(response)
        print('-' * 27, "\nmy think: ", think)
        print('-' * 27, "\nAssistant: ", text)
        print('-' * 27)
        if func_call == "Finish":
            return
        
        
        while True:
            # print(f"calling {func_call} with {func_args}:\n y to confirm")
            # while input() != 'y':
            #     continue

            if func_call == "ParseFailure":
                observation = """
                你上次生成的回答格式有问题导致Agent无法成功解释，请查阅system_prompt，严格按照要求的输出格式重新输出:
                \nTracestack:\n
                """ + text
            else:
                observation =  tools.call_func(func_call, func_args)
            if isinstance(observation, str) and func_call != dt.read_word_document.__name__:
                log(message=f"(observation): \n{observation}")
            
            # 这个observation可以以tool的身份返回，可以进行一下支持的修改，看看效果会不会好一点
            print("Model reasoning: ")
            # response = get_response_from_dsApi(observation, Memory)
            ## 这里豆包也出现了问题，observation是dict类型的，但api调用里面没有吧observation的text键对应内容提取出来。。。。。
            response = api[self.UseModel](observation, self.Memory)

            think, text, func_call, func_args = parse_response(response)
            
            print("my think: ", think)
            print('-' * 27, "\nAssistant: ", text)
            print('-' * 27)
            
            if func_call == "Finish":
                break
        log("==================Finish Task====================")
        
        