"""
Thought Chain - 思考-行动链管理模块
负责记录和管理Agent的思考过程、行动决策和观察结果
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import re


class ThoughtChain:
    """思考链管理器"""
    
    def __init__(self, storage_path: str):
        """
        初始化思考链管理器
        
        Args:
            storage_path: 存储路径
        """
        self.storage_path = storage_path
        self.thoughts_dir = os.path.join(storage_path, "thought_chains")
        os.makedirs(self.thoughts_dir, exist_ok=True)
    
    def add_chain(self,
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
        # 生成链ID
        chain_id = f"chain_{int(time.time() * 1000)}"
        
        # 构建链数据
        chain_data = {
            "chain_id": chain_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "observation": observation,
            "think": think,
            "response": response,
            "action": action,
            "action_input": action_input,
            "metadata": metadata or {}
        }
        
        # 保存链记录
        self._save_chain(session_id, chain_data)
        
        return chain_id
    
    def get_chains(self, session_id: str, limit: int = 20) -> List[Dict]:
        """
        获取思考链历史
        
        Args:
            session_id: 会话ID
            limit: 返回记录数量限制
            
        Returns:
            思考链列表
        """
        session_file = self._get_session_file(session_id)
        
        if not os.path.exists(session_file):
            return []
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                chains = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        
        # 按时间戳排序并限制数量
        chains.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return chains[:limit]
    
    def get_complete_session_flow(self, session_id: str) -> List[Dict]:
        """
        获取完整会话流程（按执行顺序）
        
        Args:
            session_id: 会话ID
            
        Returns:
            按执行顺序排列的思考链
        """
        chains = self.get_chains(session_id, limit=1000)
        # 按时间戳正序排列（最早的在前）
        chains.sort(key=lambda x: x.get('timestamp', ''))
        return chains
    
    def search(self, query: str, session_id: Optional[str] = None) -> List[Dict]:
        """
        搜索思考记录
        
        Args:
            query: 搜索关键词
            session_id: 可选会话ID过滤
            
        Returns:
            匹配的思考记录
        """
        results = []
        
        if session_id:
            # 搜索特定会话
            session_file = self._get_session_file(session_id)
            if os.path.exists(session_file):
                chains = self.get_chains(session_id, limit=1000)
                results.extend(self._search_in_chains(chains, query))
        else:
            # 搜索所有会话
            for filename in os.listdir(self.thoughts_dir):
                if filename.endswith('.json'):
                    sess_id = filename[:-5]  # 移除.json后缀
                    chains = self.get_chains(sess_id, limit=1000)
                    results.extend(self._search_in_chains(chains, query))
        
        # 按时间戳排序
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results
    
    def analyze_decision_patterns(self, session_id: str) -> Dict:
        """
        分析决策模式
        
        Args:
            session_id: 会话ID
            
        Returns:
            决策模式分析结果
        """
        chains = self.get_chains(session_id, limit=1000)
        
        if not chains:
            return {"error": "No thought chains found for this session"}
        
        # 统计动作类型
        action_counts = {}
        action_success = {}
        
        for chain in chains:
            action = chain.get('action', '')
            if action:
                action_counts[action] = action_counts.get(action, 0) + 1
                
                # 简单判断是否成功（基于observation中是否包含error）
                observation = chain.get('observation', '').lower()
                is_success = 'error' not in observation
                
                if action not in action_success:
                    action_success[action] = {'success': 0, 'total': 0}
                
                action_success[action]['total'] += 1
                if is_success:
                    action_success[action]['success'] += 1
        
        # 计算思考长度
        think_lengths = [len(chain.get('think', '')) for chain in chains]
        avg_think_length = sum(think_lengths) / len(think_lengths) if think_lengths else 0
        
        return {
            "total_chains": len(chains),
            "action_distribution": action_counts,
            "action_success_rates": {
                action: {
                    "success_rate": data['success'] / data['total'] if data['total'] > 0 else 0,
                    "success_count": data['success'],
                    "total_count": data['total']
                }
                for action, data in action_success.items()
            },
            "thinking_analysis": {
                "average_think_length": avg_think_length,
                "max_think_length": max(think_lengths) if think_lengths else 0,
                "min_think_length": min(think_lengths) if think_lengths else 0
            },
            "session_duration": self._calculate_session_duration(chains)
        }
    
    def export_thought_flow(self, session_id: str, export_path: str) -> bool:
        """
        导出思考流程
        
        Args:
            session_id: 会话ID
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        chains = self.get_complete_session_flow(session_id)
        
        if not chains:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                # 生成可读的思考流程报告
                report = self._generate_thought_flow_report(chains)
                f.write(report)
            return True
        except Exception:
            return False
    
    def _save_chain(self, session_id: str, chain_data: Dict):
        """保存链记录到文件"""
        session_file = self._get_session_file(session_id)
        
        # 读取现有记录
        chains = []
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    chains = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                chains = []
        
        # 添加新记录
        chains.append(chain_data)
        
        # 保存记录
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(chains, f, ensure_ascii=False, indent=2)
    
    def _get_session_file(self, session_id: str) -> str:
        """获取会话文件路径"""
        # 清理session_id中的非法字符
        safe_session_id = re.sub(r'[^a-zA-Z0-9_-]', '_', session_id)
        return os.path.join(self.thoughts_dir, f"{safe_session_id}.json")
    
    def _search_in_chains(self, chains: List[Dict], query: str) -> List[Dict]:
        """在链列表中搜索关键词"""
        results = []
        query_lower = query.lower()
        
        for chain in chains:
            # 搜索观察、思考、动作等字段
            observation = chain.get('observation', '').lower()
            think = chain.get('think', '').lower()
            response = chain.get('response', '').lower()
            action = chain.get('action', '').lower()
            
            if (query_lower in observation or 
                query_lower in think or 
                query_lower in response or
                query_lower in action):
                results.append(chain)
        
        return results
    
    def _calculate_session_duration(self, chains: List[Dict]) -> Dict:
        """计算会话持续时间"""
        if not chains:
            return {"start": None, "end": None, "duration_seconds": 0}
        
        # 按时间戳排序
        sorted_chains = sorted(chains, key=lambda x: x.get('timestamp', ''))
        
        start_time = sorted_chains[0].get('timestamp')
        end_time = sorted_chains[-1].get('timestamp')
        
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration = (end_dt - start_dt).total_seconds()
        else:
            duration = 0
        
        return {
            "start": start_time,
            "end": end_time,
            "duration_seconds": duration
        }
    
    def _generate_thought_flow_report(self, chains: List[Dict]) -> str:
        """生成思考流程报告"""
        report = []
        report.append("=" * 80)
        report.append("AGENT THOUGHT FLOW ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nTotal Steps: {len(chains)}")
        report.append(f"Session ID: {chains[0].get('session_id', 'Unknown') if chains else 'Unknown'}")
        report.append("\n" + "=" * 80 + "\n")
        
        for i, chain in enumerate(chains, 1):
            report.append(f"STEP {i}:")
            report.append("-" * 40)
            report.append(f"Timestamp: {chain.get('timestamp', 'Unknown')}")
            report.append(f"\nObservation:\n{chain.get('observation', '')}")
            report.append(f"\nThink:\n{chain.get('think', '')}")
            report.append(f"\nResponse:\n{chain.get('response', '')}")
            report.append(f"\nAction: {chain.get('action', '')}")
            report.append(f"Action Input: {json.dumps(chain.get('action_input', {}), indent=2, ensure_ascii=False)}")
            report.append("\n" + "=" * 80 + "\n")
        
        return "\n".join(report)
    
    def get_statistics(self) -> Dict:
        """
        获取思考链统计信息
        
        Returns:
            统计信息字典
        """
        sessions = []
        for filename in os.listdir(self.thoughts_dir):
            if filename.endswith('.json'):
                sessions.append(filename[:-5])
        
        total_chains = 0
        for session_id in sessions:
            chains = self.get_chains(session_id, limit=10000)
            total_chains += len(chains)
        
        return {
            "total_sessions_with_thoughts": len(sessions),
            "total_thought_chains": total_chains,
            "storage_path": self.thoughts_dir
        }