from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer


def create_header(app_logic):
    header = QFrame()
    header.setFixedHeight(90)
    header.setStyleSheet("""
        QFrame { 
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 rgba(137, 180, 250, 0.1), 
                                      stop: 1 rgba(116, 199, 236, 0.1));
            border: 2px solid rgba(137, 180, 250, 0.3);
            border-radius: 15px;
        }
    """)
    layout = QHBoxLayout(header)
    layout.setContentsMargins(30, 15, 30, 15)
    title = QLabel("ShareSync")
    title.setStyleSheet("""
        QLabel { 
            font-size: 28px; 
            font-weight: bold; 
            color: #89b4fa; 
            background: transparent;
            border: none;
            margin: 0px;
        }
    """)
    layout.addWidget(title)
    subtitle = QLabel("P2P File Network")
    subtitle.setStyleSheet("""
        QLabel { 
            font-size: 14px; 
            color: #6c7086; 
            background: transparent;
            border: none;
            margin-left: 15px;
            font-weight: normal;
        }
    """)
    layout.addWidget(subtitle)
    layout.addStretch()
    status = QLabel()

    def update_status():
        connected, local_ip = app_logic.get_lan_status()
        if connected:
            status.setText(f"● Online ({local_ip})")
            status.setStyleSheet("""
                QLabel { 
                    font-size: 14px; 
                    color: #a6e3a1; 
                    background: rgba(166, 227, 161, 0.1);
                    border: 1px solid rgba(166, 227, 161, 0.3);
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
            """)
        else:
            status.setText("● Offline")
            status.setStyleSheet("""
                QLabel { 
                    font-size: 14px; 
                    color: #f38ba8; 
                    background: rgba(243, 139, 168, 0.1);
                    border: 1px solid rgba(243, 139, 168, 0.3);
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
            """)
    update_status()
    layout.addWidget(status)
    # Auto-refresh every 2 seconds
    timer = QTimer(header)
    timer.timeout.connect(update_status)
    timer.start(2000)

    return header
