word_tools_prompt = str("""
---

read_word_document
{
  "name": "read_word_document",
  "description": "读取包含图片的Word文档,返回文本和图片的Base64编码内容,按顺序排列。此工具解析Word文档(.docx格式),提取其中的文本段落和嵌入图片,将图片转换为Base64编码,按照在文档中出现的顺序返回。适用于需要同时处理文档文本和图片内容的场景。",
  "parameters": {
    "properties": {
      "path": {
        "description": "Word文档的文件路径。支持相对路径(相对于当前工作目录)和绝对路径。必须是.docx格式的Word文档。",
        "type": "string"
      }
    },
    "required": ["path"],
    "type": "object"
  },
  "returns": "成功时返回列表,包含文档内容的有序组合。每个元素是字典:文本内容为 {\"type\": \"text\", \"text\": \"内容\"},图片为 {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/格式;base64,编码数据\"}}。失败时返回以 \"error in reading {path}: \" 开头的错误描述字符串(如文件不存在、格式错误、权限不足等)。",
  "safety_warnings": [
    "仅支持.docx格式的Word文档,不支持旧版.doc格式",
    "大型文档或包含大量高分辨率图片的文档可能导致返回数据量很大",
    "图片以Base64编码返回,会占用较多内存和token",
    "应在 `think` 中评估文档大小和复杂度,避免处理超大文件"
  ],
  "usage_tips": [
    "适用于需要提取Word文档中文本和图片的场景,如文档分析、内容提取、格式转换等",
    "返回的内容按文档中出现顺序排列,保持原始结构",
    "图片已转换为Base64编码,可直接用于显示或进一步处理",
    "读取前可先用 `list_file` 确认文件存在且为.docx格式",
    "对于只需要文本内容的场景,建议使用其他更轻量的文本提取工具",
    "建议在 `think` 中说明需要从文档中提取哪些信息"
  ]
}

""")