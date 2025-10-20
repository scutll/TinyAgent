# 当LLM希望执行某项可能修改/删除某个文件内容的许可，或执行一些可能引发危险的命令的时候 询问用户以取得许可
# 当LLM对用户的一些意图(是否要修改某文件/是否要创建文件/目的)不够明确时，为减缓幻觉的发生，向用户询问必要的信息
# 当LLM希望提问时，应该简单说明LLM想要获取的信息或许可，提示用户需要他输入信息
def inquery_uesr():
    """
    To ask user question to make Agent more clearly on user's target and task
    params: None
    return: user's explaination
    """
    print("--------------------------------")
    try:
        user_input = input("(User): ")
    except Exception as e:
        user_input = f"Error reading user input: {e}"
    print("--------------------------------")
    
    return user_input