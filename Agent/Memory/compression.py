from Agent.Memory.container import MemoryContainer
from Agent.request.api import get_response_from_Doubao
description = """
请阅读以下用户与 Agent 的对话，并以我（模型）的第一人称视角压缩关键信息。输出需简洁，重点保留：1）用户的核心诉求与限制条件；2）我完成的主要操作及给出的响应；3）最终结论或待办事项。次要细节可概述，不重要的细节可以略过甚至丢弃。
如果对话中包含了你认为是你之前进行压缩过的信息，你需要集合情况执行判断是否完整保留这段压缩后的信息，或者将这段信息融入到你的压缩结果中
总的目的是保留最重要的信息，并使压缩后的信息尽量简短(32k词压缩后尽量在200词以内，10万词的压缩后大小尽量在500词以内)。


示例结果: 我阅读了用户的文档，用户想要我帮他完成他的Java作业，为用户生成了对应的代码并将文件创建在document/文件夹里面
---
\n\n\n
"""

def memory_compress__(Memory: MemoryContainer) -> str:
   context = str(Memory.conversation) 
   print(f"context length before compression: {len(context)}\nstart compressing: ")
   content = description + context
   del context
   tmp_memory = MemoryContainer()
   tmp_memory._add_system_prompt("你是一名对话压缩助手，需按提示提炼重点。")
   compressed_context = get_response_from_Doubao(content, tmp_memory)
   
   print(f"compression ended! context length after compression: {len(compressed_context)}")
   
   return compressed_context


# if __name__ == "__main__":
#     memory = MemoryContainer()
#     log_content = ""
#     with open('logs/agent_run_log.txt', 'r', encoding='utf-8') as f:
#         for idx, line in enumerate(f):
#             if idx > 100:
#                 break
#             log_content += line
            
#     memory._add_assistant_message(log_content)
#     print(memory_compress__(memory))