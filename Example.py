from Agent.agent_core import AgentCore
agent = AgentCore()
agent.set_task("帮我分析这一个项目文件夹，写一个prompts管理的模块, prompt的组成可用参考agent_core.py中的使用方式，另外关于工具的prompt我希望可以是动态的，也就是进行工具载入再将对于tool的prompt添加进去，而不是硬编码地固定tool的prompt。注意不要修改我的源代码, 最好将你的代码放到一个文件夹里面")
agent.run()