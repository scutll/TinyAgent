# -*- coding: utf-8 -*-
from Agent.Core.agent_core import AgentCore
import os

agent = AgentCore()
agent.set_input("docs文件夹里面有我的java作业文档，你帮我进行阅读并完成代码作业，每个作业保存到一个新开的文件里面，全部放在docs文件夹里面，然后写一个运行指南教我如何运行全部代码, 生成代码的时候一定要使用工具在docs目录里面创建文件，文件名你可以自己决定")
agent.run()