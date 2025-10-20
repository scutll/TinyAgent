inquery_user_prompt = str("""
{
  "name": "inquery_user",
  "description": "在需要用户确认或补充关键信息时向用户发起交互式询问。适用于：高风险操作确认（如删除/覆盖）、不明确的用户意图澄清时的询问。",
  "parameters": {
    "properties": {
    },
    "required": [],
    "type": "object"
  },
  "returns": "成功时返回用户的输入字符串；若读取输入失败，返回以 \"Error reading user input:\" 开头的错误描述字符串。",
  "safety_warnings": [
    "当LLM希望提问时，应该简单说明LLM想要获取的信息或许可，提示用户需要他输入信息"
    "在执行高危操作前应文本确认（非仅 y/n 的模糊确认，若风险极高建议再次确认）"
  ],
  "usage_tips": [
    "在进行不可逆操作（如 delete_file/delete_dir/search_replace 覆盖）,或执行一些可能引发危险的CMD命令的时候调用以获取用户明确许可",
    "在用户意图(是否要修改某文件/是否要创建文件/目的)不够明确时调用,向用户询问必要的信息, 以避免工具误用或幻觉",
    "当LLM希望提问时，应该简单说明LLM想要获取的信息或许可，提示用户需要他输入信息"
  ]
}
""")
