import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    """ Restart application on code change. """
    def __init__(self, command):
        self.command = command
        self.start_process()

    def start_process(self):
        self.process = subprocess.Popen(self.command)

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f'File changed: {event.src_path}')
            self.restart_process()

    def restart_process(self):
        self.process.kill()
        self.process.wait()
        self.start_process()

def main():
    path = '.'  # The directory you want to watch
    command = [sys.executable, 'servo_control.py']  # Command to run your PyQt application

    event_handler = ChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print("Auto-reloading is now active...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.kill()
            event_handler.process.wait()

    observer.join()

if __name__ == "__main__":
    main()
