"""
Memory Module Usage Example
Memory管理模块使用示例

展示如何使用Memory模块记录对话和思考链，以及如何检索和分析数据
"""

import os
import sys

# 添加当前目录到Python路径，以便导入Memory模块
sys.path.append(os.path.dirname(__file__))

from memory_manager import MemoryManager


def basic_usage_example():
    """基本使用示例"""
    print("=== Memory Module Basic Usage Example ===\n")
    
    # 初始化记忆管理器
    memory = MemoryManager(storage_path="memory_data")
    
    # 示例会话ID
    session_id = "example_session_001"
    
    # 1. 记录对话
    print("1. Recording conversations...")
    memory.add_conversation_turn(
        session_id=session_id,
        user_input="请帮我分析这个项目文件夹",
        agent_response="我将先查看项目结构，了解现有代码组织方式。",
        metadata={"task_type": "file_analysis"}
    )
    
    memory.add_conversation_turn(
        session_id=session_id,
        user_input="好的，请继续",
        agent_response="正在分析项目结构，发现包含Agent、LLM等模块。",
        metadata={"step": 2}
    )
    
    # 2. 记录思考链
    print("2. Recording thought chains...")
    memory.add_thought_chain(
        session_id=session_id,
        observation="用户请求分析项目文件夹",
        think="需要先了解项目结构，然后设计合适的分析策略",
        response="我将先查看项目结构",
        action="list_file",
        action_input={"path": "."},
        metadata={"step": 1}
    )
    
    memory.add_thought_chain(
        session_id=session_id,
        observation="项目结构已展示，包含多个模块",
        think="需要进一步分析Agent模块的具体实现",
        response="我将查看Agent核心代码",
        action="read_file",
        action_input={"path": "Agent/agent_core.py"},
        metadata={"step": 2}
    )
    
    # 3. 检索数据
    print("3. Retrieving stored data...")
    
    # 获取对话历史
    conversations = memory.get_conversation_history(session_id)
    print(f"Retrieved {len(conversations)} conversations")
    
    # 获取思考链
    thought_chains = memory.get_thought_chains(session_id)
    print(f"Retrieved {len(thought_chains)} thought chains")
    
    # 4. 生成会话摘要
    print("4. Generating session summary...")
    summary = memory.get_session_summary(session_id)
    print(f"Session Summary: {summary.get('summary', {})}")
    
    # 5. 搜索功能
    print("5. Testing search functionality...")
    search_results = memory.search_conversations("项目", session_id)
    print(f"Found {len(search_results)} conversations containing '项目'")
    
    # 6. 获取统计信息
    print("6. Getting statistics...")
    stats = memory.get_statistics()
    print(f"Total conversations: {stats.get('conversation_statistics', {}).get('total_conversations', 0)}")
    print(f"Total thought chains: {stats.get('thought_chain_statistics', {}).get('total_thought_chains', 0)}")
    
    print("\n=== Basic Example Completed ===")


def integration_with_agent_example():
    """与Agent系统集成示例"""
    print("\n=== Integration with Agent System Example ===\n")
    
    # 模拟Agent核心类的增强版本
    class EnhancedAgentCore:
        def __init__(self):
            self.memory = MemoryManager()
            self.current_session = f"session_{int(os.times().elapsed)}"
            self.task = None
        
        def set_task(self, task: str):
            self.task = task
        
        def record_conversation_turn(self, user_input: str, agent_response: str):
            """记录对话轮次"""
            self.memory.add_conversation_turn(
                session_id=self.current_session,
                user_input=user_input,
                agent_response=agent_response,
                metadata={
                    "task": self.task,
                    "timestamp": os.times().elapsed
                }
            )
        
        def record_thought_chain(self, observation: str, think: str, response: str, 
                               action: str, action_input: dict):
            """记录思考链"""
            self.memory.add_thought_chain(
                session_id=self.current_session,
                observation=observation,
                think=think,
                response=response,
                action=action,
                action_input=action_input,
                metadata={
                    "task": self.task,
                    "step_timestamp": os.times().elapsed
                }
            )
        
        def get_session_analysis(self):
            """获取会话分析"""
            return self.memory.get_session_summary(self.current_session)
        
        def export_session_data(self, export_path: str):
            """导出会话数据"""
            return self.memory.export_session_data(self.current_session, export_path)
    
    # 使用示例
    agent = EnhancedAgentCore()
    agent.set_task("分析项目结构")
    
    # 模拟对话记录
    agent.record_conversation_turn(
        "请分析这个项目",
        "我将开始分析项目结构"
    )
    
    # 模拟思考链记录
    agent.record_thought_chain(
        observation="用户请求分析项目",
        think="需要先了解整体结构，然后深入分析关键模块",
        response="我将查看项目根目录",
        action="tree_file",
        action_input={"path": "."}
    )
    
    # 获取分析结果
    analysis = agent.get_session_analysis()
    print(f"Session Analysis: {analysis}")
    
    print("\n=== Integration Example Completed ===")


def advanced_features_example():
    """高级功能示例"""
    print("\n=== Advanced Features Example ===\n")
    
    memory = MemoryManager()
    
    # 1. 决策模式分析
    print("1. Decision pattern analysis...")
    # 需要先有一些思考链数据
    session_id = "analysis_session"
    
    # 添加一些示例思考链
    for i in range(5):
        memory.add_thought_chain(
            session_id=session_id,
            observation=f"Observation {i}",
            think=f"Thinking step {i}",
            response=f"Response {i}",
            action="read_file" if i % 2 == 0 else "list_file",
            action_input={"path": f"file_{i}.txt"}
        )
    
    # 分析决策模式
    from thought_chain import ThoughtChain
    thought_analyzer = ThoughtChain("memory_data")
    patterns = thought_analyzer.analyze_decision_patterns(session_id)
    print(f"Decision patterns: {patterns}")
    
    # 2. 数据导出
    print("2. Data export...")
    export_success = memory.export_session_data(session_id, "exported_session.json")
    print(f"Export successful: {export_success}")
    
    # 3. 数据清理
    print("3. Data cleanup...")
    # 注意：在实际使用中要小心，这里只是演示
    # cleaned = memory.cleanup_old_sessions(days=0)  # 这会删除所有数据
    # print(f"Cleaned {cleaned} old sessions")
    
    print("\n=== Advanced Features Example Completed ===")


if __name__ == "__main__":
    # 运行所有示例
    basic_usage_example()
    integration_with_agent_example()
    advanced_features_example()
    
    print("\n" + "="*50)
    print("All Memory Module Examples Completed Successfully!")
    print("="*50)