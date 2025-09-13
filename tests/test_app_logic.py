# type: ignore

import unittest
import os
import tempfile
from unittest.mock import Mock, patch
from src.controller.index import AppLogic


class TestAppLogic(unittest.TestCase):
    def setUp(self):
        # Mock the managers to avoid actual network operations
        with patch('src.logic.NetworkManager'), \
                patch('src.logic.ChatManager'), \
                patch('src.logic.FileManager'):
            self.app_logic = AppLogic()

            # Mock the manager methods
            self.app_logic.network_manager = Mock()
            self.app_logic.chat_manager = Mock()
            self.app_logic.file_manager = Mock()

    def test_initialization(self):
        """Test that AppLogic initializes with all managers"""
        self.assertIsNotNone(self.app_logic.network_manager)
        self.assertIsNotNone(self.app_logic.chat_manager)
        self.assertIsNotNone(self.app_logic.file_manager)
        self.assertEqual(self.app_logic.pending_transfers, {})

    def test_get_peers(self):
        """Test getting peers from network manager"""
        mock_peers = ["192.168.1.100", "192.168.1.101"]
        self.app_logic.network_manager.get_peers.return_value = mock_peers

        peers = self.app_logic.get_peers()
        self.assertEqual(peers, mock_peers)
        self.app_logic.network_manager.get_peers.assert_called_once()

    def test_send_file_success(self):
        """Test successful file sending"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name

        try:
            self.app_logic.network_manager.send_file.return_value = True
            result = self.app_logic.send_file("192.168.1.100", temp_path)
            self.assertTrue(result)
            self.app_logic.network_manager.send_file.assert_called_once_with(
                "192.168.1.100", temp_path)
        finally:
            os.unlink(temp_path)

    def test_send_file_nonexistent(self):
        """Test sending nonexistent file"""
        result = self.app_logic.send_file(
            "192.168.1.100", "/nonexistent/file.txt")
        self.assertFalse(result)

    def test_send_chat_message(self):
        """Test sending chat message"""
        message = "Hello, world!"
        self.app_logic.send_chat_message(message)
        self.app_logic.chat_manager.send_message.assert_called_once_with(
            message)

    def test_get_lan_status(self):
        """Test getting LAN status"""
        mock_status = (True, "192.168.1.100")
        self.app_logic.network_manager.get_lan_status.return_value = mock_status

        status = self.app_logic.get_lan_status()
        self.assertEqual(status, mock_status)
        self.app_logic.network_manager.get_lan_status.assert_called_once()

    def test_get_active_transfers(self):
        """Test getting active transfers"""
        mock_transfers = [
            Mock(filename="test.txt", peer_ip="192.168.1.100", status="active")]
        self.app_logic.file_manager.get_active_transfers.return_value = mock_transfers

        transfers = self.app_logic.get_active_transfers()
        self.assertEqual(transfers, mock_transfers)
        self.app_logic.file_manager.get_active_transfers.assert_called_once()

    def test_pause_transfer(self):
        """Test pausing a transfer"""
        filename = "test.txt"
        peer_ip = "192.168.1.100"

        self.app_logic.pause_transfer(filename, peer_ip)
        self.app_logic.file_manager.pause_transfer.assert_called_once_with(
            filename, peer_ip)

    def test_resume_transfer(self):
        """Test resuming a transfer"""
        filename = "test.txt"
        peer_ip = "192.168.1.100"

        self.app_logic.resume_transfer(filename, peer_ip)
        self.app_logic.file_manager.resume_transfer.assert_called_once_with(
            filename, peer_ip)

    def test_cancel_transfer(self):
        """Test cancelling a transfer"""
        filename = "test.txt"
        peer_ip = "192.168.1.100"

        self.app_logic.cancel_transfer(filename, peer_ip)
        self.app_logic.file_manager.cancel_transfer.assert_called_once_with(
            filename, peer_ip)

    def test_update_transfer_progress(self):
        """Test updating transfer progress"""
        filename = "test.txt"
        peer_ip = "192.168.1.100"
        progress = 75

        self.app_logic.update_transfer_progress(filename, peer_ip, progress)
        self.app_logic.file_manager.update_progress.assert_called_once_with(
            filename, peer_ip, progress)

    def test_remove_completed_transfers(self):
        """Test removing completed transfers"""
        self.app_logic.remove_completed_transfers()
        self.app_logic.file_manager.remove_completed.assert_called_once()

    def test_send_transfer_request_success(self):
        """Test successful transfer request"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name

        try:
            self.app_logic.chat_manager.send_transfer_request.return_value = "request_123"
            request_id = self.app_logic.send_transfer_request(
                "192.168.1.100", temp_path)

            self.assertEqual(request_id, "request_123")
            self.assertIn("request_123", self.app_logic.pending_transfers)
            self.assertEqual(
                self.app_logic.pending_transfers["request_123"], ("192.168.1.100", temp_path))
        finally:
            os.unlink(temp_path)

    def test_send_transfer_request_nonexistent(self):
        """Test transfer request for nonexistent file"""
        request_id = self.app_logic.send_transfer_request(
            "192.168.1.100", "/nonexistent/file.txt")
        self.assertIsNone(request_id)

    def test_respond_to_transfer_request(self):
        """Test responding to transfer request"""
        peer_ip = "192.168.1.100"
        request_id = "request_123"
        response = "accept"

        self.app_logic.respond_to_transfer_request(
            peer_ip, request_id, response)
        self.app_logic.chat_manager.send_transfer_response.assert_called_once_with(
            peer_ip, request_id, response)

    def test_handle_transfer_response_accept(self):
        """Test handling accepted transfer response"""
        request_id = "request_123"
        peer_ip = "192.168.1.100"

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            file_path = temp_file.name

        try:
            self.app_logic.pending_transfers[request_id] = (peer_ip, file_path)
            self.app_logic.handle_transfer_response(request_id, "accept")

            # Should start file transfer and remove from pending
            self.app_logic.network_manager.send_file.assert_called_once_with(
                peer_ip, file_path)
            self.assertNotIn(request_id, self.app_logic.pending_transfers)
        finally:
            os.unlink(file_path)

    def test_handle_transfer_response_decline(self):
        """Test handling declined transfer response"""
        request_id = "request_123"
        peer_ip = "192.168.1.100"
        file_path = "/path/to/file.txt"

        self.app_logic.pending_transfers[request_id] = (peer_ip, file_path)
        self.app_logic.handle_transfer_response(request_id, "decline")

        # Should not start transfer but remove from pending
        self.app_logic.network_manager.send_file.assert_not_called()
        self.assertNotIn(request_id, self.app_logic.pending_transfers)

    def test_add_peer(self):
        """Test adding a peer"""
        peer = "192.168.1.101"
        self.app_logic.add_peer(peer)
        self.app_logic.network_manager.add_peer.assert_called_once_with(peer)

    def test_remove_peer(self):
        """Test removing a peer"""
        peer = "192.168.1.101"
        self.app_logic.remove_peer(peer)
        self.app_logic.network_manager.remove_peer.assert_called_once_with(
            peer)

    def test_stop(self):
        """Test stopping the app logic"""
        self.app_logic.stop()
        self.app_logic.network_manager.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
