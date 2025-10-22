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
        
    def __call__(self, path='.', prefix=''):
        """
        递归生成目录树字符串
        :param path: 要展示的目录路径
        :param prefix: 内部递归使用的前缀字符串
        :return: 目录结构字符串
        """
        # 确保路径存在
        if not os.path.exists(path):
            return f"[Error] 路径不存在: {path}"

        # 列出目录下所有文件和文件夹
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return f"{prefix}└── [权限不足]: {os.path.basename(path)}"

        # 构建结果字符串列表
        result_lines = []

        for i, name in enumerate(entries):
            full_path = os.path.join(path, name)
            is_last = i == len(entries) - 1

            # 树形符号
            connector = '└── ' if is_last else '├── '

            # 当前行
            result_lines.append(f"{prefix}{connector}{name}")

            # 若是文件夹，递归调用
            if os.path.isdir(full_path):
                # 为子目录设置缩进前缀
                extension = '    ' if is_last else '│   '
                sub_tree = self(full_path, prefix + extension)
                if sub_tree:
                    result_lines.append(sub_tree)

        # 根层调用返回完整字符串
        if prefix == '':
            return "\n".join(result_lines)
        else:
            return "\n".join(result_lines)



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
            return f"安全检查失败: {reason}\n 命令:{command}不允许执行"    
        # 用户许可判定
        parts = command.strip().split()
        main_cmd = parts[0].lower() if parts else ""
        needs_consent, why = self._needs_user_consent(command, parts, main_cmd)
        if needs_consent and user_confirmed is not True:
            if not self._confirm_with_user(command, why):
                return f"已取消执行。\n原因: {why}\n命令: {command}"
        try:
            print(f"执行命令: {command}")

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
            output_lines.append(f"命令执行完成 (return code: {result.returncode})")
            output_lines.append(f"命令: {command}")
            
            if result.stdout:
                output_lines.append("\n--- command output ---")
                output_lines.append(result.stdout.strip())
            
            if result.stderr:
                output_lines.append("\n--- command error ---")
                output_lines.append(result.stderr.strip())
            
            # 如果命令失败
            if result.returncode != 0:
                output_lines.insert(0, f"命令执行失败 (退出码: {result.returncode})")
            
            return "\n".join(output_lines)
            
        except subprocess.TimeoutExpired:
            return f"❌ 命令执行超时（>{timeout}秒）\n命令: {command}"
        
        except Exception as e:
            return f"❌ 命令执行异常: {str(e)}\n命令: {command}"
    
        
        
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
            return False, "空命令"
        
        # 检查命令链
        if any(sep in command for sep in ["&&", "||", ";", "|"]):
            return False, "不允许命令链或管道操作，请逐条执行命令"
        
        # 提取主命令
        parts = command_lower.split()
        if not parts:
            return False, "无效命令"
        
        main_cmd = parts[0]
        
        # 高危命令直接禁止
        if any(bad in command_lower.split() for bad in self.danger_forbidden):
            return False, "包含高危命令，已禁止"
        
        # 检查主命令是否在白名单
        if main_cmd not in self.safe_commands:
            return False, f"命令 '{main_cmd}' 不在安全白名单中"
        
        # 禁止启动交互式 REPL（无参数）
        if main_cmd in ["python", "python3", "node"] and len(parts) == 1:
            return False, f"不允许启动交互式 {main_cmd} 会话"
        
        return True, "命令通过安全检查"

    def _needs_user_consent(self, command: str, parts: list, main_cmd: str) -> Tuple[bool, str]:
        """
        判断命令是否需要用户许可（可能修改文件/仓库/环境）
        """
        cl = command.lower()

        # 文件重定向写入（覆盖或追加）都视为修改
        if ">>" in cl or ">" in cl:
            return True, "包含输出重定向，可能写入/覆盖文件"

        # 文件/目录操作：一律视为修改
        file_write_cmds = {
            "copy", "cp", "xcopy", "robocopy",
            "move", "mv", "rename", "ren",
            "mkdir", "md", "rmdir", "rd",
            "del", "rm",
        }
        if main_cmd in file_write_cmds:
            why = {
                "copy": "文件复制/覆盖", "cp": "文件复制/覆盖", "xcopy": "文件复制/覆盖", "robocopy": "文件复制/覆盖",
                "move": "移动/重命名", "mv": "移动/重命名", "rename": "移动/重命名", "ren": "移动/重命名",
                "mkdir": "创建目录", "md": "创建目录",
                "rmdir": "删除目录", "rd": "删除目录",
                "del": "删除文件", "rm": "删除文件",
            }.get(main_cmd, "文件系统修改")
            return True, f"{why}"

        # Git：读写分流
        if main_cmd == "git":
            action = parts[1] if len(parts) > 1 else ""
            read_only = {
                "status", "log", "diff", "branch", "remote", "config",
                "show", "rev-parse", "ls-files", "describe", "blame",
            }
            if action in read_only:
                return False, "Git 只读操作"
            # 其他 git 操作默认为修改
            return True, f"Git '{action}' 可能修改工作区/仓库"

        # 包管理器：安装/卸载/更新/发布等需要许可
        if main_cmd in {"pip", "pip3", "poetry", "conda"}:
            action = parts[1] if len(parts) > 1 else ""
            read_only = {"list", "show", "freeze", "check", "info", "search"}
            if action in read_only:
                return False, "包管理只读查询"
            return True, f"{main_cmd} '{action or '命令'}' 可能修改环境"

        if main_cmd in {"npm", "yarn", "pnpm"}:
            action = parts[1] if len(parts) > 1 else ""
            read_only = {"list", "ls", "outdated", "audit", "view", "info"}
            if action in read_only:
                return False, "包管理只读查询"
            return True, f"{main_cmd} '{action or '命令'}' 可能修改环境/依赖"

        # 运行脚本：默认需要许可（无法静态判断是否写入）
        if main_cmd in {"python", "python3", "node"}:
            return True, "运行脚本可能修改环境或文件"

        # 其他常见只读查询命令
        read_only_cmds = {
            "which", "where", "echo", "ps", "tasklist", "netstat",
            "systeminfo", "hostname", "whoami", "dir", "ls", "type", "cat",
            "findstr", "grep", "tree",
        }
        if main_cmd in read_only_cmds:
            return False, "只读查询命令"

        # 默认保守：需要许可
        return True, "无法判定安全性，需用户确认"

    def _confirm_with_user(self, command: str, reason: str) -> bool:
        """
        在控制台显式询问用户许可
        """
        print("即将执行可能修改系统/文件/仓库的命令：")
        print(f"- 原因：{reason}")
        print(f"- 工作目录：{os.getcwd()}")
        print(f"- 命令：{command}")
        try:
            resp = input("是否确认执行？输入 yes 继续（其他任意键取消）：").strip().lower()
            return resp == "yes"
        except Exception:
            return False
    
    
    
    
if __name__ == "__main__":
    command_line = "pip freeze > docs/requirements.txt"
    print(execute_command()(command_line))