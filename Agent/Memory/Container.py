from typing import Any, List, Union


class MemoryContainer:
    def __init__(self, conversation=[]):
        self.system_prompt = {"role": "system", "content": ""}
        self.tool_prompt = {"role": "system", "content": ""}
        self.conversation = conversation
        
    def reset__(self):
        self.conversation = []
        self.system_prompt = {"role": "system", "content": ""}
        self.tool_prompt = {"role": "system", "content": ""}
        
        
    def _add_tool_message(self, message: Union[str, List]):
        self.conversation.append({"role": "tool", "content": message})
        
    def _add_user_message(self, message: Union[str, List], tool_role=False):
        self.conversation.append({"role": "tool" if tool_role else "user", "content": message})
        
    def _add_assistant_message(self, message: str):
        self.conversation.append({"role": "assistant", "content": message})
        
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
        return [self._system_prompt()] + [self._tool_prompt()] + self.conversation
    
    
    def _user_conversation(self) -> List:
        return self.conversation
    
    
    
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