tools_prompt = str("""
下面列出所有可用工具的详细说明。每个工具都以完整的 JSON Schema 格式定义，包含名称、描述、参数定义、输出说明和使用建议。调用工具时必须严格遵循参数要求。

list_file
```json
{
  "name": "list_file",
  "description": "列出当前工作目录下的文件与目录。支持简易的 `-l` 模式显示详细信息（类似 `ls -l` 命令）。此工具用于快速浏览目录内容，帮助确认文件是否存在、了解目录结构。",
  "parameters": {
    "properties": {
      "params": {
        "description": "可选参数。当值为 \"-l\" 时，返回详细列表（包括文件类型、大小、最后修改时间）；为空字符串或不提供时，仅返回文件/目录名列表，每项一行。",
        "type": "string"
      }
    },
    "required": [],
    "type": "object"
  },
  "returns": "返回字符串，包含文件列表或详细信息。普通模式下每行一个文件/目录名；`-l` 模式下每行格式为 `类型\\t大小\\t修改时间\\t名称`。遇到异常时返回错误描述字符串。",
  "usage_tips": [
    "在执行文件操作前用此工具确认目标文件或目录是否存在",
    "使用 `-l` 参数可获取文件大小和修改时间等元信息",
    "仅列出当前工作目录的直接子项，不递归子目录（递归查看请使用 `tree_file`）"
  ]
}
```

---

tree_file

```json
{
  "name": "tree_file",
  "description": "以树形结构递归显示目录及其所有子目录和文件（类似 `tree` 命令）。此工具适用于全面了解项目结构、查找深层文件位置。",
  "parameters": {
    "properties": {
      "path": {
        "description": "要展示的目录路径。可以是相对路径或绝对路径。默认值为 \".\"（当前工作目录）。",
        "type": "string"
      },
      "prefix": {
        "description": "内部递归使用的缩进前缀。调用者通常不需要设置此参数，保持默认空字符串即可。",
        "type": "string"
      }
    },
    "required": [],
    "type": "object"
  },
  "returns": "返回字符串，使用 `├──` 和 `└──` 等符号表示树形结构，递归展示目录下所有文件和子目录。异常情况会返回错误信息字符串。",
  "usage_tips": [
    "适用于需要了解完整目录结构的场景",
    "对于大型项目，输出可能较长，应在 `think` 中评估是否需要使用此工具",
    "可以指定 `path` 参数查看特定子目录的结构"
  ]
}
```

---

delete_file

```json
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
    "建议先使用 `list_file` 或 `read_file` 确认目标文件",
    "对于重要文件，应在 `think` 中明确说明删除原因",
    "不能用于删除目录（删除目录请使用 `delete_dir`）"
  ]
}
```

---

delete_dir

```json
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
```

---

get_absolute_cur_path

```json
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
```

---

change_dir

```json
{
  "name": "change_dir",
  "description": "切换当前工作目录到指定路径。改变后续所有相对路径操作的基准目录。",
  "parameters": {
    "properties": {
      "path": {
        "description": "目标目录的路径。支持相对路径（相对于当前工作目录）和绝对路径。",
        "type": "string"
      }
    },
    "required": ["path"],
    "type": "object"
  },
  "returns": "成功时返回 \"Changed directory to: <absolute_path>\"，显示切换后的绝对路径；失败时返回 \"Error changing directory: <error_message>\"（如目录不存在、权限不足等）。",
  "usage_tips": [
    "在需要操作特定目录下多个文件时，可先切换到该目录",
    "切换后可使用 `get_absolute_cur_path` 验证是否切换成功",
    "注意切换目录会影响后续所有相对路径操作"
  ]
}
```

---

read_file

```json
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
    "读取前可先用 `list_file` 确认文件存在",
    "不适用于二进制文件（如图片、视频、可执行文件等）",
    "确保获取完整上下文，避免遗漏关键信息"
  ]
}
```

---

search_replace

```json
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
    "适用于代码修改、配置更新、文本替换等场景"
  ]
}
```

---

create_file

```json
{
  "name": "create_file",
  "description": "在指定目录中创建新文件并写入初始内容。如果目标目录不存在，会自动递归创建所需的目录结构。此工具不会覆盖已存在的文件。",
  "parameters": {
    "properties": {
      "path": {
        "description": "要创建文件的目录路径。支持相对路径和绝对路径。若目录不存在，将自动递归创建。",
        "type": "string"
      },
      "file_name": {
        "description": "要创建的文件名，必须包含扩展名（如 .py、.txt、.json 等）。文件名不应包含路径分隔符。",
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
  ],
  "usage_tips": [
    "创建前可先用 `list_file` 或 `tree_file` 确认文件不存在，避免调用失败",
    "适用于创建配置文件、源代码文件、文档、测试数据等",
    "文件默认使用 UTF-8 编码，适合大多数文本文件",
    "创建后建议用 `read_file` 验证文件内容是否正确写入",
    "如需创建多个文件，应分别调用此工具"
  ]
}
```

---

3.10 Finish

```json
{
  "name": "Finish",
  "description": "标记任务完成或无法完成。使用此工具表示你已完成用户的请求，或经过充分尝试后确认任务无法完成。最终的总结和回复应写在 `action_input` 字段中。",
  "parameters": {
    "properties": {},
    "required": [],
    "type": "object"
  },
  "returns": "此工具不返回内容。调用后任务流程结束，`action_input` 中的内容作为最终答案展示给用户。",
  "usage_when": [
    "已经完成用户请求的所有步骤",
    "已收集到足够信息可以给出完整答案",
    "经过充分尝试后确认任务无法完成（需说明原因）",
    "发现任务超出权限或存在安全风险（需说明拒绝原因）"
  ],
  "usage_tips": [
    "`action_input` 应包含对任务完成情况的清晰总结",
    "如果任务成功完成，应说明完成了什么、结果在哪里",
    "如果任务失败，应说明尝试了什么、为何失败、可能的解决方案",
    "最终答案应对用户友好、易于理解"
  ]
}
```

---
""")