import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = subprocess.Popen(["python", self.script])

    def on_modified(self, event):
        if event.src_path.endswith("py"):
            self.process.kill()
            self.process = subprocess.Popen(["python", self.script])


observer = Observer()
handler = ReloadHandler("main.py")
observer.schedule(handler, ".", recursive=False)
observer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()
    handler.process.kill()
observer.join()
