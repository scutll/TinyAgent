tree_file_prompt = """
{
  "name": "tree_file",
  "description": "Recursively list the entire directory tree (similar to the `tree` command) to understand project layout and locate deeply nested files.",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  },
  "returns": "Plain-text tree that uses characters such as `├──` and `└──`. Errors return a descriptive string.",
  "safety_notes": [],
  "usage_notes": [
    "Useful before structural changes or when you need a quick mental map of the repo.",
    "Large projects can generate long outputs—decide in `think` whether it is necessary."
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
    "Run before constructing relative paths if you're unsure about the current location."
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
        "type": "string",
        "description": "Path to the text file (relative to CWD or absolute)."
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
    "Preview structure with `tree_file` if the path is uncertain.",
    "For large files, plan which sections you truly need."
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


inquery_user_prompt = """
{
  "name": "inquery_user",
  "description": "Ask the user for clarification or explicit approval when intent is unclear or when an operation is high risk.",
  "parameters": {"type": "object", "properties": {}, "required": []},
  "returns": "User-provided text, or `Error reading user input: ...`.",
  "safety_notes": [
    "Explain exactly what information or permission you need.",
    "Use before irreversible actions such as deletions, overwrites, or dangerous shell commands."
  ],
  "usage_notes": [
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
  "description": "Run a single shell command from a curated allowlist. Read-only commands run immediately; commands that modify files/envs trigger an in-terminal confirmation step.",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "Command without chaining or piping (no &&, ||, ;, |)."
      }
    },
    "required": ["command"]
  },
  "returns": "Combined stdout/stderr plus the exit code.",
  "policy": {
    "read_only": [
      "Filesystem queries: dir/ls/tree/type/cat/findstr/grep/which/where/echo",
      "System info: hostname/whoami/systeminfo/tasklist/ps/netstat",
      "Package managers (list/show/freeze/search/outdated) for pip/conda/npm/yarn/pnpm",
      "Git read-only: status/log/diff/branch/remote/show/rev-parse/ls-files/describe/blame"
    ],
    "needs_confirmation": [
      "File edits: copy/move/rename/mkdir/rmdir/del/rm",
      "Redirections using > or >>",
      "Script execution: python/node <script>",
      "Package installs/updates/removals",
      "Git mutations: add/commit/push/pull/merge/rebase/checkout/clone"
    ],
    "forbidden": [
      "Command chains or pipes (&&, ||, ;, |)",
      "Privilege or system operations: sudo/su/shutdown/reboot/poweroff/format/diskpart"
    ]
  },
  "safety_notes": [
    "Explain in `think` why the command is required and what risk mitigation you applied.",
    "Prefer investigative commands before making changes.",
    "Avoid commands that launch interactive REPLs."
  ],
  "usage_notes": [
    "Split multi-step workflows into separate calls.",
    "Summarize the command's purpose in `response` so the user knows what to expect.",
    "Inspect stderr if the command fails and adjust accordingly."
  ]
}
"""


if __name__ == "__main__":
    import json
    print(json.loads(execute_command_prompt).keys())
