# some file management related tools for agent calling:
from pathlib import Path
import os
import time
import shutil
import os
from Agent.tools.Tools import Tool_
from Agent.prompts.tools_prompt import tree_file_prompt, delete_dir_prompt, delete_file_prompt, get_absolute_cur_path_prompt

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


    
