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

def tree_file(path='.', prefix = ''):
    '''
    tree_file: show files recursively in a tree \n
    args : None \n
    return: a str show the files structure in a tree\n
    '''
    entries = os.listdir(path)
    entries.sort()

    result_lines = []

    for index, name in enumerate(entries):
        full_path = os.path.join(path, name)
        is_last = index == len(entries) - 1  # 判断是不是当前层的最后一个
        connector = '└── ' if is_last else '├── '
        result_lines.append(prefix + connector + name)

        # 如果是文件夹，递归打印它的内容
        if os.path.isdir(full_path):
            extension = '    ' if is_last else '│   '
            result_lines.append(tree_file(full_path, prefix + extension))

    return {"text": '\n'.join(result_lines)}
 
    
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


    
