from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QVBoxLayout, QFrame, QLabel, QProgressBar


def create_transfers_tab():
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(20)
    layout.setContentsMargins(20, 20, 20, 20)
    transfer_controls = QHBoxLayout()
    transfer_controls.setSpacing(15)
    pause_btn = QPushButton("⏸️ Pause All")
    resume_btn = QPushButton("▶️ Resume All")
    cancel_btn = QPushButton("❌ Cancel All")
    transfer_controls.addWidget(pause_btn)
    transfer_controls.addWidget(resume_btn)
    transfer_controls.addWidget(cancel_btn)
    transfer_controls.addStretch()
    layout.addLayout(transfer_controls)
    transfers_group = QGroupBox("Active Transfers")
    transfers_layout = QVBoxLayout(transfers_group)
    transfers_layout.setSpacing(15)
    for i, (filename, progress, status, speed) in enumerate([
        ("Project_Report.pdf", 75, "Downloading", "1.2 MB/s"),
        ("Summer_Vibes.mp3", 100, "Completed", ""),
        ("Website_Backup.zip", 23, "Paused", ""),
        ("Vacation_Photo.jpg", 0, "Queued", "")
    ]):
        transfer_item = QFrame()
        transfer_item.setStyleSheet("""
            QFrame {
                background: rgba(49, 50, 68, 0.3);
                border: 1px solid rgba(69, 71, 90, 0.5);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        transfer_layout = QVBoxLayout(transfer_item)
        transfer_layout.setSpacing(8)
        info_layout = QHBoxLayout()
        filename_label = QLabel(f"📁 {filename}")
        filename_label.setStyleSheet(
            "QLabel { font-weight: 600; border: none; padding: 0; }")
        status_label = QLabel(f"{status} {speed}")
        status_label.setStyleSheet(
            "QLabel { color: #6c7086; border: none; padding: 0; font-size: 11px; }")
        info_layout.addWidget(filename_label)
        info_layout.addStretch()
        info_layout.addWidget(status_label)
        transfer_layout.addLayout(info_layout)
        progress_bar = QProgressBar()
        progress_bar.setValue(progress)
        progress_bar.setFormat(
            f"{progress}%" if progress < 100 else "Complete")
        if progress == 100:
            progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                              stop: 0 #a6e3a1, stop: 1 #94e2d5);
                }
            """)
        transfer_layout.addWidget(progress_bar)
        transfers_layout.addWidget(transfer_item)
    layout.addWidget(transfers_group)
    return widget
