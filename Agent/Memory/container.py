from datetime import datetime
import json
import os
from Agent.utils.logging_ import log
from typing import Any, List, Union


class MemoryContainer:
    def __init__(self):
        self.system_prompt = {"role": "system", "content": ""}
        self.tool_prompt = {"role": "system", "content": ""}
        self.conversation = []
        self.history_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "history"
        )
        os.makedirs(self.history_dir, exist_ok=True)

        
    def reset__(self):
        self.conversation = []
        self.system_prompt = {"role": "system", "content": ""}
        # self.tool_prompt = {"role": "system", "content": ""}
        
        
        
    def _add_user_message(self, message: Union[str, List]):
        message_block = {"role": "user", "content": message}
        self.conversation.append({
            "type": "user message",
            "time": datetime.now().strftime("%m%d-%H%M"),
            "content" : message_block
        })
        
    def _pop_message(self):
        if len(self.conversation):
            self.conversation.pop()
        
    def _add_assistant_message(self, message: str):
        message_block = {"role": "assistant", "content": message}
        self.conversation.append({
            "type": "assistant message",
            "time": datetime.now().strftime("%m%d-%H%M"),
            "content" : message_block
        })
        
    def _get_conversation(self) -> List:
        conv = []
        for item in self.conversation:
            conv.append(item["content"])
        return conv
        
    def _add_system_prompt(self, system_prompt):
        if self.system_prompt is None:
            self.system_prompt = {"role": "system", "content": system_prompt}
        else:
            original_prompt = self.system_prompt["content"]
            self.system_prompt={"role": "system", "content": original_prompt + system_prompt}
        
    def _add_tool_prompt(self, tool_prompt):
        if self.tool_prompt is None:
            self.tool_prompt = {"role": "system", "content": tool_prompt}
        else:
            original_prompt = self.tool_prompt["content"]
            self.tool_prompt = {"role": "system", "content": original_prompt + tool_prompt}
        
    def __call__(self) -> List:
        return [self._system_prompt()] + [self._tool_prompt()] + self._get_conversation()
    
    
    def _tool_prompt(self) -> dict:
        return self.tool_prompt
    
    
    
    def _system_prompt(self) -> dict:
        return self.system_prompt
    
    
    
    def _len_user_conversation__(self) -> int:
        return len(str(self.conversation))
    
    
    
    
    def _len_system_prompt__(self) -> int:
        return len(str(self.system_prompt))
    
    
    
    def _len_tool_prompt(self) -> int:
        return len(str(self.tool_prompt))
    
    
    
    def _load_conversation(self, filename:str):
        
        file_path = os.path.join(self.history_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.conversation = data.get("conversation", [])
            log(f"[INFO] Conversation loaded from '{file_path}'")
            # print(f"conversation loaded from {filename}")
        else:
            log(f"[ERROR] History file '{file_path}' not found. No conversation loaded.")
            # print(f"failed to load {filename}: not a file")
    
    
    def _save_conversation(self, filename:str, save_name = None):
        """
        保存当前 conversation 到 history 目录下的文件
        """
        filename += ".json"
        file_path = os.path.join(self.history_dir, filename)

        timestamp = datetime.now().strftime("%m%d-%H%M")
        data_to_save = {
            "save_time": timestamp,
            "conv_name": save_name if save_name is not None else "Not named",
            "conversation": self.conversation
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        log(f"[INFO] Conversation saved to '{file_path}'")