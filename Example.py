from Agent.agent_core import AgentCore
agent = AgentCore(UseModel="Deepseek")
agent.set_task("在网络上搜索scut的信息，整理给我，写入到一个文件里给我")
agent.run()