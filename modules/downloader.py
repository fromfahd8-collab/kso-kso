import threading, yt_dlp
from PyQt6.QtCore import QObject, pyqtSignal

class DownloadWorker(QObject):
    progress = pyqtSignal(str, dict)
    finished = pyqtSignal(str)
    def __init__(self, url, opts, download_id): super().__init__(); self.url = url; self.opts = opts; self.download_id = download_id
    def progress_hook(self, d):
        if d['status'] == 'downloading': self.progress.emit(self.download_id, d)
        elif d['status'] == 'finished': self.finished.emit(self.download_id)
    def run(self): self.opts['progress_hooks'] = [self.progress_hook]; yt_dlp.YoutubeDL(self.opts).download([self.url])

class DownloadManager:
    def __init__(self): self.workers = {}
    def start_download(self, url, opts, download_id, callback_progress, callback_finished):
        worker = DownloadWorker(url, opts, download_id); worker.progress.connect(callback_progress); worker.finished.connect(callback_finished)
        thread = threading.Thread(target=worker.run, daemon=True); thread.start(); self.workers[download_id] = {"worker": worker, "thread": thread, "status": "running"}