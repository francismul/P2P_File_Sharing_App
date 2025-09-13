from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


def create_header():
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
    status = QLabel("● Offline")
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
    layout.addWidget(status)
    connect_btn = QPushButton("Connect to Network")
    connect_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #a6e3a1, stop: 1 #94e2d5);
            font-size: 14px;
            padding: 12px 24px;
            margin-left: 15px;
        }
    """)
    layout.addWidget(connect_btn)
    return header
