# Memory Management Module

Agent对话记录和思考-行动链管理模块

## 概述

Memory模块是一个专门为Agent系统设计的记忆管理系统，负责：
- 持久化存储Agent与用户的对话历史
- 记录和管理Agent的思考-行动逻辑链条（ReAct循环）
- 提供会话分析、数据检索和导出功能
- 支持记忆数据的搜索和统计

## 功能特性

### 核心功能
- **对话记录管理**: 自动记录用户输入和Agent回复
- **思考链跟踪**: 完整记录Observation -> Think -> Response -> Action循环
- **会话管理**: 支持多会话隔离和数据组织
- **数据持久化**: 使用JSON文件存储，易于备份和迁移

### 高级功能
- **智能搜索**: 支持关键词搜索对话和思考记录
- **会话分析**: 自动生成会话摘要和统计信息
- **决策模式分析**: 分析Agent的行动模式和成功率
- **数据导出**: 支持会话数据的完整导出
- **自动清理**: 可配置的数据过期清理机制

## 安装和使用

### 基本使用

```python
from memory_manager import MemoryManager

# 初始化记忆管理器
memory = MemoryManager(storage_path="memory_data")

# 记录对话
memory.add_conversation_turn(
    session_id="session_001",
    user_input="请帮我分析项目",
    agent_response="我将开始分析项目结构"
)

# 记录思考链
memory.add_thought_chain(
    session_id="session_001",
    observation="用户请求分析项目",
    think="需要先了解项目结构",
    response="我将查看项目根目录",
    action="tree_file",
    action_input={"path": "."}
)

# 检索数据
conversations = memory.get_conversation_history("session_001")
thought_chains = memory.get_thought_chains("session_001")

# 搜索功能
results = memory.search_conversations("项目")
```

### 与Agent系统集成

```python
class EnhancedAgentCore:
    def __init__(self):
        self.memory = MemoryManager()
        self.current_session = self._generate_session_id()
    
    def process_user_input(self, user_input: str):
        # 原有的Agent处理逻辑
        agent_response = self._generate_response(user_input)
        
        # 记录对话
        self.memory.add_conversation_turn(
            self.current_session, user_input, agent_response
        )
        
        return agent_response
    
    def record_thought_process(self, observation, think, response, action, action_input):
        # 记录思考链
        self.memory.add_thought_chain(
            self.current_session, observation, think, response, action, action_input
        )
```

## 模块结构

```
Memory/
├── __init__.py              # 模块初始化
├── memory_manager.py        # 核心记忆管理器
├── conversation_store.py    # 对话记录存储
├── thought_chain.py         # 思考链管理
├── memory_utils.py          # 记忆工具函数
├── usage_example.py         # 使用示例
└── README.md               # 本文档
```

## API文档

### MemoryManager
核心管理类，提供统一的记忆管理接口。

#### 主要方法
- `add_conversation_turn()`: 添加对话记录
- `add_thought_chain()`: 添加思考链
- `get_conversation_history()`: 获取对话历史
- `get_thought_chains()`: 获取思考链
- `search_conversations()`: 搜索对话
- `get_session_summary()`: 获取会话摘要
- `export_session_data()`: 导出会话数据

### ConversationStore
专门负责对话记录的存储和管理。

#### 主要方法
- `add_turn()`: 添加对话轮次
- `get_history()`: 获取对话历史
- `search()`: 搜索对话记录
- `delete_session()`: 删除会话

### ThoughtChain
专门负责思考-行动链的记录和分析。

#### 主要方法
- `add_chain()`: 添加思考链
- `get_chains()`: 获取思考链
- `analyze_decision_patterns()`: 分析决策模式
- `export_thought_flow()`: 导出思考流程

### MemoryUtils
提供各种实用工具函数。

#### 主要方法
- `generate_session_summary()`: 生成会话摘要
- `backup_memory_data()`: 备份记忆数据
- `cleanup_old_data()`: 清理旧数据
- `validate_memory_data()`: 验证数据完整性

## 数据存储结构

记忆数据以JSON格式存储在指定目录中：

```
memory_data/
├── conversations/           # 对话记录
│   ├── session_001.json
│   └── session_002.json
├── thought_chains/         # 思考链记录
│   ├── session_001.json
│   └── session_002.json
└── backups/               # 备份数据（可选）
```

### 对话记录格式
```json
[
  {
    "record_id": "conv_1234567890",
    "session_id": "session_001",
    "timestamp": "2024-01-01T10:00:00",
    "user_input": "用户输入内容",
    "agent_response": "Agent回复内容",
    "metadata": {}
  }
]
```

### 思考链格式
```json
[
  {
    "chain_id": "chain_1234567890",
    "session_id": "session_001",
    "timestamp": "2024-01-01T10:00:00",
    "observation": "观察结果",
    "think": "思考过程",
    "response": "对用户的回复",
    "action": "执行的动作",
    "action_input": {},
    "metadata": {}
  }
]
```

## 与现有Agent系统集成

### 修改AgentCore类

在现有的`AgentCore`类中添加记忆管理功能：

```python
from Memory.memory_manager import MemoryManager

class AgentCore:
    def __init__(self):
        self.task = None
        self.cur_conv = None
        self.memory = MemoryManager()
        self.current_session = self._generate_session_id()
    
    def run(self):
        if self.task is None:
            raise Exception("None task!")
        
        # 记录初始对话
        self.memory.add_conversation_turn(
            self.current_session, self.task, "开始处理任务"
        )
        
        response = get_response_from_dsApi(self.task, conversation)
        think, text, func_call, func_args = parse_response(response)
        
        # 记录思考链
        self.memory.add_thought_chain(
            self.current_session,
            observation=self.task,
            think=think,
            response=text,
            action=func_call,
            action_input=func_args
        )
        
        while True:
            observation = tools.call_func(func_call, func_args)
            
            response = get_response_from_dsApi(observation, conversation)
            think, text, func_call, func_args = parse_response(response)
            
            # 记录每轮思考链
            self.memory.add_thought_chain(
                self.current_session,
                observation=observation,
                think=think,
                response=text,
                action=func_call,
                action_input=func_args
            )
            
            if func_call == "Finish":
                # 记录最终对话
                self.memory.add_conversation_turn(
                    self.current_session, "任务完成", text
                )
                break
```

### 会话ID生成

建议使用有意义的会话ID，便于后续检索：

```python
import time

def generate_session_id(self, task_description: str = "") -> str:
    """生成会话ID"""
    timestamp = int(time.time())
    task_hash = hash(task_description) % 10000 if task_description else "generic"
    return f"session_{timestamp}_{task_hash}"
```

## 性能考虑

- **存储效率**: 使用JSON格式，便于阅读和调试
- **搜索优化**: 简单的关键词匹配，适合中小规模数据
- **内存使用**: 按需加载会话数据，避免内存占用过大
- **扩展性**: 模块化设计，易于扩展新的存储后端

## 故障排除

### 常见问题

1. **导入错误**: 确保Memory目录在Python路径中
2. **权限错误**: 检查存储目录的写入权限
3. **数据损坏**: 使用`MemoryUtils.validate_memory_data()`验证数据完整性
4. **存储空间**: 定期使用`cleanup_old_data()`清理旧数据

### 调试技巧

- 使用`usage_example.py`测试基本功能
- 检查生成的JSON文件格式
- 使用搜索功能验证数据存储
- 查看统计信息了解系统状态

## 扩展开发

### 添加新的存储后端

可以扩展支持数据库存储：

```python
class DatabaseConversationStore(ConversationStore):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def add_turn(self, session_id, user_input, agent_response, metadata):
        # 实现数据库存储逻辑
        pass
```

### 添加新的分析功能

可以扩展分析功能：

```python
class AdvancedThoughtAnalyzer:
    def analyze_learning_patterns(self, session_id):
        # 实现学习模式分析
        pass
```

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个模块。