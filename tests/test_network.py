import unittest
import socket
import time

from src.logic.network import NetworkManager


class TestNetworkManager(unittest.TestCase):
    def setUp(self):
        self.network_manager = NetworkManager()

    def test_peer_add_remove(self):
        self.network_manager.add_peer("127.0.0.2")
        self.assertIn("127.0.0.2", self.network_manager.get_peers())
        self.network_manager.remove_peer("127.0.0.2")
        self.assertNotIn("127.0.0.2", self.network_manager.get_peers())

    def test_lan_status(self):
        status, ip = self.network_manager.get_lan_status()
        self.assertIsInstance(status, bool)
        self.assertIsInstance(ip, str)

    def test_port_in_use(self):
        self.network_manager.start()
        time.sleep(0.5)  # Give threads time to start
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.assertRaises(OSError):
            sock.bind(("", self.network_manager.port))
        sock.close()
        self.network_manager.stop()

    def test_udp_port_in_use(self):
        self.network_manager.start()
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        with self.assertRaises(OSError):
            sock.bind(("", self.network_manager.broadcast_port))
        sock.close()
        self.network_manager.stop()

    def test_socket_cleanup(self):
        self.network_manager.start()
        time.sleep(0.5)
        self.network_manager.stop()
        time.sleep(0.5)  # Allow time for sockets to close
        # After stop, ports should be free
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.bind(("", self.network_manager.port))
        sock_tcp.close()
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp.bind(("", self.network_manager.broadcast_port))
        sock_udp.close()


if __name__ == "__main__":
    unittest.main()
