import os
import json

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QListWidget,
    QFileDialog,
    QMessageBox,
    QMenu,
    QComboBox,
    QLabel,
)
from PyQt5.QtCore import Qt

from src.controller import AppLogic
from src.controller import transfer_request_signal
from src.controller import peer_signal

SHARED_FILES_FILE = "src/shared_files.json"


def create_files_tab(app_logic: AppLogic):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(20)
    layout.setContentsMargins(20, 20, 20, 20)

    # Shared files storage
    shared_files = []

    def save_shared_files():
        try:
            os.makedirs(os.path.dirname(SHARED_FILES_FILE), exist_ok=True)
            with open(SHARED_FILES_FILE, 'w') as f:
                json.dump(shared_files, f, indent=2)
        except Exception as e:
            print(f"Error saving shared files: {e}")

    def load_shared_files():
        try:
            if os.path.exists(SHARED_FILES_FILE):
                with open(SHARED_FILES_FILE, 'r') as f:
                    loaded_files = json.load(f)
                    # Filter out files that no longer exist
                    return [f for f in loaded_files if os.path.exists(f)]
        except Exception as e:
            print(f"Error loading shared files: {e}")
        return []

    # Load shared files on startup
    shared_files = load_shared_files()

    # Peer selection and send controls
    send_controls = QHBoxLayout()
    send_controls.setSpacing(15)

    peer_label = QLabel("Select Peer:")
    peer_combo = QComboBox()
    peer_combo.addItem("Select a peer...")

    def update_peer_list():
        peer_combo.clear()
        peer_combo.addItem("Select a peer...")
        peers = app_logic.get_peers()
        for peer in peers:
            peer_combo.addItem(peer)

    update_peer_list()

    send_file_btn = QPushButton("📄 Send File")
    send_folder_btn = QPushButton("📁 Send Folder")

    send_controls.addWidget(peer_label)
    send_controls.addWidget(peer_combo)
    send_controls.addWidget(send_file_btn)
    send_controls.addWidget(send_folder_btn)
    send_controls.addStretch()

    layout.addLayout(send_controls)

    # File actions (keeping original buttons for local sharing)
    file_actions = QHBoxLayout()
    file_actions.setSpacing(15)

    search_input = QLineEdit()
    search_input.setPlaceholderText("🔍 Search shared files...")
    search_input.setMinimumWidth(250)

    file_actions.addStretch()
    file_actions.addWidget(search_input)
    layout.addLayout(file_actions)

    files_group = QGroupBox("Shared Files")
    files_layout = QVBoxLayout(files_group)
    files_layout.setSpacing(10)

    files_list = QListWidget()
    files_list.setSelectionMode(QListWidget.MultiSelection)
    files_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def update_files_display():
        files_list.clear()
        for file_path in shared_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                size_str = f"{file_size / (1024*1024):.1f} MB" if file_size > 1024 * \
                    1024 else f"{file_size / 1024:.1f} KB"
                display_name = os.path.basename(file_path)
                files_list.addItem(f"📄 {display_name} • {size_str}")
            else:
                # Remove if file no longer exists
                shared_files.remove(file_path)
        save_shared_files()  # Save after cleanup

    def search_files():
        query = search_input.text().lower()
        for i in range(files_list.count()):
            item = files_list.item(i)
            if item:
                item.setHidden(query not in item.text().lower())

    def show_context_menu(position):
        menu = QMenu()
        remove_action = menu.addAction("Remove from Sharing")
        action = menu.exec_(files_list.mapToGlobal(position))
        if action == remove_action:
            selected_items = files_list.selectedItems()
            for item in selected_items:
                # Find the corresponding file path
                display_text = item.text()
                file_name = display_text.split(" • ")[0].replace("📄 ", "")
                # Copy to avoid modification during iteration
                for file_path in shared_files[:]:
                    if os.path.basename(file_path) == file_name:
                        shared_files.remove(file_path)
                        break
            update_files_display()
            save_shared_files()

    def send_file_to_peer():
        selected_peer = peer_combo.currentText()
        if selected_peer == "Select a peer...":
            QMessageBox.warning(widget, "No Peer Selected",
                                "Please select a peer to send to.")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            widget, "Select File to Send")
        if file_path:
            request_id = app_logic.send_transfer_request(
                selected_peer, file_path)
            if request_id:
                QMessageBox.information(
                    widget, "Request Sent", f"Transfer request sent to {selected_peer}")
            else:
                QMessageBox.warning(
                    widget, "Error", "Failed to send transfer request.")

    def send_folder_to_peer():
        selected_peer = peer_combo.currentText()
        if selected_peer == "Select a peer...":
            QMessageBox.warning(widget, "No Peer Selected",
                                "Please select a peer to send to.")
            return

        folder_path = QFileDialog.getExistingDirectory(
            widget, "Select Folder to Send")
        if folder_path:
            request_id = app_logic.send_transfer_request(
                selected_peer, folder_path)
            if request_id:
                QMessageBox.information(
                    widget, "Request Sent", f"Transfer request sent to {selected_peer}")
            else:
                QMessageBox.warning(
                    widget, "Error", "Failed to send transfer request.")

    def handle_transfer_request(sender_ip, filename, file_size, request_id):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Transfer Request")
        msg.setText(
            f"{sender_ip} wants to send you: {filename} ({file_size} bytes)")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        response = msg.exec_()
        if response == QMessageBox.Yes:
            app_logic.respond_to_transfer_request(
                sender_ip, request_id, "accept")
            QMessageBox.information(
                widget, "Accepted", f"Accepted transfer from {sender_ip}")
            # TODO: Start receiving the file
        else:
            app_logic.respond_to_transfer_request(
                sender_ip, request_id, "decline")
            QMessageBox.information(
                widget, "Declined", f"Declined transfer from {sender_ip}")

    def handle_transfer_response(request_id, response):
        app_logic.handle_transfer_response(request_id, response)
        if response == "accept":
            QMessageBox.information(
                widget, "Transfer Accepted", "The recipient accepted your transfer request!")
        else:
            QMessageBox.information(
                widget, "Transfer Declined", "The recipient declined your transfer request.")

    search_input.textChanged.connect(search_files)
    files_list.customContextMenuRequested.connect(show_context_menu)
    send_file_btn.clicked.connect(send_file_to_peer)
    send_folder_btn.clicked.connect(send_folder_to_peer)
    transfer_request_signal.transfer_request_received.connect(
        handle_transfer_request)
    transfer_request_signal.transfer_response_received.connect(
        handle_transfer_response)
    peer_signal.peers_changed.connect(update_peer_list)

    files_layout.addWidget(files_list)
    layout.addWidget(files_group)

    # Initial display
    update_files_display()

    return widget
