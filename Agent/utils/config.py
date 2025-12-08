import json
from typing import Dict, Any, Optional
from Agent.utils.logging_ import log
from pathlib import Path
_CONFIG_CACHE: Optional[Dict[str, Any]] = None
CONFIG_FILE = "config.json"

def set_api_base(base_url: str):
    config = _load_config()
    config['base_url'] = base_url

    CONFIG_FILE = "config.json"

    package_root = Path(__file__).resolve().parents[1]
    config_path = package_root / CONFIG_FILE

    with config_path.open("w", encoding="utf-8") as fp:
        json.dump(config, fp, indent=4, ensure_ascii=False)
    
    log(f"config set base url: {base_url}")

def set_api_key(api_key: str):
    config = _load_config()
    config['api_key'] = api_key

    CONFIG_FILE = "config.json"

    package_root = Path(__file__).resolve().parents[1]
    config_path = package_root / CONFIG_FILE

    with config_path.open("w", encoding="utf-8") as fp:
        json.dump(config, fp, indent=4, ensure_ascii=False)
    
    log(f"config set base url: {api_key}")
    
def _init_config():
    
    package_root = Path(__file__).resolve().parents[1]
    config_path = package_root / CONFIG_FILE
    
    default_config = {
        "doubao_base_url": "https://ark.cn-beijing.volces.com/api/v3"
    }
    # 创建文件并写入默认配置（保证使用 utf-8）
    with config_path.open("w", encoding="utf-8") as fp:
        json.dump(default_config, fp, indent=4, ensure_ascii=False)



def _load_config() -> Dict[str, Any]:

    package_root = Path(__file__).resolve().parents[1]
    config_path = package_root / CONFIG_FILE

    if config_path.is_file():
        with config_path.open("r", encoding="utf-8") as fp:
            _CONFIG_CACHE = json.load(fp)
        log(f"[config] loaded {CONFIG_FILE} from {config_path}")
        return _CONFIG_CACHE

    # 若不存在则在 package_root 创建一个默认的 config.json 并返回默认配置
    _init_config()

    _CONFIG_CACHE = json.load(open(config_path, "r", encoding="utf-8"))
    log(f"[config] created default {CONFIG_FILE} at {config_path}")
    return _CONFIG_CACHE