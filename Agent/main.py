from Agent.Core.agent_core import AgentCore
from Agent.utils.input_style import _read_user_input




def main():
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