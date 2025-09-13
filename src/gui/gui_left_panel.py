from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTextEdit, QListWidget, QHBoxLayout, QPushButton


def create_left_panel():
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(20)
    layout.setContentsMargins(0, 0, 10, 0)
    network_group = QGroupBox("Network Status")
    network_layout = QVBoxLayout(network_group)
    network_layout.setSpacing(15)
    network_info = QTextEdit()
    network_info.setFixedHeight(120)
    network_info.setPlainText(
        f"""🔍 Scanning for peers...\n🌐 Local IP: 10.0.0.1\n🎯 Port: 5000\n📡 Discovery: Active\n⚡ Protocol: TCP/UDP Hybrid""")
    network_info.setReadOnly(True)
    network_layout.addWidget(network_info)
    layout.addWidget(network_group)
    peers_group = QGroupBox("Connected Peers")
    peers_layout = QVBoxLayout(peers_group)
    peers_layout.setSpacing(15)
    peers_list = QListWidget()
    # Populate peers from logic
    for peer in range(1, 6):  # Placeholder for demo
        peers_list.addItem(f"🟢 10.0.0.{peer}")
    peers_layout.addWidget(peers_list)
    peer_buttons = QHBoxLayout()
    peer_buttons.setSpacing(10)
    refresh_btn = QPushButton("Refresh")
    browse_btn = QPushButton("Browse Files")
    peer_buttons.addWidget(refresh_btn)
    peer_buttons.addWidget(browse_btn)
    peers_layout.addLayout(peer_buttons)
    layout.addWidget(peers_group)
    layout.addStretch()

    def refresh_peers():
        peers_list.clear()
        for peer in range(1, 6):  # Placeholder for demo
            peers_list.addItem(f"🟢 10.0.0.{peer}")
    refresh_btn.clicked.connect(refresh_peers)
    return widget
