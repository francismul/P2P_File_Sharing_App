from src.gui.gui_main import main
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget
)


class ModernP2PGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ShareSync - P2P File Network")
        self.setGeometry(100, 100, 1200, 800)

        # Set the main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    main()
