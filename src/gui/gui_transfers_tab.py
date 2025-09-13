from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QVBoxLayout, QFrame, QLabel, QProgressBar


def create_transfers_tab(app_logic):
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
    layout.addWidget(transfers_group)

    def update_transfers():
        # Clear previous widgets
        while transfers_layout.count():
            item = transfers_layout.takeAt(0)
            if item is not None:
                w = item.widget()
                if w:
                    w.deleteLater()
        # Get active transfers from logic
        transfers = app_logic.get_active_transfers()
        if not transfers:
            empty_label = QLabel("No active transfers.")
            empty_label.setStyleSheet("color: #6c7086; font-size: 13px;")
            transfers_layout.addWidget(empty_label)
            return
        for t in transfers:
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
            filename_label = QLabel(f"📁 {t.filename}")
            filename_label.setStyleSheet(
                "QLabel { font-weight: 600; border: none; padding: 0; }")
            status_label = QLabel(f"{t.status} {t.speed}")
            status_label.setStyleSheet(
                "QLabel { color: #6c7086; border: none; padding: 0; font-size: 11px; }")
            info_layout.addWidget(filename_label)
            info_layout.addStretch()
            info_layout.addWidget(status_label)
            transfer_layout.addLayout(info_layout)
            progress_bar = QProgressBar()
            progress_bar.setValue(int(t.progress))
            progress_bar.setFormat(
                f"{int(t.progress)}%" if t.progress < 100 else "Complete")
            if t.progress >= 100:
                progress_bar.setStyleSheet("""
                    QProgressBar::chunk {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                                  stop: 0 #a6e3a1, stop: 1 #94e2d5);
                    }
                """)
            transfer_layout.addWidget(progress_bar)
            transfers_layout.addWidget(transfer_item)

    # Wire up control buttons
    def pause_all():
        for t in app_logic.get_active_transfers():
            app_logic.pause_transfer(t.filename, t.peer_ip)
        # update_transfers() will be called via signal

    def resume_all():
        for t in app_logic.get_active_transfers():
            app_logic.resume_transfer(t.filename, t.peer_ip)
        # update_transfers() will be called via signal

    def cancel_all():
        for t in app_logic.get_active_transfers():
            app_logic.cancel_transfer(t.filename, t.peer_ip)
        # update_transfers() will be called via signal
    pause_btn.clicked.connect(pause_all)
    resume_btn.clicked.connect(resume_all)
    cancel_btn.clicked.connect(cancel_all)

    # Connect FileManager signal for real-time updates
    app_logic.file_manager.transfers_changed.connect(update_transfers)
    update_transfers()
    return widget
