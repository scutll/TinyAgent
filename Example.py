# -*- coding: utf-8 -*-
from Agent.Core.agent_core import AgentCore
import os

agent = AgentCore(model="deepseek-chat")
agent.set_task("帮我查询当前git仓库情况和当前环境的pip安装列表，在docs文件夹里面创建一个新文件写道里面")
agent.run()