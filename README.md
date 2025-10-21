# TinyAgent : a small agent to help you do something

## 现支持功能: 
- 读取**Word文档(docx文件，多模态使用Doubao，可支持表格信息粗略读取)**、各种文本文件、搜索网页信息
- 简单的**根据任务生成代码**

## 模型使用:
- Doubao-thinking: 代码生成能力更强，但更慢(可以用作Planner)
- Deepseek-chat: 速度更快但能力较弱，适合于简单的任务执行(Plan中的Executor)

## 当前问题或期望的改进
### 问题

- 对Word文档文件的读取能力鲁棒性不足，遇到格式复杂的word文档很难进行读取
- 小模型对prompt的理解能力不够，Deepseek-chat偶尔会输出错误格式, Doubao-1.6-lite经常错且会直接死循环
- prompt过长(system 5k + tool 15k+)
- 触发一些Exception时候模型的自主解决能力不足，无法继续进行任务
- 有时候模型会出现 **"自己已经创建了代码文件"但实际上并没有任何创造文件工具被调用** 的幻觉，怎么解决
- 面对当前的**高重复性任务**，目前只能
  - 【1】一直将对下个操作无参考下的对话塞进记忆里面，造成token数爆炸性增长
  - 【2】自行使用循环，每次重新设置任务并重新调用Agent(不雅观而且麻烦)

### 期望改进
- [x] 添加一个tool来询问用户意见，当对用户意图不清楚的时候调用
- [ ] 可以使用到**Plan-and-Execute**的思考框架，可以参考由豆包等较大的模型来进行思考规划，然后具体任务交给下游Agent(以Deepseek等为LLM)进行执行
- 对于prompt过长的问题:
- [ ] 设置**Memory压缩功能**，在不影响模型当前任务的情况下，**对除了system prompt的对话历史进行概要压缩**来减少总token数
- [ ] 设置工具动态载入规则，使用**类RAG规则查询工具**来载入对应工具，后续也可以删除太久不使用的工具prompt
- [ ] **面对一些重复性较高的任务时以往的token完全不具备参考性**，希望能**设计出模型自主选择是否丢弃当前部分聊天记录来减少无用token的堆积**，既可以缓解token爆炸增长，也可以使模型不会因对话太长忘记prompt的


## Setup and start
先在项目根目录创建config.json, 填上一下信息：(默认使用豆包)
```JSON
{
    "doubao_api_key": ,
    "doubao_base_url": 
}
```
如果使用deepseek-api:
```JSON
{
    "ds_api_key": ,
    "ds_base_url": 
}
```
创建Agent时:
```python
agent = AgentCore(UseModel="Deepseek")
```


填上对应的URL和API_key

然后就可以直接配置Agent并开始任务: 
```Python
from Agent.agent_core import AgentCore
agent = AgentCore()
agent.set_task("帮我分析这一个项目文件夹，写一个prompts管理的模块，最好将你的代码放到一个文件夹里面")
agent.run()
```

---

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

