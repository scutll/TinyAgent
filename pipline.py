# a PIPLINE designed for DeepSeek model using transformers, which outputs tokens in a stream form
# Input: userInput + conv_name(create a new conv if None) + images(a list of pli_images(RGB mode)) + model_path
# images: DEFAULT a empty list denoting no image []
# tokenizer, processor, gpt using load_pretrained_model to load

# -*- coding: utf-8 -*-

import argparse
import os
import sys
from threading import Thread

import torch
from PIL import Image
from transformers import TextIteratorStreamer
from deepseek_vl.utils.io import load_pretrained_model

# open an image and convert it into RGB form
def load_image(image_file):
    image = Image.open(image_file).convert("RGB")
    return image


class pipline:
    def __init__(self,
                 args,
                 model_path="model/deepseek-1.3b/snapshots/model"):
        self.args = args
        self.model_path = model_path
        self.tokenizer, self.vl_processor, self.vl_gpt = load_pretrained_model(model_path=model_path)
        self.conversations = dict()
        self.gen_config = self.load_gen_config(self.tokenizer, self.vl_processor)
        
        
    def load_gen_config(self, tokenizer, vl_processor):
        config = dict(
            pad_token_id=vl_processor.tokenizer.eos_token_id,
            bos_token_id=vl_processor.tokenizer.bos_token_id,
            eos_token_id=vl_processor.tokenizer.eos_token_id,
            max_new_tokens=self.args.max_gen_len,
            use_cache=True,
        )
        if self.args.temperature > 0:
            config.update(
                {
                    "do_sample": True,
                    "top_p": self.args.top_p,
                    "temperature": self.args.temperature,
                    # 重复惩罚
                    "repetition_penalty": self.args.repetition_penalty,
                }
            )
        else:
            config.update({"do_sample": False})
            
        return config
    
    def __call__(self,userInput: str, conv_name=None, images=None, model_path="model/deepseek-1.3b/snapshots/model"):
        conv = None
        if images is None:
            images = []
        
        # 开启新对话并保存:
        if conv_name is None:
            conv_name = str(len(self.conversations))
            conv = self.vl_processor.new_chat_template()
            self.conversations[conv_name] = conv
        else:
            conv = self.conversations[conv_name]
            
        roles = conv.roles
        
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
        self.gen_config["inputs_embeds"] = inputs_embeds
        self.gen_config["attention_mask"] = prepare_inputs.attention_mask
        self.gen_config["streamer"] = streamer
        
        thread = Thread(target=self.vl_gpt.language_model.generate,
                        kwargs=self.gen_config)
        thread.start()
        
        # return in a stream
        yield from streamer
        

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
    parser.add_argument("--max_gen_len", type=int, default=10000000)
    args = parser.parse_args()
    
#  ==================test=======================
    answer = ""
    Pipline = pipline(args)
    answer_iter = Pipline("你好，你能帮我写一个计算斐波那契数列的C++程序吗")
    sys.stdout.write(f"Model: ")
    for char in answer_iter:
        answer += char
        sys.stdout.write(char)
        sys.stdout.flush()
        
    sys.stdout.write("\n")
    sys.stdout.flush()