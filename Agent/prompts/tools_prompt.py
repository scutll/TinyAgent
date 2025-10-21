
tree_file_prompt = """
tree_file
json
{
  "name": "tree_file",
  "description": "以树形结构递归显示目录及其所有子目录和文件（类似 `tree` 命令）。此工具适用于全面了解项目结构、查找深层文件位置。",
  "parameters": {
    "properties": {
    },
    "required": [],
    "type": "object"
  },
  "returns": "返回字符串，使用 `├──` 和 `└──` 等符号表示树形结构，递归展示目录下所有文件和子目录。异常情况会返回错误信息字符串。",
  "usage_tips": [
    "适用于需要了解完整目录结构的场景",
    "对于大型项目，输出可能较长，应在 `think` 中评估是否需要使用此工具",
  ]
}
---
"""

delete_file_prompt = """
delete_file

{
  "name": "delete_file",
  "description": "删除指定的单个文件。此操作不可逆，应谨慎使用。",
  "parameters": {
    "properties": {
      "filename": {
        "description": "要删除的文件名或路径。支持相对路径和绝对路径。必须是文件，不能是目录。",
        "type": "string"
      }
    },
    "required": ["filename"],
    "type": "object"
  },
  "returns": "成功时返回 \"{filename} deleted!\"；失败时返回 \"Error deleting {filename}: <error_message>\"。",
  "safety_warnings": [
    "删除操作不可逆，调用前必须在 `think` 中确认文件路径正确",
    "建议先使用 `tree_file` 或 `read_file` 确认目标文件",
    "对于重要文件，应在 `think` 中明确说明删除原因",
    "不能用于删除目录（删除目录请使用 `delete_dir`）"
  ]
}
---

"""
delete_dir_prompt = """
delete_dir

{
  "name": "delete_dir",
  "description": "递归删除整个目录及其所有内容（包括所有子目录和文件）。这是一个高风险操作，不可逆，使用时必须极其谨慎。",
  "parameters": {
    "properties": {
      "directory": {
        "description": "要删除的目录路径。支持相对路径和绝对路径。必须是目录，不能是文件。",
        "type": "string"
      }
    },
    "required": ["directory"],
    "type": "object"
  },
  "returns": "成功时返回 \"{directory} and its contents deleted!\"；失败时返回错误描述（如目录不存在、不是目录、权限不足等）。",
  "safety_warnings": [
    "这是最危险的操作之一，删除不可恢复",
    "调用前必须在 `think` 中进行严格验证",
    "建议先使用 `tree_file` 查看目录内容，确认删除范围",
    "对于根目录、上级目录、系统目录等敏感路径，必须拒绝操作",
    "必要时应在 `response` 中要求用户明确确认"
  ]
}

---
"""

get_absolute_cur_path_prompt = """

get_absolute_cur_path

{
  "name": "get_absolute_cur_path",
  "description": "获取当前工作目录的绝对路径。用于确认当前位置、构建绝对路径、调试路径问题。",
  "parameters": {
    "properties": {},
    "required": [],
    "type": "object"
  },
  "returns": "返回字符串，表示当前工作目录的绝对路径。",
  "usage_tips": [
    "在不确定当前位置时使用此工具",
    "在执行相对路径操作前可先确认当前目录",
    "有助于构建和验证文件的完整路径"
  ]
}

---

"""

read_file_prompt = """

read_file

{
  "name": "read_file",
  "description": "读取指定文本文件的完整内容。此工具将文件内容作为字符串返回，适用于分析、修改或展示文件内容。调用此工具时，你有责任确保获取了完整的上下文。每次调用时应该：1) 评估查看的内容是否足以完成任务；2) 注意哪些部分未显示；3) 如果内容不足且可能在未显示部分，主动再次调用工具查看；4) 有疑问时，再次调用工具获取更多信息。",
  "parameters": {
    "properties": {
      "path": {
        "description": "要读取的文件路径。支持相对路径（相对于当前工作目录）和绝对路径。必须是文本文件。",
        "type": "string"
      }
    },
    "required": ["path"],
    "type": "object"
  },
  "returns": "成功时返回文件的完整文本内容（使用 UTF-8 编码读取）；失败时返回以 \"error in reading {path}: \" 开头的错误描述字符串（如文件不存在、权限不足、编码错误等）。",
  "usage_tips": [
    "适用于读取配置文件、源代码、日志、文档等文本格式文件",
    "对于大文件应在 `think` 中评估是否需要分块处理或使用其他策略",
    "读取前可先用 `tree_file` 确认文件存在",
    "不适用于二进制文件（如图片、视频、可执行文件等）",
    "确保获取完整上下文，避免遗漏关键信息"
  ]
}

---
"""
search_replace_prompt = """

search_replace

{
  "name": "search_replace",
  "description": "在文本文件中搜索并替换指定内容。支持全局替换（替换所有匹配项）或整体覆盖（当 `match` 为 null 时）。修改会立即写入文件，不可撤销。",
  "parameters": {
    "properties": {
      "path": {
        "description": "要修改的文件路径。支持相对路径和绝对路径。文件必须存在且为文本文件。",
        "type": "string"
      },
      "match": {
        "description": "要搜索的字符串。所有匹配此字符串的地方都会被替换。如果值为 null，则用 replace 内容覆盖整个文件（谨慎使用）。",
        "type": ["string", "null"]
      },
      "replace": {
        "description": "替换后的新字符串。当 match 不为 null 时，所有匹配 match 的地方都会被替换为此字符串；当 match 为 null 时，此字符串将成为文件的全部内容。",
        "type": "string"
      }
    },
    "required": ["path", "match", "replace"],
    "type": "object"
  },
  "returns": "成功时返回修改后的文件完整内容（便于验证修改结果）；失败时返回以 \"error in search_replace {path}: \" 开头的错误描述字符串。",
  "safety_warnings": [
    "修改会直接写入文件，操作不可逆，调用前必须在 `think` 中确认修改的准确性",
    "强烈建议先用 `read_file` 读取文件，确认 `match` 字符串存在且准确，避免误替换",
    "对于复杂修改，应在 `think` 中说明修改策略并评估影响范围",
    "`match` 为 null 时会覆盖整个文件，风险极高，需在 `think` 中明确记录",
    "建议在 `search_replace` 调用后再次使用 `read_file` 确认修改结果"
  ],
  "usage_tips": [
    "替换操作是全局的（所有匹配项都会被替换，而非仅第一个）",
    "对于需要部分替换的场景，应确保 `match` 字符串足够具体且唯一",
    "可以通过返回的新内容立即验证修改是否符合预期",
    "适用于代码修改、配置更新、文本替换等场景",
    "建议在 `search_replace` 调用后再次使用 `read_file` 确认修改结果"
  ]
}

---

"""


create_file_prompt = """
create_file
{
  "name": "create_file",
  "description": "在指定目录中创建新文件并写入初始内容。如果目标目录不存在，会自动递归创建所需的目录结构。此工具不会覆盖已存在的文件。",
  "parameters": {
    "properties": {
      "path": {
        "description": "要创建文件的目录路径。支持相对路径和绝对路径。若目录不存在，将自动递归创建。Example: ./Test",
        "type": "string"
      },
      "file_name": {
        "description": "要创建的文件名，必须包含扩展名（如 .py、.txt、.json 等）。文件名不应包含路径分隔符, 也不应该有目录前缀，而应该是单纯的文件名。Example: test.txt",
        "type": "string"
      },
      "content": {
        "description": "文件的初始内容。可以是空字符串（创建空文件）或包含任意文本内容。使用 UTF-8 编码写入。",
        "type": "string"
      }
    },
    "required": ["path", "file_name", "content"],
    "type": "object"
  },
  "returns": "成功时返回 \"File created successfully: {full_path}\"，显示创建文件的完整路径；失败时返回以 \"error in creating file\" 开头的错误描述字符串（如文件已存在、权限不足等）。",
  "safety_warnings": [
    "若目标文件已存在，工具会返回错误以防止意外覆盖现有文件",
    "如需修改已存在的文件，应使用 `search_replace` 工具",
    "目录路径会自动创建，调用前应在 `think` 中确认路径正确性，避免创建错误的目录结构",
    "对于敏感目录（如系统目录、重要项目目录），应在 `think` 中进行额外验证"
    "建议在 `create_file` 调用后再次使用 `read_file` 确认修改结果"
  ],
  "usage_tips": [
    "创建前可先用 `list_file` 或 `tree_file` 确认文件不存在，避免调用失败",
    "适用于创建配置文件、源代码文件、文档、测试数据等",
    "文件默认使用 UTF-8 编码，适合大多数文本文件",
    "建议在 `create_file` 调用后再次使用 `read_file` 确认修改结果",
    "如需创建多个文件，应分别调用此工具"
  ]
}
---
"""

Finish_prompt = """
Finish
{
  "name": "Finish",
  "description": "标记任务完成或无法完成。使用此工具表示你已完成用户的请求，或经过充分尝试后确认任务无法完成。最终的总结和回复应该体现在 `response` 字段中。",
  "parameters": {
    "properties": {},
    "required": [],
    "type": "object"
  },
  "returns": "此工具不返回内容。调用后任务流程结束，`response` 中的内容作为最终答案展示给用户。",
  "usage_when": [
    "已经完成用户请求的所有步骤",
    "已收集到足够信息可以给出完整答案",
    "经过充分尝试后确认任务无法完成（需说明原因）",
    "发现任务超出权限或存在安全风险（需说明拒绝原因）"
  ],
  "usage_tips": [
    "`response` 应包含对任务完成情况的清晰总结",
    "如果任务成功完成，应说明完成了什么、结果在哪里",
    "如果任务失败，应说明尝试了什么、为何失败、可能的解决方案",
    "最终答案应对用户友好、易于理解"
  ]
}

---
"""

inquery_user_prompt = """
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
"""

fetch_webpage_prompt = """
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

"""


fetch_webpage_with_selector_prompt = """
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
"""

read_word_document_prompt = """
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
    "读取前可先用 `tree_file` 确认文件存在且为.docx格式",
    "对于只需要文本内容的场景,建议使用其他更轻量的文本提取工具",
    "建议在 `think` 中说明需要从文档中提取哪些信息"
    "如果读取文件信息比较少，可能是因为文档是表格形式的，可以使用extract_info_from_docx_table来重新读取"
  ]
}
---
"""
extract_info_from_docx_table_prompt = """
extract_info_from_docx_table
{
  "name": "extract_info_from_docx_table",
  "description": "提取Word文档(.docx格式)中所有表格的单元格内容,返回纯文本字符串。此工具专门用于解析包含表格的Word文档,自动遍历所有表格并提取每个单元格的文本内容,去除空白字符后按顺序拼接成字符串,每个单元格内容占一行。适用于表单、申请表、数据表等结构化文档的信息提取场景。",
  "parameters": {
    "properties": {
      "file_path": {
        "description": "Word文档的文件路径。支持相对路径(相对于当前工作目录)和绝对路径。必须是.docx格式的Word文档,且文档中包含表格内容。",
        "type": "string"
      }
    },
    "required": ["file_path"],
    "type": "object"
  },
  "returns": "成功时返回字符串,包含文档中所有表格的单元格内容,每个非空单元格内容占一行,按表格顺序和单元格位置(从左到右、从上到下)依次排列。失败时抛出FileNotFoundError异常并返回错误描述字符串(如\"文件不存在: {file_path}\"),或因文件格式错误、权限不足等原因导致的其他异常。",
  "safety_warnings": [
    "仅支持.docx格式的Word文档,不支持旧版.doc格式",
    "只提取表格内容,不包含文档中的普通段落文本",
    "会自动过滤空单元格,只返回有内容的单元格",
    "对于包含大量表格或复杂表格结构的文档,返回的字符串可能很长",
    "不保留表格的格式信息(如合并单元格、边框、颜色等),只提取纯文本内容"
  ],
  "usage_tips": [
    "适用于提取入会申请表、信息登记表、数据统计表等包含表格的Word文档",
    "返回的是简洁的纯文本格式,每行一个单元格内容,便于后续解析和处理",
    "对于需要保留表格结构信息的场景,建议使用其他更完整的表格解析工具",
    "提取后的内容可以直接用于文本分析、信息提取、数据录入等场景",
    "建议在 `think` 中说明需要从表格中提取哪些字段或信息",
    "如果文档包含多个表格,所有表格内容会按顺序合并返回",
    "单元格内的换行符会被保留,可能导致某些内容跨多行显示"
  ]
}

"""

execute_command_prompt = """
execute_command
{
  "name": "execute_command",
  "description": "执行安全的命令行命令，仅限于项目环境配置、包管理、环境查询和项目启动等操作。",
  "parameters": {
    "properties": {
      "command": {
        "description": "要执行的命令字符串。切勿包含任何危险操作。示例:  'npm install express', 'pip install openai', 'python example.py'",
        "type": "string"
      }
    },
    "required": ["command"],
    "type": "object"
  },
  
  
  "returns": "命令行的运行结果以及输出",
  
  "allowed_commands": {
    "package_management": [
      "pip install/list/show/freeze/check - Python包管理(仅限安装、查看、检查)",
      "poetry install/update/show/env/run - Poetry包管理",
      "conda install/list/env list/activate/info - Conda环境管理",
      "npm install/ci/list/outdated/audit/start/run - Node.js包管理",
      "yarn install/list/outdated/start/run - Yarn包管理",
      "pnpm install/list/outdated/start/run - PNPM包管理"
    ],
    "project_startup": [
      "python -m <module> - 运行Python模块",,
      "python <script.py> - 运行Python脚本",
      "node <script.js> - 运行Node.js脚本",
      "npm run serve - 运行npm脚本",
      "yarn start/run - 启动yarn项目"
    ],
    "environment_query": [
      "python --version - 查看Python版本",
      "node --version / npm --version - 查看Node版本",
      "pip --version - 查看pip版本",
      "which <command> / where <command> - 查找命令位置(Unix/Windows)",
      "echo <text> - 输出文本",
      "hostname - 查看主机名",
      "whoami - 查看当前用户",
      "systeminfo - 查看系统信息(Windows)"
    ],
    "git_readonly": [
      "git status - 查看Git状态",
      "git log - 查看提交历史",
      "git diff - 查看差异",
      "git branch - 查看分支",
      "git remote -v - 查看远程仓库",
      "git config --list - 查看配置"
    ],
    "process_management": [
      "ps aux / ps -ef - 查看进程列表(Unix)",
      "tasklist - 查看进程列表(Windows)",
      "netstat -ano - 查看网络连接和端口占用"
    ]
  },
  
  "forbidden_commands": {
    "file_operations": [
      "rm/del - 删除文件",
      "rmdir/rd - 删除目录",
      "mv/move - 移动/重命名文件",
      "rename/ren - 重命名文件",
      "mkdir/md - 创建目录",
      "touch - 创建空文件"
    ],
    "dangerous_operations": [
      "chmod/chown - 修改权限/所有者",
      "sudo/su - 提升权限",
      "shutdown/reboot/init - 关机/重启",
      "systemctl/service - 系统服务管理",
      "format/fdisk/mkfs - 格式化/分区操作"
    ],
    "git_write_operations": [
      "git push - 推送到远程仓库",
      "git commit - 提交更改",
      "git add - 添加文件到暂存区",
      "git rm - 删除文件",
      "git clone - 克隆仓库",
      "git pull/fetch/merge - 拉取/合并代码"
    ],
    "command_chains": [
      "&& - 命令链接(与)",
      "|| - 命令链接(或)",
      "; - 命令分隔符",
      "| - 管道操作"
    ],
    "file_redirection": [
      "> - 文件覆盖重定向(允许 >> 追加重定向)"
    ]
  },
  
  "safety_warnings": [
    "所有命令在执行前都会经过严格的安全检查，不符合规则的命令会被直接拒绝",
    "绝对禁止任何文件系统的增删改移动操作，包括但不限于 rm/del/mv/copy/mkdir 等",
    "绝对禁止任何可能导致系统危险的命令，如 sudo/shutdown/chmod 等",
    "Git只允许只读操作(status/log/diff等)，禁止任何写操作(push/commit/add等)",
    "不允许使用命令链(&& || ; |)，必须逐条执行命令",
    "不允许使用 > 覆盖重定向，防止意外覆盖文件(允许使用 >> 追加)",
    "pip/npm等包管理工具只允许 install/list/show 等安全操作",
    "Python执行只允许运行模块(-m)或明确的.py文件",
    "命令执行有60秒超时限制，超时会自动终止",
    "所有命令都在当前工作目录(cwd)中执行"
  ],
  
  "usage_tips": [
    "在 response 中明确说明为什么需要执行该命令，预期的结果是什么",
    "涉及环境安装等的非纯查询命令应先向用户请示是否执行，切勿擅自修改用户配置环境"
    "对于一些不影响环境的查询命令，可以不通过用户许可自行执行"
    "对于包安装操作，建议先检查包是否已安装(pip list/npm list)",
    "对于项目启动命令，应确保项目配置文件存在且正确",
    "如果命令失败，应仔细分析标准错误输出(stderr)中的错误信息",
    "对于环境查询命令，可以用于确认环境配置是否正确",
    "建议先使用查询命令(如 pip list)确认当前状态，再决定是否需要安装",
    "Git查询命令可用于了解代码仓库状态，但不能修改代码",
    "命令执行可能需要一定时间，应在 think 中评估是否会超时",
    "若命令需要用户交互(如确认输入)，会导致命令挂起，应避免此类命令"
  ],
  
  "examples": [
    {
      "command": "pip list",
      "description": "列出已安装的Python包"
    },
    {
      "command": "npm install express",
      "description": "安装Node.js的express包"
    },
    }
  ],
  
  "rejected_examples": [
    {
      "command": "rm -rf docs",
      "reason": "包含禁止的文件删除命令 rm"
    },
    {
      "command": "pip install numpy && rm test.py",
      "reason": "不允许命令链 && 且包含危险命令 rm"
    },
    {
      "command": "echo 'test' > file.txt",
      "reason": "不允许使用 > 覆盖文件"
    },
  ]
}
---
"""