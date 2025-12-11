# some file management related tools for agent calling:
from pathlib import Path
import os
import time
import shutil
import subprocess
import os
from typing import Tuple, Optional
from Agent.tools.Tools import Tool_
from Agent.prompts.tools_prompt import tree_file_prompt, delete_dir_prompt, delete_file_prompt, get_absolute_cur_path_prompt, execute_command_prompt

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
    """
    执行系统命令（带安全与许可控制）

    行为约定：
    - 仅允许预定义白名单中的主命令。
    - 可能修改文件/仓库/环境的命令，执行前会在控制台显式询问用户输入 yes 确认；
      若上层已获得同意，可传 user_confirmed=True 跳过二次确认。
    - 只读查询类命令（如 git status、dir/ls、pip list 等）直接执行。
    - 禁止命令链/管道（例如 &&、||、;、|）以及高危系统命令（shutdown/sudo 等）。
    """
    
    def __init__(self):
        super().__init__(execute_command_prompt)
        # 安全命令白名单（是否需许可由 _needs_user_consent 判定）
        self.safe_commands = {
            # 语言/运行时
            "python", "python3", "node",
            # 包管理
            "pip", "pip3", "poetry", "conda",
            "npm", "yarn", "pnpm",
            # Git
            "git",
            # 系统/信息/查询
            "which", "where", "echo",
            "ps", "tasklist", "netstat",
            "systeminfo", "hostname", "whoami",
            "dir", "ls", "type", "cat", "findstr", "grep", "tree",
            # 文件/目录操作（修改类命令运行前将请求许可）
            "copy", "cp", "xcopy", "robocopy",
            "move", "mv", "rename", "ren",
            "mkdir", "md", "rmdir", "rd",
            "del", "rm",
        }
        # 永久禁止（高危/系统级）
        self.danger_forbidden = {
            "shutdown", "reboot", "poweroff", "halt",
            "format", "fdisk", "mkfs", "diskpart",
            "sudo", "su",
        }
        
    def __call__(self, command: str, user_confirmed: Optional[bool] = None) -> str:
        timeout=60
        is_safe, reason = self._is_safe_command(command)
        if not is_safe:
            return f"Security check failed: {reason}\nCommand: {command} is not allowed"
        # 用户许可判定
        parts = command.strip().split()
        main_cmd = parts[0].lower() if parts else ""
        needs_consent, why = self._needs_user_consent(command, parts, main_cmd)
        if needs_consent and user_confirmed is not True:
            if not self._confirm_with_user(command, why):
                return f"Execution cancelled.\nReason: {why}\nCommand: {command}"
        try:
            print(f"Running Command: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            # 构建返回信息
            output_lines = []
            output_lines.append(f"Command completed (return code: {result.returncode})")
            output_lines.append(f"Command: {command}")
            
            if result.stdout:
                output_lines.append("\n--- command output ---")
                output_lines.append(result.stdout.strip())
            
            if result.stderr:
                output_lines.append("\n--- command error ---")
                output_lines.append(result.stderr.strip())
            
            # If command failed
            if result.returncode != 0:
                output_lines.insert(0, f"Command failed (exit code: {result.returncode})")
            
            return "\n".join(output_lines)
            
        except subprocess.TimeoutExpired:
            return f"❌ Command timed out (>{timeout}s)\nCommand: {command}"
        
        except Exception as e:
            return f"❌ Command execution error: {str(e)}\nCommand: {command}"
    
        
        
    def _is_safe_command(self, command: str) -> Tuple[bool, str]:
        """
        检查命令是否安全
        
            command: 要执行的命令字符串
            
        Returns:
            (是否安全, 原因说明)
        """
        command_lower = command.lower().strip()
        
        # 检查空命令
        if not command_lower:
            return False, "empty command"
        
        # 检查命令链
        if any(sep in command for sep in ["&&", "||", ";", "|"]):
            return False, "Command chaining or piping is not allowed; execute commands separately"
        
        # 提取主命令
        parts = command_lower.split()
        if not parts:
            return False, "invalid command"
        
        main_cmd = parts[0]
        
        # 高危命令直接禁止
        if any(bad in command_lower.split() for bad in self.danger_forbidden):
            return False, "contains forbidden high-risk command"
        
        # 检查主命令是否在白名单
        if main_cmd not in self.safe_commands:
            return False, f"Command '{main_cmd}' is not in the safe whitelist"
        
        # 禁止启动交互式 REPL（无参数）
        if main_cmd in ["python", "python3", "node"] and len(parts) == 1:
            return False, f"Starting interactive {main_cmd} session is not allowed"
        
        return True, "Command passed security check"

    def _needs_user_consent(self, command: str, parts: list, main_cmd: str) -> Tuple[bool, str]:
        """
        判断命令是否需要用户许可（可能修改文件/仓库/环境）
        """
        cl = command.lower()

        # 文件重定向写入（覆盖或追加）都视为修改
        if ">>" in cl or ">" in cl:
            return True, "Contains output redirection; may write/overwrite files"

        # 文件/目录操作：一律视为修改
        file_write_cmds = {
            "copy", "cp", "xcopy", "robocopy",
            "move", "mv", "rename", "ren",
            "mkdir", "md", "rmdir", "rd",
            "del", "rm",
        }
        if main_cmd in file_write_cmds:
            why = {
                "copy": "file copy/overwrite", "cp": "file copy/overwrite", "xcopy": "file copy/overwrite", "robocopy": "file copy/overwrite",
                "move": "move/rename", "mv": "move/rename", "rename": "move/rename", "ren": "move/rename",
                "mkdir": "create directory", "md": "create directory",
                "rmdir": "delete directory", "rd": "delete directory",
                "del": "delete file", "rm": "delete file",
            }.get(main_cmd, "filesystem modification")
            return True, f"{why}"

        # Git：读写分流
        if main_cmd == "git":
            action = parts[1] if len(parts) > 1 else ""
            read_only = {
                "status", "log", "diff", "branch", "remote", "config",
                "show", "rev-parse", "ls-files", "describe", "blame",
            }
            if action in read_only:
                return False, "Git read-only operation"
            # Other git actions are assumed to modify
            return True, f"Git '{action}' may modify the workspace/repository"

        # 包管理器：安装/卸载/更新/发布等需要许可
        if main_cmd in {"pip", "pip3", "poetry", "conda"}:
            action = parts[1] if len(parts) > 1 else ""
            read_only = {"list", "show", "freeze", "check", "info", "search"}
            if action in read_only:
                return False, "Package manager read-only query"
            return True, f"{main_cmd} '{action or 'command'}' may modify the environment"

        if main_cmd in {"npm", "yarn", "pnpm"}:
            action = parts[1] if len(parts) > 1 else ""
            read_only = {"list", "ls", "outdated", "audit", "view", "info"}
            if action in read_only:
                return False, "Package manager read-only query"
            return True, f"{main_cmd} '{action or 'command'}' may modify environment/dependencies"

        # 运行脚本：默认需要许可（无法静态判断是否写入）
        if main_cmd in {"python", "python3", "node"}:
            return True, "Running scripts may modify environment or files"

        # 其他常见只读查询命令
        read_only_cmds = {
            "which", "where", "echo", "ps", "tasklist", "netstat",
            "systeminfo", "hostname", "whoami", "dir", "ls", "type", "cat",
            "findstr", "grep", "tree",
        }
        if main_cmd in read_only_cmds:
            return False, "read-only query command"

        # Default conservative: require consent
        return True, "Unable to determine safety; user confirmation required"

    def _confirm_with_user(self, command: str, reason: str) -> bool:
        """
        在控制台显式询问用户许可
        """
        print("About to execute a command that may modify system/files/repository:")
        print(f"- Reason: {reason}")
        print(f"- Working directory: {os.getcwd()}")
        print(f"- Command: {command}")
        try:
            resp = input("Confirm execution? Type 'yes' to continue (any other key cancels):").strip().lower()
            return resp == "yes"
        except Exception:
            return False
    
    
    
    
if __name__ == "__main__":
    command_line = "pip freeze > docs/requirements.txt"
    print(execute_command()(command_line))