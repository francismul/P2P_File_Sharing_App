from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel


def create_status_bar():
    status_bar = QFrame()
    status_bar.setFixedHeight(50)
    status_bar.setStyleSheet("""
        QFrame { 
            background: rgba(30, 30, 46, 0.6);
            border: 1px solid rgba(69, 71, 90, 0.5);
            border-radius: 10px;
        }
    """)
    layout = QHBoxLayout(status_bar)
    layout.setContentsMargins(25, 8, 25, 8)
    network_status = QLabel("🌐 Network: 3 peers connected")
    network_status.setStyleSheet(
        "QLabel { border: none; font-size: 12px; color: #a6e3a1; font-weight: 500; }")
    transfer_status = QLabel("📊 Transfers: 2 active, 1 completed")
    transfer_status.setStyleSheet(
        "QLabel { border: none; font-size: 12px; color: #89b4fa; font-weight: 500; }")
    bandwidth_status = QLabel("⚡ Bandwidth: ↓ 1.2 MB/s  ↑ 0.8 MB/s")
    bandwidth_status.setStyleSheet(
        "QLabel { border: none; font-size: 12px; color: #f9e2af; font-weight: 500; }")
    layout.addWidget(network_status)
    layout.addWidget(transfer_status)
    layout.addStretch()
    layout.addWidget(bandwidth_status)
    return status_bar
