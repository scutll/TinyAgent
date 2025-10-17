import json
from typing import Tuple
def parse_response(response: str)->Tuple[str, str, str, dict]:
    try:
        data = json.loads(response)
    except Exception as e:
        print(e)
        print("Error: failed to parse response=================\n",
              response, 
              "========================================")
        return "", response, "ParseFailure", dict()

    return data["think"], data["response"], data["action"], data["action_input"]
    
    