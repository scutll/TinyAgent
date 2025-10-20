def log(message):
    """写入日志"""
    log_file_path = f"logs/agent_run_log.txt"
    try:
        with open(log_file_path, "a", encoding='utf-8') as f:
            # 如果 message 不是字符串，先转换为字符串
            if not isinstance(message, str):
                message = str(message)
            f.write(message + '\n')
            f.flush()
    except Exception as e:
        print(f"failed to log: {e}")