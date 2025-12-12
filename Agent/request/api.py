from openai import OpenAI
from pydantic import BaseModel, Field
from volcenginesdkarkruntime import Ark
from Agent.utils.logging_ import log
from Agent.utils.config import _load_config
from Agent.Memory.container import MemoryContainer
from typing import Any, Dict, Iterable, Optional, Tuple, Union


def _normalize_models(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    models = config.get("models", {})
    if isinstance(models, dict):
        return {str(name): value for name, value in models.items() if isinstance(value, dict)}
    return {}


def _match_model_entry(models: Dict[str, Dict[str, Any]], name: Optional[str]) -> Optional[Tuple[str, Dict[str, Any]]]:
    if not isinstance(name, str) or not name:
        return None
    name_lower = name.lower()
    for candidate, cfg in models.items():
        if candidate.lower() == name_lower:
            return candidate, cfg
    return None


def _first_non_empty(*values: Optional[str]) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _runtime_settings() -> Dict[str, Any]:
    config = _load_config()
    models = _normalize_models(config)
    configured_model = config.get("configured_model")
    sanitized: Dict[str, Dict[str, Any]] = {}
    for name, raw_cfg in models.items():
        base = raw_cfg if isinstance(raw_cfg, dict) else {}
        merged = {
            "name": name,
            "api_key": _first_non_empty(
                base.get("api_key"),
                config.get("api_key"),
                config.get("doubao_api_key"),
            ),
            "base_url": _first_non_empty(
                base.get("base_url"),
                config.get("base_url"),
                config.get("doubao_base_url"),
            ),
            "model": base.get("model"),
            "provider": base.get("provider") or base.get("client") or base.get("type"),
            "raw": base,
        }
        sanitized[name] = merged

    return {
        "config": config,
        "models": sanitized,
    "configured_model": configured_model,
    }


def _resolve_model(runtime: Dict[str, Any], channel: str) -> Dict[str, Any]:
    models: Dict[str, Dict[str, Any]] = runtime.get("models", {})
    config: Dict[str, Any] = runtime.get("config", {})
    configured_model: Optional[str] = runtime.get("configured_model")

    if not models:
        raise ValueError("No models configured in config.json")

    channel_key = channel.lower()
    if channel_key == "structured":
        candidate_names: Iterable[Optional[str]] = ["doubao"]
    else:
        candidate_names = []
        mapping = config.get("channels")
        if isinstance(mapping, dict):
            for key, value in mapping.items():
                if isinstance(key, str) and key.lower() == channel_key:
                    candidate_names = [value]
                    break

        if not isinstance(candidate_names, Iterable) or candidate_names == []:
            candidate_names = [channel]

    for candidate in candidate_names:
        matched = _match_model_entry(models, candidate)
        if matched:
            name, entry = matched
            prepared = {
                "name": name,
                "api_key": entry.get("api_key", ""),
                "base_url": entry.get("base_url", ""),
                "model": entry.get("model", ""),
                "provider": entry.get("provider"),
                "raw": entry.get("raw", {}),
            }
            if not prepared["model"]:
                raise ValueError(f"Model '{name}' must define a 'model' field in config.json")
            return prepared

    if configured_model:
        matched = _match_model_entry(models, configured_model)
        if matched:
            name, entry = matched
            prepared = {
                "name": name,
                "api_key": entry.get("api_key", ""),
                "base_url": entry.get("base_url", ""),
                "model": entry.get("model", ""),
                "provider": entry.get("provider"),
                "raw": entry.get("raw", {}),
            }
            if not prepared["model"]:
                raise ValueError(f"configured_model '{name}' 未设置 model 字段")
            return prepared

    if configured_model:
        raise ValueError(f"configured_model '{configured_model}' 在 models 中不存在，请检查配置")

    if len(models) == 1:
        entry = next(iter(models.values()))
        prepared = {
            "name": entry.get("name", next(iter(models.keys()))),
            "api_key": entry.get("api_key", ""),
            "base_url": entry.get("base_url", ""),
            "model": entry.get("model", ""),
            "provider": entry.get("provider"),
            "raw": entry.get("raw", {}),
        }
        if not prepared["model"]:
            raise ValueError("Configured model entry must include a 'model' field")
        return prepared

    if channel_key == "structured":
        raise ValueError("structured 响应仅支持 Doubao，请在 config.json 的 models 中配置 'doubao' 模型")

    raise ValueError(f"无法根据 channel '{channel}' 在 config.json 中找到匹配的模型配置，请检查配置文件。")
CURRENT_DIALOG_ = ""
def set_dialog(dialog:str):
    global CURRENT_DIALOG_
    CURRENT_DIALOG_ = dialog


# 从配置文件读取API配置
def get_response_from_Doubao(input: Union[list, str], Memory: MemoryContainer, Model: Optional[str] = None):
    """
    supporting models:\n
    \t"doubao-seed-1-6-thinking-250715",
    \t"doubao-seed-1-6-flash-250615"
    """
    # 带图片的文本以List形式的参数给到input
    Memory._add_user_message(input)
    global CURRENT_DIALOG_
    Memory._save_conversation(CURRENT_DIALOG_)
    
    runtime = _runtime_settings()
    doubao_settings = _resolve_model(runtime, "Doubao")
    model_name = Model or doubao_settings["model"]
    client = Ark(
        api_key=doubao_settings["api_key"],
        base_url=doubao_settings["base_url"]
    )
    log(f"[LLM request][{model_name}]\n{input[:100]}...")
    completion = client.chat.completions.create(
        model=model_name,
        messages=Memory(),
        stream=False,
    )
    result = str(completion.choices[0].message.content) # type: ignore
    log(f"[LLM response][{model_name}]\n{result}")
    if result:
        Memory._add_assistant_message(str(result))
        Memory._save_conversation(CURRENT_DIALOG_)
    else:
        Memory._pop_message() 

    log("======================================")
    return result if result is not None else "Failed to generate response!"


def get_response_from_gpt(input: Union[list, str], Memory: MemoryContainer, Model: Optional[str] = None):
    Memory._add_user_message(input)
    global CURRENT_DIALOG_
    Memory._save_conversation(CURRENT_DIALOG_)
    
    runtime = _runtime_settings()
    gpt_settings = _resolve_model(runtime, "gpt")
    model_name = Model or gpt_settings["model"]
    client = OpenAI(
        api_key=gpt_settings["api_key"],
        base_url=gpt_settings["base_url"] or None,
    )
    log(f"[LLM request][{model_name}]\n{input[:100]}...")
    completion = client.chat.completions.create(
        model=model_name,
        messages=Memory(),
        stream=False,
    )
    result = str(completion.choices[0].message.content) # type: ignore
    log(f"[LLM response][{model_name}]\n{result}")
    if result:
        Memory._add_assistant_message(str(result))
        Memory._save_conversation(CURRENT_DIALOG_)
    else:
        Memory._pop_message()  

    log("======================================")
    return result if result is not None else "Failed to generate response!"

class agentOutputFields(BaseModel):
    observation: str = Field(description="简单描述上一轮系统提供的信息，首轮为用户输入的摘要。")
    think: str = Field(description="你的内部思考过程, 包括对observation的分析和下一步应该如何做")
    response: str = Field( description="给用户的可见回答，简要说明情况或回答问题。或Finish操作的回应内容")
    action: str = Field(description="本轮要执行的工具名称，或 'Finish'。")
    action_input: Dict[str, Any] = Field(default_factory=dict, description="传给工具的参数字典, 具体格式应该参照tools prompt")
    
    

def structured_response(input: Union[list, str], Memory: MemoryContainer, Model: Optional[str] = None):
    Memory._add_user_message(input)
    global CURRENT_DIALOG_
    Memory._save_conversation(CURRENT_DIALOG_)
    runtime = _runtime_settings()
    doubao_settings = _resolve_model(runtime, "structured")
    model_name = Model or doubao_settings["model"]
    log(f"[structured request][{model_name}]\n{input}")
    client = OpenAI(
        base_url=doubao_settings["base_url"],
        api_key=doubao_settings["api_key"],
        max_retries=3,
    ) 
    response = client.responses.parse(
        model=model_name, 
        input=Memory(),
        text_format=agentOutputFields
    )
    
    result = response.output_parsed
    log(f"[structured response][{model_name}]\n{result}")
    if result:
        Memory._add_assistant_message(str(result))
        Memory._save_conversation(CURRENT_DIALOG_)
    else:
        # 这个情况下save以后暂时没法删除，除非下次保存覆盖，待完善
        Memory._pop_message()
    
    return result if result is not None else "Failed to generate response!"

api = {
    "Doubao": get_response_from_Doubao,
    "gpt": get_response_from_gpt,
    "structured": structured_response
}