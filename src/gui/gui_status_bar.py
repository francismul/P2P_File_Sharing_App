from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from src.controller import AppLogic

from src.controller import peer_signal
from src.controller import bandwidth_signal


def create_status_bar(app_logic: AppLogic):
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
    network_status = QLabel()
    network_status.setStyleSheet(
        "QLabel { border: none; font-size: 12px; color: #a6e3a1; font-weight: 500; }")
    transfer_status = QLabel()
    transfer_status.setStyleSheet(
        "QLabel { border: none; font-size: 12px; color: #89b4fa; font-weight: 500; }")
    bandwidth_status = QLabel()
    bandwidth_status.setStyleSheet(
        "QLabel { border: none; font-size: 12px; color: #f9e2af; font-weight: 500; }")
    layout.addWidget(network_status)
    layout.addWidget(transfer_status)
    layout.addStretch()
    layout.addWidget(bandwidth_status)

    def update_network_status():
        peers = app_logic.get_peers()
        network_status.setText(f"🌐 Network: {len(peers)} peers connected")

    def update_transfer_status():
        transfers = app_logic.get_active_transfers()
        active = sum(1 for t in transfers if t.status == "active")
        completed = sum(1 for t in transfers if t.status == "completed")
        transfer_status.setText(
            f"📊 Transfers: {active} active, {completed} completed")

    def update_bandwidth_status(download=1.2, upload=0.8):
        bandwidth_status.setText(
            f"⚡ Bandwidth: ↓ {download:.2f} MB/s  ↑ {upload:.2f} MB/s")

    def update_all():
        update_network_status()
        update_transfer_status()
        update_bandwidth_status()

    peer_signal.peers_changed.connect(update_network_status)
    if hasattr(app_logic.file_manager, "transfers_changed"):
        app_logic.file_manager.transfers_changed.connect(
            update_transfer_status)
    bandwidth_signal.bandwidth_changed.connect(update_bandwidth_status)
    update_all()
    return status_bar
