from datetime import datetime
import msvcrt
import os
import time
from Agent.Core.agent_core import AgentCore
from typing import Any, Optional

from Agent.utils.input_style import _read_user_input
from Agent.utils.config import (
    _load_config,
    config_,
    delete_config,
    ensure_model,
    list_models,
    set_model_config,
    set_configured_model,
)
import argparse


def _safe_input(prompt: str) -> Optional[str]:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\n操作已取消!\n")
        return None


def _print_config_tree(node: Any, indent: int = 0) -> None:
    prefix = "  " * indent
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                _print_config_tree(value, indent + 1)
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(node, list):
        for index, item in enumerate(node):
            print(f"{prefix}[{index}]:")
            _print_config_tree(item, indent + 1)
    else:
        print(f"{prefix}{node}")


def _handle_settings_menu() -> None:
    while True:
        config_snapshot = _load_config()
        print("-" * 48)
        print("当前配置:")
        _print_config_tree(config_snapshot)
        print("-" * 48)
        print("1. 设置全局配置")
        print("2. 管理模型配置")
        print("3. 设置配置模型")
        print("4. 返回主菜单")
        choice = _safe_input("选择操作 [1-4]: ")
        if choice is None:
            return
        choice = choice.strip()
        if choice == "1":
            _handle_global_config()
        elif choice == "2":
            _handle_model_management()
        elif choice == "3":
            _handle_configured_model()
        elif choice in {"4", "", "q", "Q"}:
            break
        else:
            print("无效选择!\n")


def _handle_global_config() -> None:
    while True:
        action = _safe_input("选择操作: [a] 添加/更新 / [d] 删除 / [回车返回]: ")
        if action is None:
            print("已退出全局配置。\n")
            return
        action = action.strip().lower()
        if action == "" or action == "b":
            break
        if action not in {"a", "d"}:
            print("无效操作!\n")
            continue

        key = _safe_input("配置键: ")
        if key is None:
            print("该项操作已取消。\n")
            continue
        key = key.strip()
        if not key:
            print("键名不能为空!\n")
            continue

        if action == "d":
            try:
                delete_config(key)
                print("配置删除成功!\n")
            except KeyError:
                print("删除失败: 指定配置不存在。\n")
        else:
            value = _safe_input("配置值: ")
            if value is None:
                print("该项配置已取消。\n")
                continue
            config_(key, value)
            print("配置修改成功!\n")


def _handle_model_management() -> None:
    while True:
        config_snapshot = _load_config()
        models = list_models()
        if models:
            print("已配置模型:")
            for name in models:
                marker = "(配置中)" if config_snapshot.get("configured_model") == name else ""
                print(f" - {name} {marker}")
        else:
            print("当前没有配置任何模型，输入名称即可创建。")
        model_name = _safe_input("输入模型名称（回车返回）: ")
        if model_name is None:
            print("已退出模型管理。\n")
            return
        model_name = model_name.strip()
        if not model_name:
            break
        ensure_model(model_name)
        _edit_model_config(model_name)


def _edit_model_config(model_name: str) -> None:
    while True:
        config_snapshot = _load_config()
        model_config = (
            config_snapshot.get("models", {}).get(model_name, {})
        )
        print(f"[{model_name}] 当前配置:")
        if model_config:
            _print_config_tree(model_config, indent=1)
        else:
            print("  (暂无配置)")
        key = _safe_input(f"[{model_name}] 配置键（回车完成）: ")
        if key is None:
            print(f"已取消 {model_name} 的配置编辑。\n")
            return
        key = key.strip()
        if not key:
            break
        value = _safe_input(f"[{model_name}] 配置值: ")
        if value is None:
            print("该项配置已取消。\n")
            continue
        set_model_config(model_name, key, value)
        print(f"[{model_name}] 配置更新成功!\n")
control_panel = """Welcome for using CodeM!
1. start codem
2. view chats
3. settings
4. contact us"""


def _handle_configured_model() -> None:
    config_snapshot = _load_config()
    models = list_models()
    if not models:
        print("当前没有可用模型，请先创建模型再设置配置项。\n")
        return

    current = config_snapshot.get("configured_model")
    if current:
        print(f"当前配置模型: {current}")
    else:
        print("当前尚未设置配置模型。")

    print("可选模型:")
    for idx, name in enumerate(models, start=1):
        marker = "(当前)" if current == name else ""
        print(f" {idx}. {name} {marker}")

    choice = _safe_input("输入编号或名称（回车取消）: ")
    if choice is None or not choice.strip():
        print("已取消配置模型设置。\n")
        return
    choice = choice.strip()

    if choice.isdigit():
        index = int(choice)
        if 1 <= index <= len(models):
            name = models[index - 1]
        else:
            print("编号超出范围!\n")
            return
    else:
        name = choice

    try:
        set_configured_model(name)
        print(f"配置模型已更新为: {name}\n")
    except ValueError as exc:
        print(f"设置失败: {exc}\n")
        
        
def main():
    CURRENT_DIALOG_ = datetime.now().strftime("%m%d-%H%M")
    
    print(control_panel)
    agent = AgentCore()
    while True:
        ch = msvcrt.getwch()
        
        if ch == "1":
            while True:
                try: 
                    # userInput = _read_user_input()
                    userInput = input(">")
                    agent.set_input(userInput)
                    agent.run(CURRENT_DIALOG_)
                    
                # ctrl + C -> new conversation
                except KeyboardInterrupt:
                    agent.reset_conversation__()
                    print("A new chat started!")
                    CURRENT_DIALOG_ = datetime.now().strftime("%m%d-%H%M")
                
                except EOFError:
                    print("\nThanks for using CodeM!")
                    break
        
        elif ch == "2":
            history_dir = os.path.join(os.path.dirname(__file__), "history")
            os.makedirs(history_dir, exist_ok=True)
            
            files = os.listdir(history_dir)
            if len(files) == 0:
                print("no chat saved!")
                continue
            
            cnt = 0
            chat_cache = {}
            print("-" * 32)
            print("chats:")
            for filename in files:
                file_path = os.path.join(history_dir, filename)
                if os.path.isfile(file_path):     
                    name = os.path.splitext(filename)[0]   # 去掉 .json
                    cnt += 1
                    print(f"{cnt}. {name}")
                    chat_cache[cnt] = name
            print("-" * 32)
            switch_ = input("switch chat: ")
            if switch_.isdigit():
                if int(switch_) <= cnt:
                    agent.load_conv(chat_cache[int(switch_)] + ".json")
                    print(f"chat switched to {chat_cache[int(switch_)]}!")
                    CURRENT_DIALOG_ = chat_cache[int(switch_)]
                    continue
                
            print("invalid switch choice!")
            
        
        elif ch == "3":
            time.sleep(0.3)
            _handle_settings_menu()
        
        elif ch == "4":
            print("-" * 32)
            print("Github: https://github.com/scutll/TinyAgent")
            print("-" * 32)
        
        else:
            if ch == "\003" or ch == "\x1b" or ch == "\x1a":  # Ctrl+C\Ctrl+Z\ESC
                return
            
            handle_invalid_choice()
            
    
        

if __name__ == "__main__":
    main()
    
def handle_invalid_choice():
    print("not a valid choice!", end="", flush=True)
            
    start = time.time()
    while time.time() - start < 1:

        if msvcrt.kbhit():
            msvcrt.getwch() 
        
        time.sleep(0.01) 
    
    print("\r\033[2K", end="", flush=True)