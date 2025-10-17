class promptHandler:
    
    def __init__(self) -> None:
        self.prompt_think_ = ""
        self.prompt_tools_ = ""

    def _set_think_prompt_(self, prompt: str):
        self.prompt_think_ = prompt

    def _add_tool_to_prompt(self, tool_: str):
        self.prompt_tools = self.prompt_tools + "\n\n" + tool_
        
        
    def prompt_template(self):
        return self.prompt_think_ + self.prompt_tools_