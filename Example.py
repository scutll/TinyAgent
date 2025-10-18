from Agent.agent_core import AgentCore
agent = AgentCore(UseModel="Doubao")
agent.set_task("""
读取docs/中的test.docx文档，帮我总结内容
               """)
agent.run()