import json
def parse_response(response: str):
    data = json.loads(response)
    return data["think"], data["response"], data["action"], data["action_input"]
    
    