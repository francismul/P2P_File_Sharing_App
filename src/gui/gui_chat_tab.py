from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QPushButton


def create_chat_tab():
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(15)
    layout.setContentsMargins(20, 20, 20, 20)
    chat_display = QTextEdit()
    chat_display.setReadOnly(True)
    chat_display.setPlainText("""🤖 System: Chat initialized - Welcome to ShareSync!
👤 Alice: Hey everyone! Just shared some new project files
👤 Bob: Thanks Alice! Downloading the presentation now
👤 You: Great timing, I needed those documents
👤 Charlie: My connection seems slow today, anyone else?
🤖 System: Charlie's connection quality: Poor (high latency detected)
👤 Alice: Try switching to a different peer for faster downloads
👤 Bob: @Charlie I can share those files directly with you
👤 Charlie: Much better now, thanks Bob! 🙏
🤖 System: Diana has left the network""")
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

    def send_chat():
        msg = chat_input.text()
        if msg:
            pass
            chat_display.append(f"👤 You: {msg}")
            chat_input.clear()
    send_btn.clicked.connect(send_chat)
    return widget
