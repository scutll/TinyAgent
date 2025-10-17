import json
import logging
from typing import Any, Dict, List

class ToolsContainer:
    def __init__(self):
        self.tools = dict()
        # 设置基础日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        logging.getLogger("httpx").setLevel(logging.WARNING)
    
    def load_tool(self, tool):
        """加载工具函数到容器中"""
        if not isinstance(tool, List):
            tool = [tool]
        for tl in tool:
            self.tools[tl.__name__] = tl
            self.logger.info(f"Tool loaded: {tl.__name__}")
    
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
            error_msg = f"Tool not found: {func_call}."
            # self.logger.error(error_msg)
            return error_msg
        
        func = self.tools[func_call]
        
        # 验证参数是否为字典类型
        if not isinstance(func_args, dict):
            error_msg = f"Invalid arguments type: {type(func_args)}. Expected dict."
            self.logger.error(error_msg)
            return error_msg
        
        self.logger.info(f"Calling tool: {func_call}")
        
        try:
            # 调用工具函数
            result = func(**func_args)
            # self.logger.info(f"Tool {func_call} executed successfully")
            return result
        except TypeError as e:
            # 参数类型错误
            error_msg = f"Parameter error in {func_call}: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
        except KeyError as e:
            # 参数键错误
            error_msg = f"Missing parameter in {func_call}: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
        except Exception as e:
            # 其他异常
            error_msg = f"Failed to run {func_call} with {func_args}: {str(e)}"
            self.logger.error(error_msg)
            return error_msg