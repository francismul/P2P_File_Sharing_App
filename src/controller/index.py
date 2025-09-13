import os
import logging

# from src.network.chat import ChatManager  # Moved to __init__ to avoid circular import
from src.logic import FileManager
from src.controller import peer_signal
from src.controller import transfer_request_signal

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("src/logs/app.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ShareSync")


class AppLogic:
    def __init__(self, chat_display=None, username=None):
        # Lazy import to avoid circular dependency
        from src.logic import NetworkManager
        from src.logic import ChatManager

        logger.info("Initializing AppLogic")

        self.network_manager = NetworkManager()
        self.chat_manager = ChatManager(
            chat_display, username=username or self.network_manager._get_local_ip())
        self.file_manager = FileManager()
        self.network_manager.start()
        self.chat_manager.start()
        self.pending_transfers = {}
        transfer_request_signal.transfer_response_received.connect(
            self.handle_transfer_response)
        logger.info("Network and Chat managers started")

    def get_peers(self):
        peers = self.network_manager.get_peers()
        logger.info(f"Fetched peers: {peers}")
        return peers

    def send_file(self, peer_ip, file_path):
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                self.file_manager.add_transfer(file_path, peer_ip, size)
                logger.info(f"Sending file '{file_path}' to {peer_ip}")
                self.network_manager.send_file(peer_ip, file_path)
                return True
            else:
                logger.error(f"File {file_path} does not exist.")
                return False
        except Exception as e:
            logger.error(f"Sending file {file_path} to {peer_ip}: {e}")
            return False

    def receive_file(self):
        # Receiving is handled automatically by NetworkManager
        logger.info("Receive file called (handled automatically)")
        pass

    def stop(self):
        logger.info("Stopping network manager")
        self.network_manager.stop()

    def send_chat_message(self, msg):
        logger.info(f"Sending chat message: {msg}")
        self.chat_manager.send_message(msg)

    def receive_chat_message(self):
        # Receiving is handled automatically by ChatManager
        logger.info("Receive chat message called (handled automatically)")
        pass

    def get_lan_status(self):
        status = self.network_manager.get_lan_status()
        logger.info(f"LAN status: {status}")
        return status

    # File transfer management
    def get_active_transfers(self):
        transfers = self.file_manager.get_active_transfers()
        logger.info(
            f"Active transfers: {[(t.filename, t.peer_ip, t.status) for t in transfers]}")
        return transfers

    def pause_transfer(self, filename, peer_ip):
        logger.info(f"Pausing transfer: {filename} to {peer_ip}")
        self.file_manager.pause_transfer(filename, peer_ip)

    def resume_transfer(self, filename, peer_ip):
        logger.info(f"Resuming transfer: {filename} to {peer_ip}")
        self.file_manager.resume_transfer(filename, peer_ip)

    def cancel_transfer(self, filename, peer_ip):
        logger.info(f"Cancelling transfer: {filename} to {peer_ip}")
        self.file_manager.cancel_transfer(filename, peer_ip)

    def update_transfer_progress(self, filename, peer_ip, progress):
        logger.info(
            f"Updating progress for {filename} to {peer_ip}: {progress}%")
        self.file_manager.update_progress(filename, peer_ip, progress)

    def remove_completed_transfers(self):
        logger.info("Removing completed/cancelled transfers")
        self.file_manager.remove_completed()

    # Transfer request management
    def send_transfer_request(self, peer_ip, file_path):
        try:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                is_folder = os.path.isdir(file_path)
                filename = os.path.basename(file_path)
                request_id = self.chat_manager.send_transfer_request(
                    peer_ip, filename, str(file_size), is_folder)
                if request_id:
                    self.pending_transfers[request_id] = (peer_ip, file_path)
                logger.info(
                    f"Sent transfer request for {filename} to {peer_ip}")
                return request_id
            else:
                logger.error(f"File/folder {file_path} does not exist.")
                return None
        except Exception as e:
            logger.error(
                f"Sending transfer request for {file_path} to {peer_ip}: {e}")
            return None

    def respond_to_transfer_request(self, peer_ip, request_id, response):
        try:
            self.chat_manager.send_transfer_response(
                peer_ip, request_id, response)
            logger.info(
                f"Sent {response} response for request {request_id} to {peer_ip}")
        except Exception as e:
            logger.error(f"Sending transfer response to {peer_ip}: {e}")

    def handle_transfer_response(self, request_id, response):
        if request_id in self.pending_transfers:
            peer_ip, file_path = self.pending_transfers[request_id]
            if response == "accept":
                logger.info(
                    f"Transfer accepted by {peer_ip}, starting transfer of {file_path}")
                self.start_file_transfer(peer_ip, file_path)
            else:
                logger.info(f"Transfer declined by {peer_ip}")
            del self.pending_transfers[request_id]
        else:
            logger.warning(
                f"Received response for unknown request ID: {request_id}")

    def start_file_transfer(self, peer_ip, file_path):
        """Start sending a file to a peer"""
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                self.file_manager.add_transfer(file_path, peer_ip, size)
                logger.info(
                    f"Starting file transfer: {file_path} to {peer_ip}")
                self.network_manager.send_file(peer_ip, file_path)
                return True
            else:
                logger.error(f"File {file_path} does not exist.")
                return False
        except Exception as e:
            logger.error(
                f"Starting file transfer {file_path} to {peer_ip}: {e}")
            return False

    def add_peer(self, peer):
        self.network_manager.add_peer(peer)
        peer_signal.peers_changed.emit()

    def remove_peer(self, peer):
        self.network_manager.remove_peer(peer)
        peer_signal.peers_changed.emit()

    def update_network(self):
        # Call this when network state changes
        peer_signal.peers_changed.emit()

    def __del__(self):
        logger.info("AppLogic instance deleted, stopping network manager")
        self.stop()
