import subprocess
import threading
import queue
import time
import sys
import os
from typing import Optional


class TerminalSession:
    """
    长生命周期终端 Session
    Agent 通过 send(command) 与 shell 交互
    """

    def __init__(
        self,
        shell: str = "powershell",
        echo: bool = False,
        quiet_time: float = 5.0,
        max_wait: float = 30.0,
        poll_interval: float = 0.05,
    ):
        self.shell = shell
        self.echo = echo

        # Default wait settings; can be overridden per call in send().
        self.quiet_time = quiet_time
        self.max_wait = max_wait
        self.poll_interval = poll_interval

        self.process = None
        self._lock = threading.Lock()

        self._stdout_queue = queue.Queue()
        self._stderr_queue = queue.Queue()

        self._stdout_thread = None
        self._stderr_thread = None

        self.start()

    # ---------------------------
    # lifecycle
    # ---------------------------

    def start(self):
        """启动 shell 进程"""
        if self.process and self.is_alive():
            return

        if self.shell == "powershell":
            cmd = [
                "powershell",
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
            ]
        elif self.shell == "cmd":
            cmd = ["cmd.exe"]
        else:
            raise ValueError(f"Unsupported shell: {self.shell}")

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=os.getcwd(),
        )

        self._stdout_queue = queue.Queue()
        self._stderr_queue = queue.Queue()

        self._stdout_thread = threading.Thread(
            target=self._reader,
            args=(self.process.stdout, self._stdout_queue),
            daemon=True,
        )
        self._stderr_thread = threading.Thread(
            target=self._reader,
            args=(self.process.stderr, self._stderr_queue),
            daemon=True,
        )

        self._stdout_thread.start()
        self._stderr_thread.start()

    def restart(self):
        """重启 shell"""
        self.stop()
        self.start()

    def stop(self):
        """终止 shell"""
        try:
            if self.process:
                self.process.kill()
        except Exception:
            pass
        self.process = None

    # 为了兼容 SessionManager.close()，提供 close() 别名
    def close(self):
        self.stop()

    def is_alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    # ---------------------------
    # io
    # ---------------------------

    def write(self, data: str):
        if not self.is_alive():
            raise RuntimeError("Terminal process is not alive")

        if self.echo:
            sys.stdout.write(data)
            sys.stdout.flush()

        self.process.stdin.write(data)
        self.process.stdin.flush()

    def send(
        self,
        command: str,
        *,
        quiet_time: Optional[float] = None,
        max_wait: Optional[float] = None,
        poll_interval: Optional[float] = None,
        append_newline: bool = True,
    ) -> dict:
        """写入命令并阻塞等待输出稳定

        等待策略：
        - 首次输出前：最多等待 max_wait，期间不受 quiet_time 约束（避免未产生首个输出时过早返回）。
        - 首次输出后：持续收集，直到连续 quiet_time 秒没有新输出或整体超时 max_wait。
        """

        with self._lock:
            if not self.is_alive():
                self.restart()

            # 使用 per-call 配置覆盖实例默认配置。
            quiet_time = self.quiet_time if quiet_time is None else quiet_time
            max_wait = self.max_wait if max_wait is None else max_wait
            poll_interval = self.poll_interval if poll_interval is None else poll_interval

            if append_newline:
                self.write(command)
                self.write("\n")
            else:
                self.write(command)

            stdout_chunks = []
            stderr_chunks = []

            start_time = time.time()
            last_output_time = start_time
            first_output_seen = False

            while True:
                got_output = False

                # stdout
                try:
                    while True:
                        out = self._stdout_queue.get_nowait()
                        stdout_chunks.append(out)
                        last_output_time = time.time()
                        got_output = True
                        first_output_seen = True
                except queue.Empty:
                    pass

                # stderr
                try:
                    while True:
                        err = self._stderr_queue.get_nowait()
                        stderr_chunks.append(err)
                        last_output_time = time.time()
                        got_output = True
                        first_output_seen = True
                except queue.Empty:
                    pass

                now = time.time()

                # 全局超时保护
                if now - start_time >= max_wait:
                    print(f"[DEBUG] send timeout: waited {now - start_time:.1f}s for command: {command}")
                    break

                # 首次输出前：继续等待直到超时
                if not first_output_seen:
                    time.sleep(poll_interval)
                    continue

                # 首次输出后：静默窗口判断
                if not got_output and (now - last_output_time) >= quiet_time:
                    break

                time.sleep(poll_interval)

            return {
                "stdout": "".join(stdout_chunks),
                "stderr": "".join(stderr_chunks),
            }

    # ---------------------------
    # internal
    # ---------------------------

    @staticmethod
    def _reader(pipe, q: queue.Queue):
        """后台 reader 线程"""
        try:
            for line in iter(pipe.readline, ""):
                q.put(line)
        except Exception:
            pass
