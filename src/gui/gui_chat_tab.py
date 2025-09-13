from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QHBoxLayout,
    QLineEdit,
    QPushButton
)

from src.controller import AppLogic
from src.controller import chat_signal


def create_chat_tab(app_logic: AppLogic):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(15)
    layout.setContentsMargins(20, 20, 20, 20)

    chat_display = QTextEdit()
    chat_display.setReadOnly(True)
    layout.addWidget(chat_display)

    chat_input_layout = QHBoxLayout()
    chat_input_layout.setSpacing(10)
    chat_input = QLineEdit()
    chat_input.setPlaceholderText("Type your message here...")
    send_btn = QPushButton("Send")
    send_btn.setFixedWidth(80)
    chat_input_layout.addWidget(chat_input, 1)
    chat_input_layout.addWidget(send_btn)
    layout.addLayout(chat_input_layout)

    # ---- Hook networking ----
    def handle_send():
        msg = chat_input.text().strip()
        if msg:
            app_logic.send_chat_message(msg)
            chat_input.clear()

    send_btn.clicked.connect(handle_send)
    chat_input.returnPressed.connect(handle_send)

    def update_chat_display(sender, message):
        chat_display.append(f"👤 {sender}: {message}")

    chat_signal.message_received.connect(update_chat_display)

    return widget, app_logic
