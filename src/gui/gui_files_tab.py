from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGroupBox, QListWidget


def create_files_tab():
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(20)
    layout.setContentsMargins(20, 20, 20, 20)
    file_actions = QHBoxLayout()
    file_actions.setSpacing(15)
    share_btn = QPushButton("Share Folder")
    download_btn = QPushButton("Download Selected")
    search_input = QLineEdit()
    search_input.setPlaceholderText("🔍 Search files...")
    search_input.setMinimumWidth(250)
    file_actions.addWidget(share_btn)
    file_actions.addWidget(download_btn)
    file_actions.addStretch()
    file_actions.addWidget(search_input)
    layout.addLayout(file_actions)
    files_group = QGroupBox("Available Files")
    files_layout = QVBoxLayout(files_group)
    files_layout.setSpacing(10)
    files_list = QListWidget()
    files_list.addItems([
        "📄 Project_Report.pdf • 2.5 MB • Alice",
        "🎵 Summer_Vibes.mp3 • 4.2 MB • Bob",
        "🗜️ Website_Backup.zip • 156 MB • Alice",
        "📝 README.txt • 1 KB • Charlie",
        "🖼️ Vacation_Photo.jpg • 3.1 MB • Bob",
        "📊 Sales_Presentation.pptx • 8.7 MB • Diana"
    ])
    files_layout.addWidget(files_list)
    layout.addWidget(files_group)
    # Example: send file to selected peer (first peer for demo)

    def send_selected_file():
        selected_items = files_list.selectedItems()
        if selected_items:
            file_name = selected_items[0].text().split(
                '•')[0].strip().split(' ')[-1]
            peers = ['10.0.0.1', '']
            if peers:
                # For demo, send to first peer and assume file exists locally
                pass
    download_btn.clicked.connect(send_selected_file)
    return widget
