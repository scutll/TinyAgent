import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

_LOGGER: Optional[logging.Logger] = None
_LOG_FILE: Optional[Path] = None
_LOCK = Lock()


def _init_logger() -> logging.Logger:
    """Create a session-specific logger with second-level timestamped file name."""
    global _LOGGER, _LOG_FILE
    if _LOGGER is not None:
        return _LOGGER

    with _LOCK:
        if _LOGGER is not None:
            return _LOGGER

        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        _LOG_FILE = logs_dir / f"agent_run_{timestamp}.log"

        logger = logging.getLogger("TinyAgent")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

        file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.info("日志系统初始化完成，输出文件: %s", _LOG_FILE)
        _LOGGER = logger

    return _LOGGER


def get_log_file_path() -> str:
    """Return the absolute path of current log file."""
    _ = _init_logger()
    return str(_LOG_FILE) if _LOG_FILE else ""


def log(
    message: Any,
    level: str = "info",
    category: str = "system",
    **details: Any,
) -> None:
    """Centralized log interface supporting structured details."""
    logger = _init_logger()
    log_method = getattr(logger, level.lower(), logger.info)

    payload: Dict[str, Any] = {
        "category": category,
        "message": message,
    }
    if details:
        payload["details"] = details

    log_method(json.dumps(payload, ensure_ascii=False, default=str))