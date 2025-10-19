from Agent.Core.agent_core import AgentCore
agent = AgentCore(UseModel="Doubao")
agent.set_task("""
从网络搜索FDU的信息并帮我写入到docs文件夹里面
               """)
agent.run()