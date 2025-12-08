from Agent.Core.agent_core import AgentCore
from Agent.utils.input_style import _read_user_input
from Agent.utils.config import *
import argparse
parser = argparse.ArgumentParser(description="Run the CodeM Agent.")
parser.add_argument("--base_url", type=str, help="set the base url for llm, using doubao's base url in default")
parser.add_argument("--api_key", "-k", type=str, help="set the base url for llm, using doubao's base url in default")
args = parser.parse_args()

def main():

    if args.api_key:
        set_api_key(args.api_key)
    if args.base_url:
        set_api_base(args.base_url)
    if args.api_key or args.base_url:
        return
    
    
    agent = AgentCore()
    while True:
        try: 
            usertask = _read_user_input()
            agent.set_task(usertask)
            agent.run()
            
        # ctrl + C -> new conversation
        except KeyboardInterrupt:
            agent.reset_conversation__()
        
        except EOFError:
            print("\nThanks for using CodeM!")
            break
        

if __name__ == "__main__":
    main()