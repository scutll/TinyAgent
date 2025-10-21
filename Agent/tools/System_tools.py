# some file management related tools for agent calling:
from pathlib import Path
import os
import time
import shutil
import subprocess
import os
from typing import Tuple
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
    
    def __init__(self):
        super().__init__(execute_command_prompt)
        # 安全命令白名单
        self.safe_commands = {
            # Python 包管理
            "pip", "pip3", "poetry", "conda",
            # Node.js 包管理
            "npm", "yarn", "pnpm",
            # 项目启动
            "python", "python3", "node",
            # 环境信息查询
            "which", "where", "echo",
            # Git 只读操作
            "git",
            # 进程查看
            "ps", "tasklist", "netstat",
            # 系统信息
            "systeminfo", "hostname", "whoami",
        }
        self.forbidden_keywords = {
            "rm", "del", "rmdir", "rd",
            "mv", "move", "rename", "ren",
            "copy", "cp", "xcopy",
            "mkdir", "md", "touch",
            "chmod", "chown", "sudo", "su",
            "shutdown", "reboot", "format", "fdisk",
        }
        
        # Git 危险操作
        self.git_forbidden = {
            "push", "commit", "add", "rm", "clone", "pull", "fetch", "merge"
        }
        
    def __call__(self, command: str) -> str:
        timeout=60
        is_safe, reason = self._is_safe_command(command)
        if not is_safe:
            return f"安全检查失败: {reason}\n 命令:{command}不允许执行"    
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
        
        # 检查文件覆盖重定向
        if ">" in command and ">>" not in command:
            return False, "不允许使用 '>' 覆盖文件"
        
        # 提取主命令
        parts = command_lower.split()
        if not parts:
            return False, "无效命令"
        
        main_cmd = parts[0]
        
        # 检查危险关键词
        for forbidden in self.forbidden_keywords:
            if forbidden in command_lower:
                return False, f"包含禁止的命令: {forbidden}"
        
        # Git 特殊检查
        if main_cmd == "git":
            if len(parts) < 2:
                return False, "Git 命令不完整"
            
            git_action = parts[1]
            if git_action in self.git_forbidden:
                return False, f"Git 不允许执行写操作: {git_action}"
            
            # 只允许只读操作
            allowed_git = ["status", "log", "diff", "branch", "remote", "config"]
            if git_action not in allowed_git:
                return False, f"Git 只允许只读操作: {', '.join(allowed_git)}"
            
            return True, "Git 只读操作"
        
        # 检查主命令是否在白名单
        if main_cmd not in self.safe_commands:
            return False, f"命令 '{main_cmd}' 不在安全白名单中"
        
        # Python/Node 限制
        if main_cmd in ["python", "python3"]:
            if "-m" not in parts and not any(p.endswith(".py") for p in parts):
                return False, "Python 只允许运行模块(-m)或 .py 文件"
        
        # pip/npm 安全检查
        if main_cmd in ["pip", "pip3", "npm", "yarn", "pnpm"]:
            allowed_actions = ["install", "list", "show", "freeze", "check", 
                            "outdated", "audit", "start", "run", "ci"]
            if len(parts) > 1 and parts[1] not in allowed_actions:
                return False, f"{main_cmd} 只允许: {', '.join(allowed_actions)}"
        
        return True, "命令通过安全检查"
    
    
    
    
if __name__ == "__main__":
    command_line = "conda env list"
    print(execute_command()(command_line))