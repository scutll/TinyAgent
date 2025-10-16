"""
Conversation Store - 对话记录存储模块
负责对话历史的持久化存储、检索和管理
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import re


class ConversationStore:
    """对话存储管理器"""
    
    def __init__(self, storage_path: str):
        """
        初始化对话存储
        
        Args:
            storage_path: 存储路径
        """
        self.storage_path = storage_path
        self.conversations_dir = os.path.join(storage_path, "conversations")
        os.makedirs(self.conversations_dir, exist_ok=True)
    
    def add_turn(self, 
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
        # 生成记录ID
        record_id = f"conv_{int(time.time() * 1000)}"
        
        # 构建记录数据
        record_data = {
            "record_id": record_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }
        
        # 保存记录
        self._save_record(session_id, record_data)
        
        return record_id
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """
        获取会话历史
        
        Args:
            session_id: 会话ID
            limit: 返回记录数量限制
            
        Returns:
            对话历史列表
        """
        session_file = self._get_session_file(session_id)
        
        if not os.path.exists(session_file):
            return []
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        
        # 按时间戳排序并限制数量
        records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return records[:limit]
    
    def search(self, query: str, session_id: Optional[str] = None) -> List[Dict]:
        """
        搜索对话记录
        
        Args:
            query: 搜索关键词
            session_id: 可选会话ID过滤
            
        Returns:
            匹配的对话记录
        """
        results = []
        
        if session_id:
            # 搜索特定会话
            session_file = self._get_session_file(session_id)
            if os.path.exists(session_file):
                records = self.get_history(session_id, limit=1000)
                results.extend(self._search_in_records(records, query))
        else:
            # 搜索所有会话
            for filename in os.listdir(self.conversations_dir):
                if filename.endswith('.json'):
                    sess_id = filename[:-5]  # 移除.json后缀
                    records = self.get_history(sess_id, limit=1000)
                    results.extend(self._search_in_records(records, query))
        
        # 按相关性排序
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results
    
    def get_session_list(self) -> List[str]:
        """
        获取所有会话ID列表
        
        Returns:
            会话ID列表
        """
        sessions = []
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                sessions.append(filename[:-5])  # 移除.json后缀
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        session_file = self._get_session_file(session_id)
        
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                return True
            except OSError:
                return False
        return False
    
    def _save_record(self, session_id: str, record_data: Dict):
        """保存记录到文件"""
        session_file = self._get_session_file(session_id)
        
        # 读取现有记录
        records = []
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                records = []
        
        # 添加新记录
        records.append(record_data)
        
        # 保存记录
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def _get_session_file(self, session_id: str) -> str:
        """获取会话文件路径"""
        # 清理session_id中的非法字符
        safe_session_id = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
        return os.path.join(self.conversations_dir, f"{safe_session_id}.json")
    
    def _search_in_records(self, records: List[Dict], query: str) -> List[Dict]:
        """在记录列表中搜索关键词"""
        results = []
        query_lower = query.lower()
        
        for record in records:
            # 搜索用户输入和Agent回复
            user_input = record.get('user_input', '').lower()
            agent_response = record.get('agent_response', '').lower()
            
            if (query_lower in user_input or 
                query_lower in agent_response):
                results.append(record)
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        获取对话存储统计信息
        
        Returns:
            统计信息字典
        """
        sessions = self.get_session_list()
        total_records = 0
        
        for session_id in sessions:
            records = self.get_history(session_id, limit=10000)
            total_records += len(records)
        
        return {
            "total_sessions": len(sessions),
            "total_conversations": total_records,
            "storage_path": self.conversations_dir
        }