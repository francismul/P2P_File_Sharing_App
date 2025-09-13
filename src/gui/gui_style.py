def get_modern_style():
    return """
    QMainWindow {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                  stop: 0 #1e1e2e, stop: 1 #181825);
        color: #cdd6f4;
    }
    QWidget {
        background: transparent;
        color: #cdd6f4;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QLabel {
        color: #cdd6f4;
        background: transparent;
        padding: 8px;
        border-radius: 6px;
        font-size: 13px;
    }
    QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #89b4fa, stop: 1 #74c7ec);
        color: #11111b;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 13px;
        font-weight: 600;
        min-height: 16px;
    }
    QPushButton:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #94bffe, stop: 1 #7fd3f3);
    }
    QPushButton:pressed {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #7aa2f7, stop: 1 #6cb6e8);
    }
    QPushButton:disabled {
        background: #45475a;
        color: #6c7086;
    }
    QListWidget {
        background: rgba(49, 50, 68, 0.8);
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 12px;
        padding: 8px;
        font-size: 12px;
        selection-background-color: rgba(137, 180, 250, 0.3);
        outline: none;
    }
    QListWidget::item {
        padding: 12px;
        border-radius: 6px;
        margin: 2px 0px;
        border: none;
    }
    QListWidget::item:selected {
        background: rgba(137, 180, 250, 0.2);
        color: #89b4fa;
    }
    QListWidget::item:hover {
        background: rgba(137, 180, 250, 0.1);
    }
    QProgressBar {
        border: none;
        background: #313244;
        border-radius: 8px;
        text-align: center;
        color: #cdd6f4;
        font-weight: 600;
        height: 20px;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                  stop: 0 #a6e3a1, stop: 1 #94e2d5);
        border-radius: 8px;
        margin: 2px;
    }
    QTextEdit {
        background: rgba(49, 50, 68, 0.6);
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 12px;
        padding: 15px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 11px;
        line-height: 1.4;
    }
    QLineEdit {
        background: rgba(49, 50, 68, 0.8);
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
    }
    QLineEdit:focus {
        border: 2px solid #89b4fa;
        background: rgba(49, 50, 68, 1.0);
    }
    QGroupBox {
        color: #cdd6f4;
        border: 2px solid #45475a;
        border-radius: 12px;
        margin-top: 15px;
        font-size: 14px;
        font-weight: 600;
        background: rgba(30, 30, 46, 0.5);
        padding-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 5px 15px;
        background: #89b4fa;
        color: #11111b;
        border-radius: 6px;
        font-weight: bold;
    }
    QTabWidget::pane {
        border: 2px solid #45475a;
        border-radius: 12px;
        background: rgba(30, 30, 46, 0.3);
        padding: 5px;
    }
    QTabBar::tab {
        background: rgba(69, 71, 90, 0.7);
        color: #cdd6f4;
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        margin: 2px;
        font-weight: 500;
        min-width: 80px;
    }
    QTabBar::tab:selected {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #89b4fa, stop: 1 #74c7ec);
        color: #11111b;
        font-weight: bold;
    }
    QTabBar::tab:hover:!selected {
        background: rgba(137, 180, 250, 0.2);
    }
    QSplitter::handle {
        background: #45475a;
        border-radius: 3px;
    }
    QSplitter::handle:horizontal {
        width: 6px;
    }
    QSplitter::handle:vertical {
        height: 6px;
    }
    QFrame {
        border-radius: 12px;
        background: rgba(30, 30, 46, 0.4);
    }
    """
