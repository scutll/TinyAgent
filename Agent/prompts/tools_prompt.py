tree_file_prompt = """
{
  "name": "tree_file",
  "description": "List a directory tree (similar to `tree`) to inspect and analyze project structure.",
  "parameters": {
    "type": "object",
    "properties": {
      "start_path": {
        "type": "string",
        "description": "Path to start scanning from. Use it to focus on a specific subdirectory when deeper inspection is needed."
      },
      "search_depth": {
        "type": "integer",
        "description": "How many directory levels to expand (1–4). Controls recursion depth to avoid excessive output."
      },
      "ignore_list": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Directory names to ignore completely (not displayed and not expanded). Useful for skipping non-code folders such as .vscode, .idea, node_modules, __pycache__, dist, build, etc."
      }
    },
    "required": []
  },
  "returns": "A plain-text tree using characters like `├──` and `└──`. Errors return descriptive strings.",
  "usage_notes": [
    "Use this tool to understand the project's code structure, locate important directories, and prepare for further analysis.",
    "First call: always use `search_depth = 1` to get a top-level overview. Based on the result, set an appropriate `ignore_list` to exclude non-code or irrelevant directories.",
    "After ignore_list is set, increase `search_depth` (2–4) to progressively explore more code files while keeping output manageable.",
    "When you need to inspect the inside of a specific directory beyond the global depth limit, set `start_path` to that directory and repeat the same shallow-→-refine procedure."
  ]
}
"""


delete_file_prompt = """
{
  "name": "delete_file",
  "description": "Delete a single file permanently. This action cannot be undone.",
  "parameters": {
    "type": "object",
    "properties": {
      "filename": {
        "type": "string",
        "description": "Path to the file to delete (relative or absolute). Must point to a file, not a directory."
      }
    },
    "required": ["filename"]
  },
  "returns": "`{filename} deleted!` when successful, or `Error deleting {filename}: ...` on failure.",
  "safety_notes": [
    "Confirm the path with `tree_file` or `read_file` before deleting.",
    "Explain the reason for deletion inside `think`.",
    "Use `delete_dir` for folders instead of this tool."
  ],
  "usage_notes": []
}
"""


delete_dir_prompt = """
{
  "name": "delete_dir",
  "description": "Recursively delete a directory and everything inside. Extremely high-risk and irreversible.",
  "parameters": {
    "type": "object",
    "properties": {
      "directory": {
        "type": "string",
        "description": "Path to the directory to remove (relative or absolute)."
      }
    },
    "required": ["directory"]
  },
  "returns": "`{directory} and its contents deleted!` or a descriptive error string.",
  "safety_notes": [
    "Never run on root/system/parent directories.",
    "Document the justification and expected impact in `think`.",
    "Request explicit user confirmation for risky deletions."
  ],
  "usage_notes": [
    "Inspect the directory with `tree_file` before removal."
  ]
}
"""


get_absolute_cur_path_prompt = """
{
  "name": "get_absolute_cur_path",
  "description": "Return the absolute path of the agent's current working directory.",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  },
  "returns": "Absolute path as a string.",
  "safety_notes": [],
  "usage_notes": [
    "Run before constructing relative paths if you're unsure about the current location.",
    "Use this tool before performing file reads/writes or executing shell commands so you can reason about absolute paths explicitly in your 'think' step."
  ]
}
"""


read_file_prompt = """
{
  "name": "read_file",
  "description": "Read the full contents of a UTF-8 text file. You are responsible for ensuring you collected enough context—call again if you need additional sections.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "list",
        "items": { "type": "string" },
        "description": "Read the full contents of one or more UTF-8 text files. **You are supposed to provide paths as a list** (a single file has to be in list form also) to retrieve files at once, which can help save resources."
      }
    },
    "required": ["path"]
  },
  "returns": "File contents as a string, or `error in reading {path}: ...` on failure.",
  "safety_notes": [
    "Do not use for binary files.",
    "Avoid leaking secrets—summarize sensitive content instead of copying verbatim when responding to users."
  ],
  "usage_notes": [
    "Preview structure with `tree_file` if paths are uncertain.",
    "Provide multiple files in the list to reduce repeated calls.",
  ]
}
"""


search_replace_prompt = """
{
  "name": "search_replace",
  "description": "Search a text file for a string and replace it (all matches). If `match` is null, the entire file will be overwritten by `replace`.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "Path to the file."},
      "match": {"type": ["string", "null"], "description": "String to replace, or null to overwrite the whole file."},
      "replace": {"type": "string", "description": "Replacement text."}
    },
    "required": ["path", "match", "replace"]
  },
  "returns": "Updated file content, or `error in search_replace {path}: ...` on failure.",
  "safety_notes": [
    "Edits are persisted immediately—double-check before calling.",
    "Explain your strategy in `think`, especially when `match` is null."
  ],
  "usage_notes": [
    "Read the file first to ensure the `match` string exists and is unique.",
    "Consider re-reading the file afterward to verify the change."
  ]
}
"""


create_file_prompt = """
{
  "name": "create_file",
  "description": "Create a brand-new file (without overwriting existing files) and write initial content. Parent directories are created automatically if missing.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "Target directory (relative or absolute)."},
      "file_name": {"type": "string", "description": "File name with extension (no path separators)."},
      "content": {"type": "string", "description": "Initial UTF-8 content (can be empty)."}
    },
    "required": ["path", "file_name", "content"]
  },
  "returns": "`File created successfully: {full_path}` or an error string.",
  "safety_notes": [
    "Use `search_replace` for existing files—this tool refuses to overwrite.",
    "Confirm the directory path is correct to avoid polluting the repo."
  ],
  "usage_notes": [
    "List the directory first if you're unsure whether the file already exists.",
    "After creation, read the file to confirm contents when necessary."
  ]
}
"""


Finish_prompt = """
{
  "name": "Finish",
  "description": "Signal that the task is complete or cannot be completed. The final explanation must live in the `response` field of the same round.",
  "parameters": {"type": "object", "properties": {}, "required": []},
  "returns": "No payload—conversation ends after this action.",
  "safety_notes": [],
  "usage_notes": [
    "Use after fulfilling the requirements, or after explaining why the task is impossible / unsafe.",
    "Summaries should mention what was done, where outputs live, and any follow-up needed."
  ]
}
"""


talk_with_user_prompt = """
{
  "name": "talk_with_user",
  "description": "Start an interactive turn with the human user to ask a clear question, get clarification, or request explicit approval.",
  "parameters": {"type": "object", "properties": {}, "required": []},
  "returns": "User-provided text, or `Error reading user input: ...`.",
  "safety_notes": [
    "Explain exactly what information or permission you need.",
    "Use before irreversible actions such as deletions, overwrites, or dangerous shell commands.",
    "Do not ask multiple unrelated questions in a single turn."
  ],
  "usage_notes": [
    "In the same round where you call `talk_with_user`, put the exact question you want to ask the human in the `response` field so the user can see it.",
    "Keep questions focused—do not over-interrogate the user.",
    "Record the reason for asking in `think` and summarize the user's answer in the next `observation`."
  ]
}
"""


fetch_webpage_prompt = """
{
  "name": "fetch_webpage",
  "description": "Fetch a web page and return cleaned text (HTML stripped). Ideal for articles, blogs, and documentation.",
  "parameters": {
    "type": "object",
    "properties": {
      "url": {"type": "string", "description": "HTTP/HTTPS URL to fetch."}
    },
    "required": ["url"]
  },
  "returns": "Clean text or `error in fetching webpage {url}: ...`.",
  "safety_notes": [
    "Only fetch publicly accessible content.",
    "Network requests may fail or timeout—plan fallbacks."
  ],
  "usage_notes": [
    "Use `fetch_webpage_with_selector` if you only need a specific section.",
    "For very large pages, consider summarizing sections incrementally."
  ]
}
"""


fetch_webpage_with_selector_prompt = """
{
  "name": "fetch_webpage_with_selector",
  "description": "Fetch a web page but only return text that matches a CSS selector (e.g., `article`, `.content`, `#main`).",
  "parameters": {
    "type": "object",
    "properties": {
      "url": {"type": "string", "description": "HTTP/HTTPS URL."},
      "selector": {"type": "string", "description": "CSS selector to target (defaults to `body` if omitted)."}
    },
    "required": ["url"]
  },
  "returns": "Text for matching elements, `No elements found with selector: {selector}` when empty, or a fetch error string.",
  "safety_notes": [
    "Same network considerations as `fetch_webpage`."
  ],
  "usage_notes": [
    "Describe in `think` why the selector should capture the needed region.",
    "If unsure about DOM structure, fetch the full page once to inspect."
  ]
}
"""


read_word_document_prompt = """
{
  "name": "read_word_document",
  "description": "Parse a .docx file and return an ordered list of text runs plus Base64-encoded images in the order they appear.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "Path to the .docx file."}
    },
    "required": ["path"]
  },
  "returns": "List mixing text and Base64 image payloads, or `error in reading {path}: ...`.",
  "safety_notes": [
    "Large documents with many images can produce huge outputs—plan accordingly.",
    "Only .docx is supported."
  ],
  "usage_notes": [
    "Mention in `think` which sections you need to extract.",
    "For table-heavy docs, consider `extract_info_from_docx_table`."
  ]
}
"""


extract_info_from_docx_table_prompt = """
{
  "name": "extract_info_from_docx_table",
  "description": "Extract every populated cell from all tables inside a .docx file, returning one line per cell in reading order.",
  "parameters": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string", "description": "Path to the .docx file that contains tables."}
    },
    "required": ["file_path"]
  },
  "returns": "Plain-text list of cell contents or a descriptive error string.",
  "safety_notes": [
    "Ignores non-table text.",
    "Large tables can return very long strings—summarize if needed."
  ],
  "usage_notes": [
    "State which fields you are hunting for so reviewers know why the tool was used.",
    "Use when you need structured data rather than the entire document body."
  ]
}
"""


execute_command_prompt = """
{
  "name": "execute_command",
  "description": "Run a shell command through a managed terminal. Supports both one-shot commands and interactive programs; the tool will keep an internal session so you can call it multiple times in a row to continue the interaction.",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "A single shell command (one line you would normally type then press Enter). Avoid chaining/piping (no &&, ||, ;, |)."
      }
    },
    "required": ["command"]
  },
  "returns": "Combined stdout/stderr produced during this call, plus basic status.",
  "safety_notes": [
    "Explain in `response` why this command is needed and whether it might modify files, the repository, or the environment.",
    "Prefer read-only/investigative commands before making changes.",
    "For destructive or high-risk commands (e.g., deleting files, formatting disks, killing important processes, heavy network operations), clearly describe the risk and purpose so the user can make an informed choice.",
    "Long-running or interactive programs are allowed, but always drive them step-by-step (one command per call) instead of starting uncontrolled background tasks."
  ],
  "usage_notes": [
    "Use one logical shell line per call (no pipelines/chains).",
    "For interactive flows: first start the program (for example, `python -i -u`) with one call, then send subsequent inputs as new calls to `execute_command`.",
    "Treat each call as if a human typed a single line and pressed Enter, then waited for the output to stabilize.",
    "Summarize the command's purpose and potential risk in `response` so the user knows what will happen.",
    "Inspect stderr if the command fails and adjust the next command accordingly."
  ]
}
"""


if __name__ == "__main__":
    import json
    print(json.loads(execute_command_prompt).keys())
