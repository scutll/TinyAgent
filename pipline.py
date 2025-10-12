# a PIPELINE designed for DeepSeek model using transformers, which outputs tokens in a stream form
# Input: userInput images(a list of pli_images(RGB mode)) + model_path
# images: DEFAULT a empty list denoting no image []
# tokenizer, processor, gpt using load_pretrained_model to load
# for multi-conversations we employ interfaces to add/delete or switch into dirrerent conversations


# *** Response from this pipeline sometimes reflects a lot differently from the cli_chat from the official demo. whether it's some wrong in pipeline(generation_config/upload of latest message/any else) or just the model's fault is not very clear. 
# but we confirm that the conversation supports multi-rounds talks 

# -*- coding: utf-8 -*-
import json
import argparse
import os
import sys
from threading import Thread

from dataclasses import dataclass
import torch
from PIL import Image
from transformers import TextIteratorStreamer
from deepseek_vl.utils.io import load_pretrained_model




# open an image and convert it into RGB form
def load_image(image_file):
    image = Image.open(image_file).convert("RGB")
    return image

# to config the pipeline
@dataclass
class PipelineConfig:
    model_path: str = "model/deepseek-1.3b/snapshots/model"
    temperature: float = 0.2
    top_p: float = 0.95
    repetition_penalty: float = 1.1
    max_gen_len: int = 1024
    device: str = "cuda"
    


class pipeline:
    def __init__(self,
                 pcfg:PipelineConfig,
                 tokenizer,
                 vl_processor,
                 vl_gpt):
        self.pcfg = pcfg
        self.model_path = pcfg.model_path
        self.tokenizer, self.vl_processor, self.vl_gpt = tokenizer, vl_processor, vl_gpt
        self.gen_config = self.load_gen_config()

        
        
    def load_gen_config(self):
        config = dict(
            pad_token_id=self.vl_processor.tokenizer.eos_token_id,
            bos_token_id=self.vl_processor.tokenizer.bos_token_id,
            eos_token_id=self.vl_processor.tokenizer.eos_token_id,
            max_new_tokens=self.pcfg.max_gen_len,
            use_cache=True,
        )
        if self.pcfg.temperature > 0:
            config.update(
                {
                    "do_sample": True,
                    "top_p": self.pcfg.top_p,
                    "temperature": self.pcfg.temperature,
                    # 重复惩罚
                    "repetition_penalty": self.pcfg.repetition_penalty,
                } # type: ignore
            )
        else:
            config.update({"do_sample": False})
            
        return config
    
    
    # load input to get response
    @torch.inference_mode()
    def __call__(self,userInput: str, images, conv, model_path="model/deepseek-1.3b/snapshots/model"):
    
        if images is None:
            images = []
  
        # ==============图片处理==================
        if len(images) > 0:
            image_token = self.vl_processor.image_token
            userInput += image_token * len(images)
        
        
        conv.append_message(conv.roles[0], userInput)
        conv.append_message(conv.roles[1], None)
    
        
        prompt = conv.get_prompt()
        prepare_inputs = self.vl_processor.__call__(
            prompt=prompt, images=images, force_batchify=True
        ).to(self.vl_gpt.device)

        inputs_embeds = self.vl_gpt.prepare_inputs_embeds(**prepare_inputs)
        
        streamer = TextIteratorStreamer(
            tokenizer=self.tokenizer, skip_prompt=True, skip_special_tokens=True
        )
        
        gen_cfg = self.gen_config.copy()
        gen_cfg["inputs_embeds"] = inputs_embeds
        gen_cfg["attention_mask"] = prepare_inputs.attention_mask
        gen_cfg["streamer"] = streamer
            
        thread = Thread(target=self.vl_gpt.language_model.generate,
                            kwargs=gen_cfg)
        thread.start()
        
        answer = ""
        # return in a stream
        for char  in streamer:
            answer += char
            yield char
        conv.update_last_message(answer)
       


# Management of conversations 
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
        print(f"conversation switched into {name}")
        
    def cur_conv_name(self):
        for k, v in self.conversations.items():
            if self.cur_conv is v:
                return k
        


# =============test======================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_path",
        type=str,
        default="model/deepseek-1.3b/snapshots/model",
        help="the huggingface model name or the local path of the downloaded huggingface model.",
    )
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=0.95)
    parser.add_argument("--repetition_penalty", type=float, default=1.1)
    parser.add_argument("--max_gen_len", type=int, default=1024)
    args = parser.parse_args()
    
    tokenizer, vl_processor, vl_gpt = load_pretrained_model(model_path=args.model_path)
    
    
#  ==================test=======================
    answer = ""
    cfg = PipelineConfig(
        model_path=args.model_path,
        temperature=args.temperature,
        top_p=args.top_p,
        max_gen_len=args.max_gen_len,
        repetition_penalty=args.repetition_penalty
    )
    Pipeline = pipeline(cfg,
                        tokenizer=tokenizer,
                        vl_processor=vl_processor,
                        vl_gpt=vl_gpt)
    
    convs = Conversations(vl_processor)
    
    
    convs.create_conversation("chat1")
    convs.switch_conversation("chat1")
    
    answer_iter = Pipeline("给我讲讲模型蒸馏的原理", images=None, conv=convs.cur_conv)
    sys.stdout.write(f"({convs.cur_conv_name()})Model: ")
    for char in answer_iter:
        answer += char
        sys.stdout.write(char)
        sys.stdout.flush()
        
    sys.stdout.write("\n")
    sys.stdout.flush()

    answer_iter = Pipeline("模型蒸馏为什么可以降低参数量", images=None, conv=convs.cur_conv)
    sys.stdout.write(f"({convs.cur_conv_name()})Model: ")
    for char in answer_iter:
        answer += char
        sys.stdout.write(char)
        sys.stdout.flush()
        
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    
    answer_iter = Pipeline("为什么推理性能又不会降低很多", images=None, conv=convs.cur_conv)
    sys.stdout.write(f"({convs.cur_conv_name()})Model: ")
    for char in answer_iter:
        answer += char
        sys.stdout.write(char)
        sys.stdout.flush()
        
    sys.stdout.write("\n")
    sys.stdout.flush()