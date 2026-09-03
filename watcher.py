"""Incremental error-log watcher. Failed callbacks do not consume events."""
from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class LogWatcher(FileSystemEventHandler):
    def __init__(self, log_file_path: str, callback: Callable[[str], None], *, max_bytes: int = 32_000) -> None:
        self.path = Path(log_file_path).resolve(); self.callback = callback; self.max_bytes = max_bytes
        self.path.touch(exist_ok=True); self._last_position = self.path.stat().st_size
    def on_modified(self, event: object) -> None:
        if not getattr(event, "is_directory", False) and Path(getattr(event, "src_path", "")).resolve() == self.path: self._check_for_new_errors()
    def _check_for_new_errors(self) -> None:
        if self.path.stat().st_size < self._last_position: self._last_position = 0
        with self.path.open("rb") as file:
            file.seek(self._last_position); data = file.read(self.max_bytes + 1); new_position = file.tell()
        text = data[:self.max_bytes].decode("utf-8", "replace")
        if "Exception" not in text and "Error:" not in text: self._last_position = new_position; return
        self.callback(text); self._last_position = new_position

def start_watching(log_path: str, on_error_callback: Callable[[str], None]) -> None:
    handler = LogWatcher(log_path, on_error_callback); observer = Observer(); observer.schedule(handler, str(handler.path.parent), recursive=False); observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()
