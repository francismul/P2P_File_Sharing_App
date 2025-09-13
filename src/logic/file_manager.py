from PyQt5.QtCore import QObject, pyqtSignal
import threading
import time


class FileTransfer:
    def __init__(self, filename, peer_ip, size):
        self.filename = filename
        self.peer_ip = peer_ip
        self.size = size
        self.progress = 0
        self.status = "Queued"
        self.speed = ""
        self.paused = False
        self.cancelled = False
        self.lock = threading.Lock()
        self.last_update = time.time()
        self.last_progress = 0

    def update_progress(self, progress):
        with self.lock:
            now = time.time()
            delta_bytes = (progress - self.last_progress) / 100 * self.size
            delta_time = now - self.last_update
            if delta_time > 0:
                self.speed = f"{(delta_bytes / delta_time) / 1024:.2f} KB/s"
            self.last_update = now
            self.last_progress = progress

            self.progress = progress
            if progress >= 100:
                self.status = "Completed"
            elif not self.paused and not self.cancelled:
                self.status = "Downloading"


class FileManager(QObject):
    transfers_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.transfers = {}  # {(filename, peer_ip): FileTransfer}
        self.lock = threading.Lock()

    def add_transfer(self, filename, peer_ip, size):
        with self.lock:
            key = (filename, peer_ip)
            transfer = FileTransfer(filename, peer_ip, size)
            self.transfers[key] = transfer
            self.transfers_changed.emit()
            return transfer

    def get_active_transfers(self):
        with self.lock:
            return [t for t in self.transfers.values()
                    if t.status in ("Queued", "Downloading", "Paused") and not t.cancelled]

    def pause_transfer(self, filename, peer_ip):
        key = (filename, peer_ip)
        if key in self.transfers:
            t = self.transfers[key]
            t.paused = True
            t.status = "Paused"
            self.transfers_changed.emit()

    def resume_transfer(self, filename, peer_ip):
        key = (filename, peer_ip)
        if key in self.transfers:
            t = self.transfers[key]
            t.paused = False
            t.status = "Downloading"
            self.transfers_changed.emit()

    def cancel_transfer(self, filename, peer_ip):
        key = (filename, peer_ip)
        if key in self.transfers:
            t = self.transfers[key]
            t.cancelled = True
            t.status = "Cancelled"
            self.transfers_changed.emit()

    def update_progress(self, filename, peer_ip, progress):
        key = (filename, peer_ip)
        if key in self.transfers:
            self.transfers[key].update_progress(progress)
            self.transfers_changed.emit()

    def remove_completed(self):
        with self.lock:
            self.transfers = {k: t for k, t in self.transfers.items()
                              if t.status not in ("Completed", "Cancelled")}
            self.transfers_changed.emit()
