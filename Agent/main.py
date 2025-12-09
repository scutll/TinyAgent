from datetime import datetime
import msvcrt
import os
import time
from Agent.Core.agent_core import AgentCore
from Agent.utils.input_style import _read_user_input
from Agent.utils.config import *
import argparse
control_panel = """Welcome for using CodeM!
1. start codem
2. view chats
3. settings
4. contact us"""

def main():
    CURRENT_DIALOG_ = datetime.now().strftime("%m%d-%H%M")
    
    print(control_panel)
    agent = AgentCore()
    while True:
        ch = msvcrt.getwch()
        
        if ch == "1":
            while True:
                try: 
                    userInput = _read_user_input()
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
                    continue
                
            print("invalid switch choice!")
            
        
        elif ch == "3":
            from Agent.utils.config import config_, _load_config
            CONFIG = _load_config()
            print("-" * 32)
            for k, v in CONFIG.items():
                print(f"{k}: {v}")
            print("-" * 32)
            
            try:
                time.sleep(0.5)
                input_ = input("进行设置吗: [y/n]: ")
            except KeyboardInterrupt or EOFError:
                continue
            
            if input_ != 'y':
                continue
            else:
                try:
                    key = input("config key: ")
                    value = input("config value: ")
                except KeyboardInterrupt or EOFError:
                    print("取消配置!")
                    continue
                config_(key, value) 
                print("配置修改成功!")
        
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