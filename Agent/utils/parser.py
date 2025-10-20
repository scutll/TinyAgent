import json
from typing import Tuple, Union
from Agent.utils.logging import log
def parse_response(response: str)->Tuple[str, str, str, dict]:
    try:
        ex_response = extract_JSON_block(response)            
        data = json.loads(ex_response)
        # check keys
        required_ = ["think", "response", "action", "action_input"]
        for required in required_:
            if required not in data.keys():
                raise KeyError(f"key {required} required but not in your answer!")
            
            
    except Exception as e:
        log(str(e))
        log("Error: failed to parse response=================\n" + response)
        return "", str(e) + "\n" + response, "ParseFailure", dict()

    return data["think"], data["response"], data["action"], data["action_input"]
    
    
# 应对偶尔错误的mdJSON格式，可以从中提取JSON内容而不用再让LLM再次生成
def extract_JSON_block(s: str) -> str:
    start = s.find("{")
    if start == -1:
        return ""
    
    i = start
    stack = []
    for j in range(i, len(s)):
        if s[j] == "{":
            stack.append(s[j])
        elif s[j] == "}":
            stack.pop()
            if not len(stack):
                return s[i: j+1]
    
    return ""
