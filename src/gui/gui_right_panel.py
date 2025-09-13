from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .gui_files_tab import create_files_tab
from .gui_transfers_tab import create_transfers_tab
from .gui_chat_tab import create_chat_tab


def create_right_panel():
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(0)
    layout.setContentsMargins(10, 0, 0, 0)
    tabs = QTabWidget()
    files_tab = create_files_tab()
    tabs.addTab(files_tab, "📁 Files")
    transfers_tab = create_transfers_tab()
    tabs.addTab(transfers_tab, "📤 Transfers")
    chat_tab = create_chat_tab()
    tabs.addTab(chat_tab, "💬 Chat")
    layout.addWidget(tabs)
    return widget
