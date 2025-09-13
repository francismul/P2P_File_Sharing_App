import uuid

import socket
import threading
from decouple import config


port = config("CHAT_PORT", default=5002, cast=int)


class ChatManager:
    def __init__(self, chat_display, username=None, port=port):
        self.chat_display = chat_display
        self.username = username or self._get_local_ip()
        self.port = port
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._listen, daemon=True).start()

    def stop(self):
        self.running = False

    def send_message(self, msg):
        message = f"CHAT:{self.username}:{msg}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode(), ("<broadcast>", self.port))
        sock.close()

    def send_transfer_request(self, target_ip, filename, file_size, is_folder=False):
        request_id = str(uuid.uuid4())
        message = f"TRANSFER_REQUEST:{self.username}:{request_id}:{filename}:{file_size}:{is_folder}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (target_ip, self.port))
        sock.close()
        return request_id

    def send_transfer_response(self, target_ip, request_id, response):
        message = f"TRANSFER_RESPONSE:{self.username}:{request_id}:{response}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (target_ip, self.port))
        sock.close()

    def _listen(self):
        # Import moved here to avoid circular import
        from src.controller import chat_signal
        from src.controller import transfer_request_signal
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.port))
        while self.running:
            try:
                data, addr = sock.recvfrom(4096)
                decoded = data.decode(errors="ignore")
                if decoded.startswith("CHAT:"):
                    _, sender, message = decoded.split(":", 2)
                    chat_signal.message_received.emit(sender, message)
                elif decoded.startswith("TRANSFER_REQUEST:"):
                    _, sender, request_id, filename, file_size, is_folder = decoded.split(
                        ":", 5)
                    transfer_request_signal.transfer_request_received.emit(
                        addr[0], filename, file_size, request_id)
                elif decoded.startswith("TRANSFER_RESPONSE:"):
                    _, sender, request_id, response = decoded.split(":", 3)
                    transfer_request_signal.transfer_response_received.emit(
                        request_id, response)
            except Exception:
                pass

    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except:
            return "127.0.0.1"
        finally:
            s.close()
