# the api to receive input and generate response, returning in stream
import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from llmApi.LLM.pipeline import pipeline
from llmApi.LLM.convsManagement import Conversations
from deepseek_vl.utils.io import load_pretrained_model
import json


# deploy the model ==============================================================
tokenizer, vl_processor, vl_gpt = load_pretrained_model("llmApi/model/deepseek-7b/model")

Convs = Conversations(vl_processor=vl_processor)

temperature = 0.2
top_p = 0.95
repetition_penalty = 1.1

generation_config = dict(
        pad_token_id=vl_processor.tokenizer.eos_token_id,
        bos_token_id=vl_processor.tokenizer.bos_token_id,
        eos_token_id=vl_processor.tokenizer.eos_token_id,
        max_new_tokens=2048,
        use_cache=True,
    )
if temperature > 0:
    generation_config.update(
        {
            "do_sample": True,
            "top_p": top_p,
            "temperature": temperature,
            # 重复惩罚
            "repetition_penalty": repetition_penalty,
        }
    )
else:
    generation_config.update({"do_sample": False})
    
LLM = pipeline(tokenizer=tokenizer,
               vl_processor=vl_processor,
               vl_gpt=vl_gpt,
               generation_config=generation_config)

Convs.create_conversation("chat1")
Convs.switch_conversation("chat1")
# =================================================================================


# the api

app = FastAPI()
@app.post("/agent/llm")
async def get_response(request: Request):
    body = await request.json()
    prompt = body.get("user_text", "")
    return StreamingResponse(LLM(prompt, images=None, conv=Convs.cur_conv))
