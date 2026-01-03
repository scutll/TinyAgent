import threading
from typing import Optional

from Agent.utils.terminal.session import TerminalSession


class TerminalSessionManager:
    """
    Session 管理器：
    - 多 Session 管理
    - 自动创建
    - 重启 / 关闭
    """

    def __init__(self):
        self.sessions = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> TerminalSession:
        """获取 Session，不存在则创建"""
        with self._lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = TerminalSession()
            return self.sessions[session_id]

    # ---------------------------
    # high-level io helpers
    # ---------------------------

    def send_command(
        self,
        session_id: str,
        command: str,
        *,
        quiet_time: Optional[float] = None,
        max_wait: Optional[float] = None,
        poll_interval: Optional[float] = None,
        append_newline: bool = True,
    ) -> dict:
        """向指定 Session 写入命令并阻塞收集输出"""
        session = self.get(session_id)
        return session.send(
            command,
            quiet_time=quiet_time,
            max_wait=max_wait,
            poll_interval=poll_interval,
            append_newline=append_newline,
        )

    def restart(self, session_id: str):
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].restart()

    def close(self, session_id: str):
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].close()
                del self.sessions[session_id]

    def close_all(self):
        with self._lock:
            for s in self.sessions.values():
                s.close()
            self.sessions.clear()
