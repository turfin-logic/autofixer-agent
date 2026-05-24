import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogWatcher(FileSystemEventHandler):
    def __init__(self, log_file_path, callback):
        self.log_file_path = log_file_path
        self.callback = callback
        self._last_position = 0
        
        # Ensure file exists
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as f:
                f.write("")

    def on_modified(self, event):
        if event.src_path == self.log_file_path:
            self._check_for_new_errors()

    def _check_for_new_errors(self):
        with open(self.log_file_path, 'r') as file:
            file.seek(self._last_position)
            new_logs = file.read()
            self._last_position = file.tell()

            if "Exception" in new_logs or "Error:" in new_logs:
                print("🚨 [Watcher] CRASH DETECTED! Analyzing log...")
                self.callback(new_logs)

def start_watching(log_path, on_error_callback):
    event_handler = LogWatcher(log_path, on_error_callback)
    
    # Watch the directory containing the log file
    directory = os.path.dirname(log_path) or '.'
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    
    print(f"👀 [Watcher] Listening for crashes in '{log_path}'...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
