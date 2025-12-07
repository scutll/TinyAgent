from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Optional

_LOG_FILE: Optional[Path] = None
_LOCK = Lock()
_PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _ensure_log_file() -> Path:
    global _LOG_FILE
    if _LOG_FILE is not None:
        return _LOG_FILE

    with _LOCK:
        if _LOG_FILE is None:
            logs_dir = _PACKAGE_ROOT / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            _LOG_FILE = logs_dir / f"agent_run_{timestamp}.log"
    return _LOG_FILE  # type: ignore[return-value]


def get_log_file_path() -> str:
    return str(_ensure_log_file())


def log(message: Any) -> None:
    if not isinstance(message, str):
        message = str(message)
    log_file = _ensure_log_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line)