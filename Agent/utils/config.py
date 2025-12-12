import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from Agent.utils.logging_ import log

CONFIG_FILE = "config.json"
_CONFIG_CACHE: Optional[Dict[str, Any]] = None
_CONFIG_MTIME: Optional[float] = None


def _get_package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _get_config_path() -> Path:
    return _get_package_root() / CONFIG_FILE


def _default_config() -> Dict[str, Any]:
    return {
        "configured_model": "doubao",
        "channels": {
            "Doubao": "doubao",
            "structured": "doubao",
        },
        "models": {
            "doubao": {
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "model": "doubao-seed-1-6-thinking-250715",
                "api_key": "",
                "provider": "doubao"
            }
        }
    }


def _save_config(config: Dict[str, Any]) -> None:
    global _CONFIG_CACHE, _CONFIG_MTIME
    config_path = _get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with config_path.open("w", encoding="utf-8") as fp:
        json.dump(config, fp, indent=4, ensure_ascii=False)

    _CONFIG_CACHE = json.loads(json.dumps(config))  # 深拷贝缓存，避免外部修改
    try:
        _CONFIG_MTIME = config_path.stat().st_mtime
    except FileNotFoundError:
        _CONFIG_MTIME = None
    log(f"[config] saved {CONFIG_FILE} to {config_path}")


def _init_config() -> Dict[str, Any]:
    config = _default_config()
    _save_config(config)
    log(f"[config] created default {CONFIG_FILE} at {_get_config_path()}")
    return config


def _ensure_config_shape(config: Dict[str, Any]) -> Dict[str, Any]:
    if "models" not in config or not isinstance(config["models"], dict):
        config["models"] = {}
    if "configured_model" not in config:
        legacy = config.get("active_model")
        if isinstance(legacy, str) and legacy.strip():
            config["configured_model"] = legacy.strip()
        else:
            config.setdefault("configured_model", "")
        if "active_model" in config:
            del config["active_model"]
    return config


def _load_config(refresh: bool = False) -> Dict[str, Any]:
    global _CONFIG_CACHE, _CONFIG_MTIME

    config_path = _get_config_path()
    if not refresh and _CONFIG_CACHE is not None:
        current_mtime: Optional[float] = None
        if config_path.is_file():
            try:
                current_mtime = config_path.stat().st_mtime
            except FileNotFoundError:
                current_mtime = None
        if current_mtime is None and _CONFIG_MTIME is not None:
            refresh = True
        elif current_mtime is not None and (_CONFIG_MTIME is None or abs(current_mtime - _CONFIG_MTIME) > 1e-9):
            refresh = True
        if not refresh:
            return json.loads(json.dumps(_CONFIG_CACHE))

    if config_path.is_file():
        with config_path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        config = _ensure_config_shape(data)
        cache_copy = json.loads(json.dumps(config))
        _CONFIG_CACHE = cache_copy
        try:
            _CONFIG_MTIME = config_path.stat().st_mtime
        except FileNotFoundError:
            _CONFIG_MTIME = None
        if cache_copy != data:
            _save_config(config)
        log(f"[config] loaded {CONFIG_FILE} from {config_path}")
        return json.loads(json.dumps(cache_copy))

    return _init_config()


def get_configured_model(config: Optional[Dict[str, Any]] = None) -> str:
    data = config or _load_config()
    value = data.get("configured_model")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("configured_model 未设置，请在全局配置中选择一个模型")
    return value.strip()


def set_configured_model(model_name: str) -> Dict[str, Any]:
    if not model_name:
        raise ValueError("model_name 不能为空")
    config = _load_config()
    models = config.get("models", {})
    if model_name not in models:
        raise ValueError(f"模型 '{model_name}' 不存在，请先在 models 中创建")
    config["configured_model"] = model_name
    _save_config(config)
    log(f"config set configured_model: {model_name}")
    return config


def _coerce_value(value: Union[str, Any]) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _normalize_path(key: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(key, str):
        key = key.replace("[", ".").replace("]", "")
        parts = [segment.strip() for segment in key.split(".") if segment.strip()]
    else:
        parts = [str(segment).strip() for segment in key if str(segment).strip()]
    if not parts:
        raise ValueError("Key path cannot be empty")
    return parts


def _set_nested_value(target: Dict[str, Any], path: List[str], value: Any) -> None:
    current: Dict[str, Any] = target
    for segment in path[:-1]:
        next_node = current.get(segment)
        if not isinstance(next_node, dict):
            next_node = {}
            current[segment] = next_node
        current = next_node
    current[path[-1]] = value


def _delete_nested_key(target: Dict[str, Any], path: List[str]) -> None:
    current: Dict[str, Any] = target
    parents: List[Tuple[Dict[str, Any], str]] = []
    for segment in path[:-1]:
        next_node = current.get(segment)
        if not isinstance(next_node, dict):
            raise KeyError("/".join(path))
        parents.append((current, segment))
        current = next_node
    if path[-1] not in current:
        raise KeyError("/".join(path))
    del current[path[-1]]

    for parent, segment in reversed(parents):
        child = parent.get(segment)
        if isinstance(child, dict) and not child:
            del parent[segment]
        else:
            break


def config_(key: Union[str, Iterable[str]], value: Any) -> Dict[str, Any]:
    config = _load_config()
    path = _normalize_path(key)
    coerced = _coerce_value(value)
    _set_nested_value(config, path, coerced)
    _save_config(config)
    log(f"config set {'/'.join(path)}: {coerced}")
    return config


def delete_config(key: Union[str, Iterable[str]]) -> Dict[str, Any]:
    config = _load_config()
    path = _normalize_path(key)
    _delete_nested_key(config, path)
    _save_config(config)
    log(f"config delete {'/'.join(path)}")
    return config


def ensure_model(model_name: str) -> Dict[str, Any]:
    if not model_name:
        raise ValueError("model_name cannot be empty")
    config = _load_config()
    models = config.setdefault("models", {})
    model_config = models.setdefault(model_name, {})
    _save_config(config)
    log(f"config ensured model: {model_name}")
    return model_config


def set_model_config(model_name: str, key: Union[str, Iterable[str]], value: Any) -> Dict[str, Any]:
    if not model_name:
        raise ValueError("model_name cannot be empty")
    config = _load_config()
    models = config.setdefault("models", {})
    model_config = models.setdefault(model_name, {})
    path = _normalize_path(key)
    coerced = _coerce_value(value)
    _set_nested_value(model_config, path, coerced)
    _save_config(config)
    log(f"config set model {model_name} -> {'/'.join(path)}: {coerced}")
    return model_config


def list_models() -> List[str]:
    config = _load_config()
    return sorted(config.get("models", {}).keys())


def set_api_base(base_url: str) -> Dict[str, Any]:
    return config_("base_url", base_url)


def set_api_key(api_key: str) -> Dict[str, Any]:
    return config_("api_key", api_key)