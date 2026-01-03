# TinyAgent : a small agent to help you do something

Version 0.1.0
可以直接安装在设备中，用命令行进行操作，但是config.json需要在文件里面设置，也暂不支持对话保存
Version 0.1.1
支持CLI配置api_key/base_url, 并解决了创建新对话时的问题，以及解决了llm不正常使用用户同语言问题

Version 0.1.2 计划
config.json支持更多配置


Version 0.1.5
完善了模型配置互动模块，现在可以选择不同模型进行互动
为agent开放了更大的命令行运行权限，可以运行更多命令行。用户也可以选择将命令行添加到白名单跳过验证
提高了agent创建代码和运行命令行验证的积极性

Version 1.0.0 
1. 全新支持切换对话(暂时不能直接查看对话记录内容)
2. 支持文件上传功能，tmp/内的文件直接作为信息文件上传给llm, 支持Word、pdf、图片、文本文件

Version 1.0.1
1. 解决了tmp/目录在用户工作目录时候读取失败的问题
2. 完善文件选择逻辑，可以在命令行选择单个文件或一整个目录

Version 1.0.2
1. 增加了PPT文字识别功能，提取PPT内的图文
2. 提升了对文本文件的读取范围(后缀不限的文本文件都可以进行读取)
3. 强化了命令行工具，现在可以由Agent进行命令行交互程序



Version 1.1.0 计划
1. 推出word文档编辑功能，可以支持编辑增删文字。现在的问题是很难找到合适的word读取与提交给llm的格式，所以很难推进文档编辑工具的编写

后续Version计划
1. 使用全新的llm输出形式，可以支持工具调用解析的同时支持流式返回向用户展示的response，这个很麻烦
2. 建立知识库功能，建设长记忆搜索功能
3. 建立统一的MCP接口, 也就是llm通过跟MCP一样的接口来对接工具(设置包装类来调用本地工具), 还可同时调用网络MCP工具
4. 完善对话管理功能，设置自动提取信息并命名对话记录的功能，现在的想法是第一轮人机对话后进行总结并重命名
5. 深入学习Python的一些编程规范和未了解过的编程规则，把现在写的史山重构下
6. 修改一些文件上传的逻辑，现在只能显示本次文件提交过程中已经提交的文件，并且一键提交以后不会显示上传失败的文件，而且提交完成以后再打开文件上传功能也没法查看已经提交的文件(这些都要从Agent层面看有哪些文件是实际上传成功的，删除逻辑也是在这个层面才能操作)


## 现支持功能: 
- 读取**Word文档(docx文件，多模态使用Doubao，可支持表格信息粗略读取)**、各种文本文件、搜索网页信息
- 简单的**根据任务生成代码**

## 模型使用:
- GPT-4.1: 综合能力更强，生成格式最准确
- Doubao-thinking: 代码生成能力更强，但更慢(可以用作Planner)
- Deepseek-chat: 速度更快但能力较弱，适合于简单的任务执行(Plan中的Executor)

## 当前问题或期望的改进
### 问题

- 对Word文档文件的读取能力鲁棒性不足，遇到格式复杂的word文档很难进行读取
- 小模型对prompt的理解能力不够，Deepseek-chat偶尔会输出错误格式, Doubao-1.6-lite经常错且会直接死循环
- prompt过长(system 5k + tool 15k+)
- 触发一些Exception时候模型的自主解决能力不足，无法继续进行任务
- **IMPORTANT**有时候模型会出现 **"自己已经创建了代码文件"但实际上并没有任何创造文件工具被调用** 的幻觉，怎么解决
- 面对当前的**高重复性任务**，目前只能
  - 【1】一直将对下个操作无参考下的对话塞进记忆里面，造成token数爆炸性增长
  - 【2】自行使用循环，每次重新设置任务并重新调用Agent(不雅观而且麻烦)

### 期望改进
- [ ] Human-in-the-loop这个工具在接受用户输入的时候如果有Ctrl+C会直接退出的bug应该进行改进，而且现在的确也没有在运行此工具时退出的功能
- [x] 使用Openai的结构化输出接口来使得LLM输出调用工具更为稳定
  - 在
- [x] 添加一个tool来询问用户意见，当对用户意图不清楚的时候调用
- [ ] 可以使用到**Plan-and-Execute**的思考框架，可以参考由豆包等较大的模型来进行思考规划，然后具体任务交给下游Agent(以Deepseek等为LLM)进行执行
- 对于context过长的问题:
- [x] 设置**Memory压缩功能**，在不影响模型当前任务的情况下，**对除了system prompt的对话历史进行概要压缩**来减少总token数
- [ ] 设置工具动态载入规则，使用**类RAG规则查询工具**来载入对应工具，后续也可以删除太久不使用的工具prompt
      - 这个比较难，经常出现工具完全不匹配的问题
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

