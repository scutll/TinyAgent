# the core agent part 
# it does not contains the model directly, but the pipeline does for it 
# the agent_core is deployed in user's system, and the Model deployed in the server. agent_core uploads input and gets reply streamly from server

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"

from typing import Any, Optional, Union

from Agent.request.api import api,structured_response, agentOutputFields
from Agent.prompts.prompt_react import prompt_react
from Agent.prompts.tools_prompt import *

from Agent.Memory.container import MemoryContainer
from Agent.Memory.compression import memory_compress__
from Agent.request.api import *
from Agent.utils.parser import parse_response
from Agent.utils.logging_ import log
from Agent.utils.config import get_configured_model


# 导入工具
from Agent.tools.Tools import ToolsContainer
import Agent.tools.File_tools as ft
import Agent.tools.System_tools as st
import Agent.tools.Web_tools as wt
import Agent.tools.docs_tools as dt
import Agent.tools.inquery_tool as it
from Agent.prompts.tools_prompt import Finish_prompt 
tools = ToolsContainer()
Tools = [it.talk_with_user(),
         ft.create_file(), ft.read_file(), ft.search_replace(),
         st.delete_dir(), st.delete_file(), st.get_absolute_cur_path(), st.tree_file(), st.execute_command(),
         dt.read_word_document(), dt.extract_info_from_docx_table(),
         wt.fetch_webpage_with_selector(), wt.fetch_webpage()]
tools.load_tool(Tools)
docs_with_imgs = False  # 当read_word_document读取的内容有image时设为true，这时禁止使用structured output

def set_doc_with_imgs():
    global docs_with_imgs
    docs_with_imgs = True
    log("[Warning] Docs extracted with images! Structured LLM Output prohibited!")

# 初始化conversation(Memory)

system_prompt = prompt_react 
all_tools_prompt = tools.prompt_all_tools + Finish_prompt


class AgentCore:
    def __init__(self, model: Optional[str] = None):
        self.task = None
        self._sticky_model = model is not None
        if model is None:
            try:
                model = get_configured_model()
            except ValueError:
                model = "doubao-seed-1-6-thinking-250715"
        self.model = model
        self.UseModel = model
        
        self.Memory = MemoryContainer()
        self.Memory._add_system_prompt(system_prompt)
        self.Memory._add_tool_prompt(tool_prompt=all_tools_prompt)

    def refresh_model(self, force: bool = False) -> None:
        if self._sticky_model and not force:
            return
        try:
            configured = get_configured_model()
        except ValueError:
            return
        if configured and configured != self.model:
            self.model = configured
            self.UseModel = configured
        
    def _invoke_model(self, message: Union[str, list]) -> Any:
        self.refresh_model()
        alias = (self.model or "").lower()

        if "gpt" in alias or alias in {"openai"}:
            handler = api.get("gpt")
        elif "doubao" in alias:
            handler = api.get("Doubao") if docs_with_imgs else api.get("structured")
        else:
            handler = api.get("structured") if not docs_with_imgs else api.get("Doubao")

        if handler is None:
            raise RuntimeError("No available API handler for current configuration")
        return handler(message, self.Memory)


    def set_input(self, task: str):
        self.task = task
        
        
    def reset_conversation__(self):
        self.Memory.reset__()
        self.Memory._add_system_prompt(system_prompt)
        # print("conversation reset!")
        
    def load_conv(self, filename):
        self.Memory._load_conversation(filename)
        
        
    def compress_context__(self):
        print(len(self.Memory.tool_prompt["content"]), len(self.Memory.system_prompt["content"]), len(self.Memory.conversation))
        compressed_context = memory_compress__(self.Memory)
        self.Memory.reset__()
        self.Memory._add_tool_prompt(all_tools_prompt)
        self.Memory._add_system_prompt(system_prompt)
        self.Memory._add_assistant_message(compressed_context)
        
        

    def run(self, dialog: str):
        if self.task is None:
            raise Exception("None task!")


        from Agent.request.api import set_dialog
        set_dialog(dialog)
        
        input = self.task
        log(f"[task_start] model={self.model}\n{input}")
        
        response = self._invoke_model(input)


        think, text, func_call, func_args = parse_response(response)
        log(str(response))
        print('-' * 38, f"\n{BLUE}Assistant{RESET}: ", text)
        if func_call == "Finish":
            log(f"[task_finish]\n{text}")
            log("==================Finish Task====================")
            return
        
        
        while True:
            # print(f"calling {func_call} with {func_args}:\n y to confirm")
            # while input() != 'y':
            #     continue

            if func_call == "ParseFailure":
                observation = """
                你上次生成的回答格式有问题导致Agent无法成功解释，请查阅system_prompt，严格按照要求的输出格式重新输出:
                \nTracestack:\n
                """ + think
            else:
                print(f"{GREEN}calling tool{RESET}: {func_call}")
                observation =  tools.call_func(func_call, func_args)
            if isinstance(observation, str) and func_call != dt.read_word_document.__name__:
                log(f"[tool_result] {func_call}\n{observation}")
                
            # 这里可以进行记忆压缩的操作，但难点是什么时候进行压缩，如果Agent正在进行任务没理由压缩记忆，所以需要Agent自行判断是否要进行压缩，或者在任务完成后可以进行压缩
            
            if isinstance(observation, str):
                observation = f"observation after calling {func_call}:\n" + observation       
                     
            response = self._invoke_model(observation)

            think, text, func_call, func_args = parse_response(response)
            log(str(response))
            
            # print("my think: ", think)
            print('-' * 38, f"\n{BLUE}Assistant{RESET}: ", text)
            
            if func_call == "Finish":
                log(f"[task_finish]\n{text}")
                break
        log("==================Finish Task====================")
        # self.compress_context__()