def log(message):
    """写入日志"""
    log_file_path = f"logs/agent_run_log.txt"
    with open(log_file_path, "a", encoding='utf-8') as f:
        f.write(message + '\n')
        f.flush()