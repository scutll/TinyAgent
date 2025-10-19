from typing import Any, List, Union


class MemoryContainer:
    def __init__(self, conversation=[]):
        self.conversation = conversation
        
    def reset__(self):
        self.conversation = []
        
        
    def _add_tool_message(self, message: Union[str, List]):
        self.conversation.append({"role": "tool", "content": message})
        
    def _add_user_message(self, message: Union[str, List]):
        self.conversation.append({"role": "user", "content": message})
        
    def _add_assistant_message(self, message: str):
        self.conversation.append({"role": "assistant", "content": message})
        
    def _add_prompt(self, system_prompt):
        self.conversation.append({"role": "system", "content": system_prompt})
        
    def __call__(self) -> List:
        return self.conversation