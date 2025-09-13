from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTextEdit, QListWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject

from src.controller import peer_signal
from src.controller import AppLogic

# Accept app_logic as argument


class PeerSignal(QObject):
    peers_changed = pyqtSignal()


def create_left_panel(app_logic: AppLogic):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(20)
    layout.setContentsMargins(0, 0, 10, 0)
    network_group = QGroupBox("Network Status")
    network_layout = QVBoxLayout(network_group)
    network_layout.setSpacing(15)
    network_info = QTextEdit()
    network_info.setFixedHeight(120)
    # Initial info

    def update_network_info():
        local_ip = app_logic.network_manager._get_local_ip()
        port = app_logic.network_manager.port
        peers = app_logic.get_peers()
        peer_count = len(peers)
        status_msg = (
            f"🔍 Scanning for peers...\n"
            f"🌐 Local IP: {local_ip}\n"
            f"🎯 Port: {port}\n"
            f"📡 Discovery: Active\n"
            f"⚡ Protocol: TCP/UDP Hybrid\n"
            f"👥 Peers found: {peer_count}"
        )
        network_info.setPlainText(status_msg)

    network_info.setReadOnly(True)
    network_layout.addWidget(network_info)
    layout.addWidget(network_group)
    peers_group = QGroupBox("Connected Peers")
    peers_layout = QVBoxLayout(peers_group)
    peers_layout.setSpacing(15)
    peers_list = QListWidget()
    # Populate peers from app_logic

    def update_peers_list():
        peers_list.clear()
        peers = app_logic.get_peers()
        if peers:
            for peer in peers:
                peers_list.addItem(f"🟢 {peer}")
        else:
            peers_list.addItem("No peers found. Waiting for connections...")

    peers_layout.addWidget(peers_list)
    peer_buttons = QHBoxLayout()
    peer_buttons.setSpacing(10)
    refresh_btn = QPushButton("Refresh")
    peer_buttons.addWidget(refresh_btn)
    peers_layout.addLayout(peer_buttons)
    layout.addWidget(peers_group)
    layout.addStretch()
    # Refresh button updates both network info and peers

    def refresh_all():
        update_network_info()
        update_peers_list()

    refresh_btn.clicked.connect(refresh_all)
    # Connect signal for real-time updates
    peer_signal.peers_changed.connect(refresh_all)
    refresh_all()
    return widget
