# TinyAgent : a small agent to help you do something

(使用本地模型时)Api 启动方式:

- 部署模型和api:

```bash
python -m uvicorn llmApi.API.api_genResponse:app --host 0.0.0.0 --port 5200
```

- 因为autodl禁止了外部设备访问容器ip，因此要使用cloudflared来转发到其他地址:
  - 重新开一个终端：

```bash
cloudflared tunnel --url http://localhost:5200
```

- 可以找到一个地址: 

```bash
2025-10-14T06:56:47Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2025-10-14T06:56:47Z INF |  https://few-nikon-minister-prospects.trycloudflare.com 
```

然后在apifox上将这个作为根地址就行了(注意：需要用raw data的json格式发送请求)

(当前为了方便和调试prompt还有本地小模型思考能力太弱等原因)暂时使用的是Deepseek的LLM api, 使用之前要先在agent_core那里贴上API_Key
当前阶段已经能查看项目并生成代码，但还是有一些很致命的问题：
- Agent有时候会因为JSON无法解析而崩溃,猜测应该是应为prompt描述不够充分原因，ai没有严格按照应有的格式进行输出，导致parse_response函数崩溃(这个函数设计的不够完善也是一方面-_-)
- 然后是模型的思考路径很短，不知道会不会对实际的代码生成有什么影响-_-, 感觉是prompt给的例子里面本身就很少，感觉如果项目代码比较复杂的话LLM的思考方式可能会出现理解不到位 ~__~

## Setup and start
先在项目根目录创建config.json, 填上一下信息：
```JSON
{
    "api_key": ,
    "base_url": 
}
```
填上对应的URL和API_key

然后就可以直接配置Agent并开始任务: 
```Python
from Agent.agent_core import AgentCore
agent = AgentCore()
agent.set_task("帮我分析这一个项目文件夹，写一个prompts管理的模块，最好将你的代码放到一个文件夹里面")
agent.run()
```