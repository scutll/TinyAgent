# some file management related tools for agent calling:
from pathlib import Path
import os
import time
import shutil

def list_file(params: str = ""):
    '''
    list_file: show the file list --> ls in terminal \n
    args: str such as '-l' to specify the mode to show listfiles \n 
    return: a string showing the file list in current path\n
    '''
    
    path = "."
    if params == "":
        p = Path(path)
        return {"text": '\n'.join(f.name for f in p.iterdir())}
    if "-l" in params:
        """
        模拟 ls -l 命令，列出当前路径下所有文件和文件夹的详细信息
        """
        # 获取目录下所有文件/文件夹
        entries = os.listdir(path)
        result_lines = []

        for name in entries:
            full_path = os.path.join(path + "/", name)

            # 判断文件类型
            type_flag = 'd' if os.path.isdir(full_path) else 'f'

            # 获取文件大小（字节）
            size = os.path.getsize(full_path)

            # 获取最后修改时间
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(full_path)))

            # 拼接成一行
            line = f"{type_flag}\t{size:>10}\t{mtime}\t{name}"
            result_lines.append(line)
            
        return {"text": '\n'.join(result_lines)}



import os

def tree_file(path='.', prefix=''):
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
            sub_tree = tree_file(full_path, prefix + extension)
            if sub_tree:
                result_lines.append(sub_tree)

    # 根层调用返回完整字符串
    if prefix == '':
        return "\n".join(result_lines)
    else:
        return "\n".join(result_lines)

 
    
def delete_file(filename: str):
    '''
    delete_file: delete a file \n
    args: filename \n
    return: {filename} deleted! or Exception message for deleting failed
    '''
    try:
        os.remove(filename)
        return {"text": f"{filename} deleted!"}
    except Exception as e:
        return {"text": f"Error deleting {filename}: {e}"}
    



def delete_dir(directory: str):
    """
    delete_dir: delete the whole directory recursively\n
    args: name of directory\n
    return : {directory} and its contents deleted! or Exception message if failed
    """
    try:
        # 判断目录是否存在
        if not os.path.exists(directory):
            return {"text": f"Error: {directory} does not exist."}
        
        # 判断是否是目录
        if not os.path.isdir(directory):
            return {"text": f"Error: {directory} is not a directory."}

        # 使用 shutil.rmtree() 递归删除目录及其内容
        shutil.rmtree(directory)
        return {"text": f"{directory} and its contents deleted!"}
    
    except Exception as e:
        return {"text": f"Error deleting {directory}: {e}"}



def get_absolute_cur_path():
    """
    return the absolute path of current working directory
    """
    return {"text": os.path.abspath(os.getcwd())}


    
