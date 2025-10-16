"""
Memory Utils - 记忆工具模块
提供各种实用功能和工具函数来支持Memory管理
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import shutil


class MemoryUtils:
    """记忆工具类"""
    
    def __init__(self, storage_path: str):
        """
        初始化记忆工具
        
        Args:
            storage_path: 存储路径
        """
        self.storage_path = storage_path
    
    def generate_session_summary(self, session_id: str) -> Dict:
        """
        生成会话摘要
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话摘要信息
        """
        from .conversation_store import ConversationStore
        from .thought_chain import ThoughtChain
        
        conv_store = ConversationStore(self.storage_path)
        thought_chain = ThoughtChain(self.storage_path)
        
        # 获取对话和思考链
        conversations = conv_store.get_history(session_id, limit=1000)
        thought_chains = thought_chain.get_chains(session_id, limit=1000)
        
        if not conversations and not thought_chains:
            return {"error": "Session not found or empty"}
        
        # 计算基本统计
        total_conversations = len(conversations)
        total_thought_chains = len(thought_chains)
        
        # 分析对话内容
        user_inputs = [conv.get('user_input', '') for conv in conversations]
        agent_responses = [conv.get('agent_response', '') for conv in conversations]
        
        # 分析动作类型
        actions = []
        for chain in thought_chains:
            action = chain.get('action', '')
            if action:
                actions.append(action)
        
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # 计算会话时间范围
        all_timestamps = []
        for conv in conversations:
            if 'timestamp' in conv:
                all_timestamps.append(conv['timestamp'])
        for chain in thought_chains:
            if 'timestamp' in chain:
                all_timestamps.append(chain['timestamp'])
        
        if all_timestamps:
            sorted_timestamps = sorted(all_timestamps)
            start_time = sorted_timestamps[0]
            end_time = sorted_timestamps[-1]
            
            # 计算持续时间
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration = (end_dt - start_dt).total_seconds()
        else:
            start_time = end_time = None
            duration = 0
        
        # 生成关键主题（简单的关键词提取）
        all_text = ' '.join(user_inputs + agent_responses)
        keywords = self._extract_keywords(all_text)
        
        return {
            "session_id": session_id,
            "summary": {
                "total_conversations": total_conversations,
                "total_thought_chains": total_thought_chains,
                "session_duration_seconds": duration,
                "start_time": start_time,
                "end_time": end_time,
                "average_conversation_length": self._calculate_average_length(user_inputs + agent_responses),
                "key_topics": keywords[:10],  # 取前10个关键词
                "action_distribution": action_counts
            },
            "first_user_input": user_inputs[0] if user_inputs else None,
            "last_agent_response": agent_responses[-1] if agent_responses else None,
            "most_common_action": max(action_counts, key=action_counts.get) if action_counts else None
        }
    
    def export_session(self, session_id: str, export_path: str) -> bool:
        """
        导出会话数据
        
        Args:
            session_id: 会话ID
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        from .conversation_store import ConversationStore
        from .thought_chain import ThoughtChain
        
        conv_store = ConversationStore(self.storage_path)
        thought_chain = ThoughtChain(self.storage_path)
        
        # 获取所有数据
        conversations = conv_store.get_history(session_id, limit=10000)
        thought_chains = thought_chain.get_chains(session_id, limit=10000)
        
        if not conversations and not thought_chains:
            return False
        
        # 构建导出数据
        export_data = {
            "session_id": session_id,
            "export_timestamp": datetime.now().isoformat(),
            "conversations": conversations,
            "thought_chains": thought_chains,
            "summary": self.generate_session_summary(session_id)
        }
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """
        清理过期数据
        
        Args:
            days: 保留天数
            
        Returns:
            清理的文件数量
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        # 清理对话数据
        conv_dir = os.path.join(self.storage_path, "conversations")
        if os.path.exists(conv_dir):
            cleaned_count += self._cleanup_old_files(conv_dir, cutoff_time)
        
        # 清理思考链数据
        thoughts_dir = os.path.join(self.storage_path, "thought_chains")
        if os.path.exists(thoughts_dir):
            cleaned_count += self._cleanup_old_files(thoughts_dir, cutoff_time)
        
        return cleaned_count
    
    def get_statistics(self) -> Dict:
        """
        获取记忆统计信息
        
        Returns:
            统计信息字典
        """
        from .conversation_store import ConversationStore
        from .thought_chain import ThoughtChain
        
        conv_store = ConversationStore(self.storage_path)
        thought_chain = ThoughtChain(self.storage_path)
        
        conv_stats = conv_store.get_statistics()
        thought_stats = thought_chain.get_statistics()
        
        # 计算存储空间使用
        total_size = self._calculate_storage_size()
        
        return {
            "conversation_statistics": conv_stats,
            "thought_chain_statistics": thought_stats,
            "storage_usage": {
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "storage_path": self.storage_path
            },
            "system_info": {
                "current_time": datetime.now().isoformat(),
                "python_version": "3.8+",
                "memory_module_version": "1.0.0"
            }
        }
    
    def backup_memory_data(self, backup_path: str) -> bool:
        """
        备份记忆数据
        
        Args:
            backup_path: 备份路径
            
        Returns:
            是否备份成功
        """
        try:
            if os.path.exists(backup_path):
                # 如果备份路径已存在，创建带时间戳的子目录
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(backup_path, f"memory_backup_{timestamp}")
            
            shutil.copytree(self.storage_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def restore_memory_data(self, backup_path: str) -> bool:
        """
        恢复记忆数据
        
        Args:
            backup_path: 备份路径
            
        Returns:
            是否恢复成功
        """
        try:
            # 删除现有数据
            if os.path.exists(self.storage_path):
                shutil.rmtree(self.storage_path)
            
            # 恢复备份数据
            shutil.copytree(backup_path, self.storage_path)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词（简单实现）"""
        # 移除标点符号和转换为小写
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    def _calculate_average_length(self, texts: List[str]) -> float:
        """计算平均文本长度"""
        if not texts:
            return 0.0
        total_length = sum(len(text) for text in texts)
        return total_length / len(texts)
    
    def _cleanup_old_files(self, directory: str, cutoff_time: datetime) -> int:
        """清理目录中的旧文件"""
        cleaned_count = 0
        
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                
                # 获取文件修改时间
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except OSError:
                        continue
        
        return cleaned_count
    
    def _calculate_storage_size(self) -> int:
        """计算存储空间使用"""
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(self.storage_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        
        return total_size
    
    def validate_memory_data(self) -> Dict:
        """
        验证记忆数据的完整性
        
        Returns:
            验证结果
        """
        issues = []
        
        # 检查存储目录
        if not os.path.exists(self.storage_path):
            issues.append("Storage path does not exist")
        
        # 检查对话数据目录
        conv_dir = os.path.join(self.storage_path, "conversations")
        if os.path.exists(conv_dir):
            # 检查JSON文件格式
            issues.extend(self._validate_json_files(conv_dir))
        
        # 检查思考链数据目录
        thoughts_dir = os.path.join(self.storage_path, "thought_chains")
        if os.path.exists(thoughts_dir):
            issues.extend(self._validate_json_files(thoughts_dir))
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "checked_at": datetime.now().isoformat()
        }
    
    def _validate_json_files(self, directory: str) -> List[str]:
        """验证目录中的JSON文件"""
        issues = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON in {filename}: {e}")
                except Exception as e:
                    issues.append(f"Error reading {filename}: {e}")
        
        return issues