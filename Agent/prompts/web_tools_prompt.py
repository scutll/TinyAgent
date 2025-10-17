web_tools_prompt = str("""
---

fetch_webpage


{
  "name": "fetch_webpage",
  "description": "抓取网页内容并提取主要文本。此工具使用HTTP请求获取网页HTML，然后解析并清理文本内容，去除脚本、样式等无关元素，返回纯净的文本内容。适用于获取网页文章、新闻、文档等文本信息。",
  "parameters": {
    "properties": {
      "url": {
        "description": "要抓取的网页URL。必须是有效的HTTP或HTTPS网址。",
        "type": "string"
      }
    },
    "required": ["url"],
    "type": "object"
  },
  "returns": "成功时返回网页的清理后文本内容；失败时返回以 \"error in fetching webpage {url}: \" 开头的错误描述字符串（如网络连接失败、URL无效、超时等）。",
  "safety_warnings": [
    "此工具会发起外部网络请求，可能涉及隐私和安全风险",
    "仅用于抓取公开可访问的网页，避免访问敏感或受限内容",
    "网络请求可能失败或超时，应在 `think` 中准备备用方案",
    "对于重要数据，建议在 `think` 中验证URL的正确性和安全性"
  ],
  "usage_tips": [
    "Baidu搜索可能有爬虫验证，优先可以使用Wiki百科进行搜索",
    "适用于获取新闻文章、博客内容、文档页面等文本信息",
    "对于需要特定部分内容的网页，可使用 `fetch_webpage_with_selector` 工具",
    "网络连接可能不稳定，建议在 `think` 中考虑重试机制",
    "返回的文本已去除HTML标签和无关元素，适合直接分析",
    "对于大型网页，输出可能较长，应在 `think` 中评估是否需要分块处理"
  ]
}


---

fetch_webpage_with_selector


{
  "name": "fetch_webpage_with_selector",
  "description": "使用CSS选择器抓取网页特定部分的内容。此工具获取网页HTML后，使用指定的CSS选择器定位目标元素，只返回匹配元素的文本内容。适用于精确提取网页特定区域的内容，如文章正文、标题、列表等。",
  "parameters": {
    "properties": {
      "url": {
        "description": "要抓取的网页URL。必须是有效的HTTP或HTTPS网址。",
        "type": "string"
      },
      "selector": {
        "description": "CSS选择器，用于定位网页中的特定元素。例如：\"article\" 选择文章区域，\".content\" 选择class为content的元素，\"#main\" 选择id为main的元素。默认值为 \"body\"。",
        "type": "string"
      }
    },
    "required": ["url"],
    "type": "object"
  },
  "returns": "成功时返回匹配选择器的元素文本内容；如果未找到匹配元素，返回 \"No elements found with selector: {selector}\"；失败时返回以 \"error in fetching webpage {url}: \" 开头的错误描述字符串。",
  "safety_warnings": [
    "此工具会发起外部网络请求，可能涉及隐私和安全风险",
    "仅用于抓取公开可访问的网页，避免访问敏感或受限内容",
    "选择器可能无法匹配到内容，应在 `think` 中准备备用选择器或方案",
    "网络请求可能失败或超时，应在 `think` 中考虑重试机制"
  ],
  "usage_tips": [
    "适用于精确提取网页特定部分的内容，如文章正文、评论区、导航菜单等",
    "常见CSS选择器示例：\"article\"（文章）、\".content\"（内容区域）、\"#main\"（主区域）、\"p\"（段落）、\"h1\"（标题）",
    "如果不确定选择器，可先用 `fetch_webpage` 获取完整内容分析结构",
    "对于动态加载的内容，此工具可能无法获取，需要其他技术手段",
    "建议在 `think` 中说明选择器的选择理由和预期目标"
  ]
}
""")