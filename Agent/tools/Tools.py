from typing import Any, Dict, List

class ToolsContainer:
    def __init__(self):
        self.prompt_all_tools = "Below is a detailed description of all available tools. Each tool is defined in complete JSON Schema format, including its name, description, parameter definitions, output specifications, and usage recommendations. When invoking a tool, you must strictly follow the parameter requirements.\n"
        self.tools = dict()
        
    
    def load_tool(self, tool):
        """加载工具函数到容器中"""
        if not isinstance(tool, List):
            tool = [tool]
        for tl in tool:
            tool_name = tl.__class__.__name__
            self.tools[tool_name] = tl
            self.prompt_all_tools += tl.tool_prompt
    
    def call_func(self, func_call: str, func_args: Dict[str, Any]) -> Any:
        """
        调用指定工具函数
        
        Args:
            func_call: 工具函数名称
            func_args: 函数参数字典
            
        Returns:
            工具函数的执行结果或错误信息
        """
        # 检查工具是否存在
        if func_call not in self.tools:
            return f"Tool not found: {func_call}."
        
        func = self.tools[func_call]
        
        # 验证参数是否为字典类型
        if not isinstance(func_args, dict):
            return f"Invalid arguments type: {type(func_args)}. Expected dict."
        
        try:
            # 调用工具函数
            result = func(**func_args)
            return f"[from tool {func_call}]: " + str(result)
        except TypeError as e:
            # 参数类型错误
            error_msg = f"Parameter error in {func_call}: {str(e)}\n"
            return error_msg
        except KeyError as e:
            # 参数键错误
            error_msg = f"Missing parameter in {func_call}: {str(e)}\n"
            return error_msg
        except Exception as e:
            # 其他异常
            error_msg = f"Failed to run {func_call} with {func_args}: {str(e)}\n"
            return error_msg
        
        
class Tool_:
    def __init__(self, prompt: str):
        self.tool_prompt = prompt
        
    def __call__(self, *args, **kwargs) -> Any:
        pass 
    

# if __name__ == "__main__":
#     toolc = ToolsContainer()
#     from Agent.tools.docs_tools import read_word_document
#     iu = read_word_document()
#     toolc.load_tool(iu)
#     print(iu.tool_prompt)
#     print(toolc.call_func("read_word_document", {"path": r"C:\Users\mxl_scut\Desktop\anything\大物实验报告上下\物理实验报告（2022级学长）\大物上实验报告\数字示波器.docx"}))
    