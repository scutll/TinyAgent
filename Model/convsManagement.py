# Management of conversations 
import torch
class Conversations:
    def __init__(self, vl_processor):
        self.conversations = dict() 
        self.vl_processor = vl_processor  
        self.conversations["default"] = self.vl_processor.new_chat_template()
        self.cur_conv = self.conversations["default"]

    def create_conversation(self, name=None):
        if name is None:
            name = len(self.conversations)
        if name in self.conversations:
            raise NameError(f"conversation {name} exists already!")
        conv = self.vl_processor.new_chat_template()
        self.conversations[name] = conv
        
        print(f"conversation {name} created")
        return name
    
    def list_conversations(self):
        return list(self.conversations.keys())
    
    def delete_conversation(self, name):
        if name not in self.conversations:
            raise NameError("no such conversation")
        del self.conversations[name]
    
    def switch_conversation(self, name):
        if name not in self.conversations:
            raise NameError("no such conversation")
        self.cur_conv = self.conversations[name]
        torch.cuda.empty_cache()
        print(f"conversation switched into {name}")
        
    def cur_conv_name(self):
        for k, v in self.conversations.items():
            if self.cur_conv is v:
                return k
        
