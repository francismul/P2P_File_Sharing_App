import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from .gui_style import get_modern_style
from .gui_header import create_header
from .gui_left_panel import create_left_panel
from .gui_right_panel import create_right_panel
from .gui_status_bar import create_status_bar


class ModernP2PGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ShareSync - P2P File Network")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet(get_modern_style())
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        header = create_header()
        main_layout.addWidget(header)
        content_area = QSplitter(Qt.Orientation.Horizontal)
        left_panel = create_left_panel()
        content_area.addWidget(left_panel)
        right_panel = create_right_panel()
        content_area.addWidget(right_panel)
        content_area.setStretchFactor(0, 1)
        content_area.setStretchFactor(1, 2)
        content_area.setSizes([350, 700])
        main_layout.addWidget(content_area, 1)
        status_bar = create_status_bar()
        main_layout.addWidget(status_bar)


def main():
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ModernP2PGui()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
