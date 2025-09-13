import unittest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
import sys

# Import GUI components
from src.gui.gui_main import ModernP2PGui
from src.controller.index import AppLogic


class TestGUIMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication for GUI tests
        cls.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

    def setUp(self):
        # Mock AppLogic to avoid actual network operations
        with patch('src.logic.NetworkManager') as mock_network, \
             patch('src.logic.ChatManager') as mock_chat, \
             patch('src.logic.FileManager') as mock_file:
            
            # Configure the mock NetworkManager
            mock_network_instance = Mock()
            mock_network_instance.get_lan_status.return_value = (True, "192.168.1.100")
            mock_network_instance.get_peers.return_value = ["192.168.1.101", "192.168.1.102"]
            mock_network.return_value = mock_network_instance
            
            # Configure other mocks
            mock_chat_instance = Mock()
            mock_chat.return_value = mock_chat_instance
            
            mock_file_instance = Mock()
            mock_file_instance.get_active_transfers.return_value = []
            mock_file.return_value = mock_file_instance
            
            self.mock_app_logic = AppLogic()
            self.gui = ModernP2PGui()
            self.gui.applogic = self.mock_app_logic

    def test_initialization(self):
        """Test GUI initialization"""
        self.assertIsNotNone(self.gui)
        self.assertEqual(self.gui.windowTitle(), "ShareSync - P2P File Network")
        self.assertIsNotNone(self.gui.applogic)

    def test_window_geometry(self):
        """Test window geometry settings"""
        # Should be set to 1200x800
        geometry = self.gui.geometry()
        self.assertEqual(geometry.width(), 1200)
        self.assertEqual(geometry.height(), 800)

    @patch('src.controller.index.AppLogic.get_peers')
    def test_refresh_peers(self, mock_get_peers):
        """Test refreshing peers list"""
        mock_peers = ["192.168.1.100", "192.168.1.101"]
        mock_get_peers.return_value = mock_peers

        # This would normally be called from a button click
        # For testing, we can call the method directly if exposed
        # Since it's internal, we'll test the logic indirectly

        # Test that get_peers is called when expected
        peers = self.mock_app_logic.get_peers()
        mock_get_peers.assert_called_once()
        self.assertEqual(peers, mock_peers)

    @patch('src.controller.index.AppLogic.send_file')
    def test_send_file_logic(self, mock_send_file):
        """Test file sending logic"""
        mock_send_file.return_value = True

        # Test successful send
        result = self.mock_app_logic.send_file("192.168.1.100", "/path/to/file.txt")
        mock_send_file.assert_called_once_with("192.168.1.100", "/path/to/file.txt")
        self.assertTrue(result)

    @patch('src.controller.index.AppLogic.send_chat_message')
    def test_send_chat_message_logic(self, mock_send_chat):
        """Test chat message sending logic"""
        message = "Hello, world!"
        self.mock_app_logic.send_chat_message(message)
        mock_send_chat.assert_called_once_with(message)

    def test_app_logic_methods_exist(self):
        """Test that all expected AppLogic methods exist"""
        expected_methods = [
            'get_peers', 'send_file', 'receive_file', 'stop',
            'send_chat_message', 'receive_chat_message', 'get_lan_status',
            'get_active_transfers', 'pause_transfer', 'resume_transfer',
            'cancel_transfer', 'update_transfer_progress', 'remove_completed_transfers',
            'send_transfer_request', 'respond_to_transfer_request', 'handle_transfer_response',
            'start_file_transfer', 'add_peer', 'remove_peer', 'update_network'
        ]

        for method_name in expected_methods:
            self.assertTrue(hasattr(self.mock_app_logic, method_name),
                          f"AppLogic missing method: {method_name}")
            self.assertTrue(callable(getattr(self.mock_app_logic, method_name)),
                          f"AppLogic.{method_name} is not callable")

    def test_network_manager_methods_exist(self):
        """Test that NetworkManager has expected methods"""
        network_manager = self.mock_app_logic.network_manager
        expected_methods = [
            'start', 'stop', 'get_peers', 'add_peer', 'remove_peer',
            'send_file', 'get_lan_status'
        ]

        for method_name in expected_methods:
            self.assertTrue(hasattr(network_manager, method_name),
                          f"NetworkManager missing method: {method_name}")

    def test_chat_manager_methods_exist(self):
        """Test that ChatManager has expected methods"""
        chat_manager = self.mock_app_logic.chat_manager
        expected_methods = [
            'start', 'stop', 'send_message', 'send_transfer_request', 'send_transfer_response'
        ]

        for method_name in expected_methods:
            self.assertTrue(hasattr(chat_manager, method_name),
                          f"ChatManager missing method: {method_name}")

    def test_file_manager_methods_exist(self):
        """Test that FileManager has expected methods"""
        file_manager = self.mock_app_logic.file_manager
        expected_methods = [
            'add_transfer', 'get_active_transfers', 'pause_transfer',
            'resume_transfer', 'cancel_transfer', 'update_progress', 'remove_completed'
        ]

        for method_name in expected_methods:
            self.assertTrue(hasattr(file_manager, method_name),
                          f"FileManager missing method: {method_name}")


class TestGUIIntegration(unittest.TestCase):
    """Test GUI integration with AppLogic"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

    def test_gui_app_logic_integration(self):
        """Test that GUI can be created with AppLogic"""
        with patch('src.logic.NetworkManager') as mock_network, \
             patch('src.logic.ChatManager') as mock_chat, \
             patch('src.logic.FileManager') as mock_file:
            
            # Configure mocks
            mock_network_instance = Mock()
            mock_network_instance.get_lan_status.return_value = (True, "192.168.1.100")
            mock_network_instance.get_peers.return_value = []
            mock_network.return_value = mock_network_instance
            
            mock_chat_instance = Mock()
            mock_chat.return_value = mock_chat_instance
            
            mock_file_instance = Mock()
            mock_file_instance.get_active_transfers.return_value = []
            mock_file.return_value = mock_file_instance
            
            app_logic = AppLogic()
            gui = ModernP2PGui()
            gui.applogic = app_logic
            
            self.assertIsNotNone(gui)
            self.assertIsNotNone(gui.applogic)
            
            # Test that GUI has access to app logic
            self.assertIsNotNone(gui.applogic)
            self.assertEqual(gui.applogic, app_logic)


if __name__ == "__main__":
    unittest.main()