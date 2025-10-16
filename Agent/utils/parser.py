import json
def parse_response(response: str):
    try:
        data = json.loads(response)
    except Exception as e:
        print(e)
        print("==============================\n", response, "==============================")
        
    return data["think"], data["response"], data["action"], data["action_input"]
    
    