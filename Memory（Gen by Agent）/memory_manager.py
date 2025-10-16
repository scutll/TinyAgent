"""
Memory Manager - 核心记忆管理模块
负责对话历史、思考链的存储、检索和管理
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from .conversation_store import ConversationStore
from .thought_chain import ThoughtChain
from .memory_utils import MemoryUtils


class MemoryManager:
    """记忆管理器 - 核心管理类"""
    
    def __init__(self, storage_path: str = "memory_data"):
        """
        初始化记忆管理器
        
        Args:
            storage_path: 数据存储路径
        """
        self.storage_path = storage_path
        self.conversation_store = ConversationStore(storage_path)
        self.thought_chain = ThoughtChain(storage_path)
        self.utils = MemoryUtils(storage_path)
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
    
    def add_conversation_turn(self, 
                            session_id: str,
                            user_input: str,
                            agent_response: str,
                            metadata: Optional[Dict] = None) -> str:
        """
        添加一轮对话记录
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            agent_response: Agent回复
            metadata: 额外元数据
            
        Returns:
            记录ID
        """
        return self.conversation_store.add_turn(
            session_id, user_input, agent_response, metadata
        )
    
    def add_thought_chain(self,
                         session_id: str,
                         observation: str,
                         think: str,
                         response: str,
                         action: str,
                         action_input: Dict,
                         metadata: Optional[Dict] = None) -> str:
        """
        添加思考-行动链记录
        
        Args:
            session_id: 会话ID
            observation: 观察结果
            think: 思考过程
            response: 对用户的回复
            action: 执行的动作
            action_input: 动作输入参数
            metadata: 额外元数据
            
        Returns:
            链ID
        """
        return self.thought_chain.add_chain(
            session_id, observation, think, response, action, action_input, metadata
        )
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            limit: 返回记录数量限制
            
        Returns:
            对话历史列表
        """
        return self.conversation_store.get_history(session_id, limit)
    
    def get_thought_chains(self, session_id: str, limit: int = 20) -> List[Dict]:
        """
        获取思考链历史
        
        Args:
            session_id: 会话ID
            limit: 返回记录数量限制
            
        Returns:
            思考链列表
        """
        return self.thought_chain.get_chains(session_id, limit)
    
    def search_conversations(self, query: str, session_id: Optional[str] = None) -> List[Dict]:
        """
        搜索对话记录
        
        Args:
            query: 搜索关键词
            session_id: 可选会话ID过滤
            
        Returns:
            匹配的对话记录
        """
        return self.conversation_store.search(query, session_id)
    
    def search_thoughts(self, query: str, session_id: Optional[str] = None) -> List[Dict]:
        """
        搜索思考记录
        
        Args:
            query: 搜索关键词
            session_id: 可选会话ID过滤
            
        Returns:
            匹配的思考记录
        """
        return self.thought_chain.search(query, session_id)
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        获取会话摘要
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话摘要信息
        """
        return self.utils.generate_session_summary(session_id)
    
    def export_session_data(self, session_id: str, export_path: str) -> bool:
        """
        导出会话数据
        
        Args:
            session_id: 会话ID
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        return self.utils.export_session(session_id, export_path)
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        清理过期会话
        
        Args:
            days: 保留天数
            
        Returns:
            清理的会话数量
        """
        return self.utils.cleanup_old_data(days)
    
    def get_statistics(self) -> Dict:
        """
        获取记忆统计信息
        
        Returns:
            统计信息字典
        """
        return self.utils.get_statistics()