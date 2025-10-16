"""
Memory Management Module
对话记录和思考-行动链管理模块

主要组件:
- MemoryManager: 核心记忆管理器
- ConversationStore: 对话记录存储
- ThoughtChain: 思考-行动链管理
- MemoryUtils: 记忆工具函数
"""

from .memory_manager import MemoryManager
from .conversation_store import ConversationStore
from .thought_chain import ThoughtChain
from .memory_utils import MemoryUtils

__all__ = [
    "MemoryManager",
    "ConversationStore", 
    "ThoughtChain",
    "MemoryUtils"
]

__version__ = "1.0.0"
__author__ = "Agent Memory Module"
__description__ = "Agent对话记录和思考-行动链管理模块"