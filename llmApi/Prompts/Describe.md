# Agent 项目设计prompt
    这是一些为agent运作设计的prompts，按照React或者plan and act的运行逻辑
- prompt_react: 最基础的Reason-Action运行链，LLM直接进行任务运行然后观测，思考，再运行，同时向用户展示Response, 但不向用户询问是否运行。这里的一个特殊点是**每轮只可以且必须调用一个工具**，但我想如果有一些ai不理解用户行为的情况需要问清楚，**是否需要不调用工具而只是先在response中返回对用户的询问，然后用户进行解释以后再继续执行**
- Plan-act: 先列一个todo-list来说明操作步骤，然后每操作一步观察后修改todo-list再运行下一步**具体流程其实还不是很清楚(待深入学习研究)**