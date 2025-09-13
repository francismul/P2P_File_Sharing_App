import socket
import threading
import os
import time
import struct
from decouple import config
from concurrent.futures import ThreadPoolExecutor
import zipfile
import tempfile


port = config("P2P_PORT", default=5001, cast=int)
broadcast_port = config("P2P_BROADCAST_PORT", default=5002, cast=int)


class NetworkManager:
    def __init__(self, port=port, broadcast_port=broadcast_port, max_workers=10):
        self.port = port
        self.broadcast_port = broadcast_port
        self.peers = set()
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._udp_sock = None  # Store UDP socket for cleanup
        self._server_sock = None  # Store TCP server socket for cleanup
        self._download_bytes = 0
        self._upload_bytes = 0
        self._last_bandwidth_emit = time.time()
        self._bandwidth_interval = 1.0  # seconds
        self.peer_update_callback = None  # Callback for peer updates
        threading.Thread(target=self._bandwidth_monitor, daemon=True).start()

    def start(self):
        self.running = True
        threading.Thread(target=self._discover_peers, daemon=True).start()
        threading.Thread(target=self._start_server, daemon=True).start()

    def stop(self):
        self.running = False
        self.executor.shutdown(wait=False)
        if self._udp_sock:
            try:
                self._udp_sock.close()
            except Exception:
                pass
            self._udp_sock = None
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
            self._server_sock = None

    # -------------------- Peer Discovery --------------------
    def _discover_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", self.broadcast_port))
        self._udp_sock = sock

        def broadcast():
            while self.running:
                try:
                    sock.sendto(b"PEER_DISCOVERY",
                                ("<broadcast>", self.broadcast_port))
                    time.sleep(3)
                except Exception:
                    pass

        threading.Thread(target=broadcast, daemon=True).start()

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                if data == b"PEER_DISCOVERY" and addr[0] != self._get_local_ip():
                    if addr[0] not in self.peers:
                        self.peers.add(addr[0])
                        if self.peer_update_callback:
                            self.peer_update_callback()
            except Exception:
                pass
        try:
            sock.close()
        except Exception:
            pass
        self._udp_sock = None

    # -------------------- Server --------------------
    def _start_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("", self.port))
        server_sock.listen(20)
        self._server_sock = server_sock

        while self.running:
            try:
                conn, addr = server_sock.accept()
                self.executor.submit(self._handle_client, conn, addr)
            except Exception:
                pass

    def _handle_client(self, conn, addr):
        try:
            header = conn.recv(8)
            if not header:
                return
            name_len, file_size = struct.unpack("!II", header)

            filename = conn.recv(name_len).decode()

            # Receive file
            temp_filename = filename + '.temp'
            with open(temp_filename, "wb") as f:
                remaining = file_size
                while remaining > 0:
                    chunk = conn.recv(min(65536, remaining))
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)
                    self._download_bytes += len(chunk)

            # Check if it's a zip file (directory)
            if filename.endswith('.zip') and zipfile.is_zipfile(temp_filename):
                # Extract directory
                extract_dir = filename[:-4]  # Remove .zip extension
                os.makedirs(extract_dir, exist_ok=True)
                with zipfile.ZipFile(temp_filename, 'r') as zipf:
                    zipf.extractall(extract_dir)
                os.unlink(temp_filename)
                print(f"[OK] Received and extracted directory: {extract_dir} from {addr}")
            else:
                # Regular file
                os.rename(temp_filename, filename)
                print(f"[OK] Received file: {filename} from {addr}")

        except Exception as e:
            print(f"[ERROR] Failed receiving from {addr}: {e}")
            # Clean up temp file if it exists
            try:
                if 'temp_filename' in locals():
                    os.unlink(temp_filename)
            except:
                pass
        finally:
            conn.close()

    # -------------------- Sending --------------------
    def send_file(self, peer_ip, filepath):
        try:
            if os.path.isdir(filepath):
                # Handle directory: create a zip file
                dir_name = os.path.basename(filepath)
                temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
                temp_zip.close()

                with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(filepath):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(filepath))
                            zipf.write(file_path, arcname)

                filename = temp_zip.name
                display_name = dir_name + '.zip'
                file_size = os.path.getsize(filename)
                cleanup_zip = True
            else:
                filename = filepath
                display_name = os.path.basename(filename)
                file_size = os.path.getsize(filename)
                cleanup_zip = False

            name_bytes = display_name.encode()
            name_len = len(name_bytes)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, self.port))

            sock.send(struct.pack("!II", name_len, file_size))
            sock.send(name_bytes)

            with open(filename, "rb") as f:
                while True:
                    data = f.read(65536)
                    if not data:
                        break
                    sock.sendall(data)
                    self._upload_bytes += len(data)

            sock.close()

            if cleanup_zip:
                os.unlink(filename)

            print(f"[OK] Sent {display_name} → {peer_ip}")
        except Exception as e:
            print(f"[ERROR] Sending to {peer_ip}: {e}")

    def get_peers(self):
        return list(self.peers)

    def get_lan_status(self):
        local_ip = self._get_local_ip()
        if local_ip and not local_ip.startswith("127."):
            return True, local_ip
        return False, local_ip

    # -------------------- Utils --------------------
    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def add_peer(self, peer_ip):
        self.peers.add(peer_ip)

    def remove_peer(self, peer_ip):
        self.peers.discard(peer_ip)

    def _bandwidth_monitor(self):
        from src.controller import bandwidth_signal
        while True:
            time.sleep(self._bandwidth_interval)
            now = time.time()
            interval = now - self._last_bandwidth_emit
            if interval > 0:
                download_rate = self._download_bytes / \
                    (1024 * 1024) / interval  # MB/s
                upload_rate = self._upload_bytes / \
                    (1024 * 1024) / interval  # MB/s
                bandwidth_signal.bandwidth_changed.emit(
                    download_rate, upload_rate)
                self._download_bytes = 0
                self._upload_bytes = 0
                self._last_bandwidth_emit = now
