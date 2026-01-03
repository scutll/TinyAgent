# some file management related tools for agent calling:
from pathlib import Path
import os
import time
import shutil
import json
from typing import Tuple, Optional
from Agent.tools.Tools import Tool_
from Agent.prompts.tools_prompt import tree_file_prompt, delete_dir_prompt, delete_file_prompt, get_absolute_cur_path_prompt, execute_command_prompt
from Agent.utils.terminal.manager import TerminalSessionManager

class tree_file(Tool_):
    def __init__(self):
        super().__init__(tree_file_prompt)
        
    def __call__(self, start_path='.', search_depth=3, ignore_list=None):
        if ignore_list is None:
                ignore_list = []
        search_depth = max(1, min(4, int(search_depth)))

        if not os.path.exists(start_path):
            return f"[Error] Path not found: {start_path}"

        def _build(path, depth, prefix):
            try:
                entries = sorted(os.listdir(path))
            except PermissionError:
                return f"{prefix}└── [Permission denied]: {os.path.basename(path)}"

            lines = []
            for i, name in enumerate(entries):
                full = os.path.join(path, name)

                # ======== 新增：ignore_list 内的目录完全不显示 ========
                if name in ignore_list:
                    continue
                # ====================================================

                is_last = (i == len(entries) - 1)
                connector = '└── ' if is_last else '├── '
                lines.append(f"{prefix}{connector}{name}")

                if os.path.isdir(full):
                    if depth >= search_depth:
                        continue
                    extension = '    ' if is_last else '│   '
                    subtree = _build(full, depth + 1, prefix + extension)
                    if subtree:
                        lines.append(subtree)

            return "\n".join(lines)

        return _build(start_path, depth=1, prefix="")



class delete_file(Tool_):
    def __init__(self):
        super().__init__(delete_file_prompt)
        
    def __call__(self, filename: str):
        '''
        delete_file: delete a file \n
        args: filename \n
        return: {filename} deleted! or Exception message for deleting failed
        '''
        try:
            os.remove(filename)
            return f"{filename} deleted!"
        except Exception as e:
            return f"Error deleting {filename}: {e}"
    


class delete_dir(Tool_):
    def __init__(self):
        super().__init__(delete_dir_prompt)
        
    def __call__(self, directory: str):
        """
        delete_dir: delete the whole directory recursively\n
        args: name of directory\n
        return : {directory} and its contents deleted! or Exception message if failed
        """
        try:
            # 判断目录是否存在
            if not os.path.exists(directory):
                return f"Error: {directory} does not exist."
            
            # 判断是否是目录
            if not os.path.isdir(directory):
                return f"Error: {directory} is not a directory."

            # 使用 shutil.rmtree() 递归删除目录及其内容
            shutil.rmtree(directory)
            return f"{directory} and its contents deleted!"
        
        except Exception as e:
            return f"Error deleting {directory}: {e}"


class get_absolute_cur_path(Tool_):
    def __init__(self):
        super().__init__(get_absolute_cur_path_prompt)
        
    def __call__(self):
        """
        return the absolute path of current working directory
        """
        return os.path.abspath(os.getcwd())


    
class execute_command(Tool_):
    """执行系统命令（简化版安全控制）

    新行为约定：
    - 保留一个「只读命令白名单」，用于常见的信息查询类命令（如 dir/ls、git status、pip list 等）。
    - 白名单中的命令：默认视为只读，可以直接执行，不再重复询问是否确认。
    - 白名单外的任何命令：统一视为「可能有副作用」，每次执行前都在控制台询问用户输入 `y` 以确认执行。
    - 不再维护复杂的高危禁止列表和细粒度判定逻辑，风险由用户在确认时自行把控。
    """

    def __init__(self):
        super().__init__(execute_command_prompt)
        # 只读命令白名单（常见信息查询 / 枚举类命令）
        self.read_only_whitelist = {
            # 系统/信息/查询
            "which", "where", "echo",
            "ps", "tasklist", "netstat",
            "systeminfo", "hostname", "whoami",
            "dir", "ls", "type", "cat", "findstr", "grep", "tree",
            # Git 只读常用命令
            "git status", "git log", "git diff", "git branch",
            "git remote", "git show", "git rev-parse", "git ls-files",
            # 包管理只读子命令（通过前缀匹配简单处理）
            "pip list", "pip show", "pip freeze", "pip check", "pip search",
            "pip3 list", "pip3 show", "pip3 freeze", "pip3 check", "pip3 search",
            "poetry show", "poetry info",
            "conda list", "conda info", "conda search",
            "npm list", "npm ls", "npm outdated", "npm audit", "npm view", "npm info",
            "yarn list", "yarn outdated", "yarn audit", "yarn info",
            "pnpm list", "pnpm ls", "pnpm outdated", "pnpm audit", "pnpm view", "pnpm info",
        }
        # 运行时允许直接执行的命令前缀（可通过用户选择动态添加），例如 "javac"、"python my_safe_script.py" 等
        self.allow_list_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "allow_cmd_list.json")
        self.dynamic_allowlist = self._load_allow_list()
        # 长生命周期 shell session 管理，用于支持需要持续交互的命令
        self.session_manager = TerminalSessionManager()

    def __call__(
        self,
        command: str,
    ) -> str:
        """执行命令（对外只暴露一个 command 参数）

        - 外部：Agent 只需要提供一行命令字符串；可以多次调用本工具，像人在同一个终端里一行一行输入一样，从而实现交互式会话。
        - 内部：通过 TerminalSessionManager 维护一个长生命周期的 shell session（默认 id="default"），并在每次调用时写入命令并等待输出稳定后返回。
        """

        # 空命令直接拒绝
        if not command or not command.strip():
            return "Security check failed: empty command is not allowed"

        normalized = " ".join(command.strip().split()).lower()

        # 判定是否在只读白名单内（前缀匹配，兼容带参数情况）
        is_read_only = any(
            normalized == item or normalized.startswith(item + " ")
            for item in self.read_only_whitelist
        )

        # 判定是否在动态 allow list 内（前缀匹配），如 "javac" 匹配所有 "javac ..." 命令
        is_in_allow_list = any(
            normalized == item or normalized.startswith(item + " ")
            for item in self.dynamic_allowlist
        )

        # 白名单 + allow list 内命令：直接执行，仅做一个浅色提示
        if is_read_only or is_in_allow_list:
            RESET = "\033[0m"
            DARK_GRAY = "\033[90m"
            print(f"{DARK_GRAY}Running Command (no extra confirmation):{DARK_GRAY}\n{RESET}{command}")
        else:
            # 需要用户确认：y=仅执行一次，Y=执行并将前缀添加到 allow list
            confirmed, add_prefix = self._confirm_with_user(command)
            if not confirmed:
                return f"Execution cancelled by user.\nCommand: {command}"
            if add_prefix:
                self._add_to_allow_list(command)

        try:

            # 这里固定使用一个内部 session_id（"default"），对 Agent 层完全透明。
            session_result = self.session_manager.send_command(
                session_id="default",
                command=command,
            )

            stdout_block = session_result.get("stdout", "").strip()
            stderr_block = session_result.get("stderr", "").strip()

            output_lines = []
            output_lines.append("Command completed")
            output_lines.append(f"Command: {command}")

            if stdout_block:
                output_lines.append("\n--- command output ---")
                output_lines.append(stdout_block)

            if stderr_block:
                output_lines.append("\n--- command error ---")
                output_lines.append(stderr_block)

            return "\n".join(output_lines)

        except Exception as e:
            return f"❌ Command execution error: {str(e)}\nCommand: {command}"
    
        
        
    def _confirm_with_user(self, command: str) -> Tuple[bool, bool]:
        """在控制台显式询问用户许可

        返回 (是否允许运行, 是否将前缀命令加入 allow list)
        小写 y: 只允许运行本次，不加入列表；
        大写 Y: 允许运行，并将前缀命令加入 allow_cmd_list.json。
        """
        try:
            RESET = "\033[0m"
            DARK_GRAY = "\033[90m"
            resp = input(
                f"{DARK_GRAY}Allow executing command? [y/n] (Y to remember cmd prefix){RESET}\n"
                f"{command}\n> "
            ).strip()
            if resp == "y":
                return True, False
            if resp == "Y":
                return True, True
            return False, False
        except Exception:
            return False, False

    def _extract_prefix(self, command: str) -> str:
        """提取用于 allow list 的前缀命令

        当前实现：取命令行的第一个 token（主命令），例如：
        - "javac Main.java" -> "javac"
        - "python script.py" -> "python"
        后续如需更细粒度（例如 "python my_safe_script.py"），可在此扩展。"""
        parts = command.strip().split()
        return parts[0].lower() if parts else ""

    def _load_allow_list(self):
        """从 allow_cmd_list.json 加载动态允许列表，不存在则返回空集合"""
        try:
            if os.path.exists(self.allow_list_path):
                with open(self.allow_list_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # 统一转为小写字符串集合
                return set(str(item).strip().lower() for item in data if str(item).strip())
        except Exception:
            pass
        return set()

    def _save_allow_list(self):
        """将当前 dynamic_allowlist 保存到 allow_cmd_list.json"""
        try:
            with open(self.allow_list_path, "w", encoding="utf-8") as f:
                json.dump(sorted(self.dynamic_allowlist), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[execute_command] Failed to save allow_cmd_list.json: {e}")

    def _add_to_allow_list(self, command: str):
        """将命令前缀添加到 allow list 并持久化到 allow_cmd_list.json"""
        prefix = self._extract_prefix(command)
        if not prefix:
            return
        if prefix in self.dynamic_allowlist:
            return
        self.dynamic_allowlist.add(prefix)
        self._save_allow_list()
    
    
    
    
if __name__ == "__main__":
    command_line = "java test"
    print(execute_command()(command_line))