# ShareSync - P2P File Sharing App

ShareSync is a modern peer-to-peer (P2P) file sharing application with a
graphical user interface (GUI) built using PyQt5. It enables users to discover
peers on the local network, share files, and chat in real time.

## Features

- **Peer Discovery:**
  - Automatically scans and discovers other peers on the local network using UDP
    broadcast.
  - Displays a list of connected peers in the GUI.

- **File Sharing:**
  - Send files to any discovered peer using TCP sockets.
  - Select files from the GUI and send to a chosen peer.
  - Shows available files and transfer status.

- **Chat System:**
  - Real-time chat between connected peers.
  - Chat messages are displayed in the GUI and sent using the network logic.

- **Modern GUI:**
  - Stylish, responsive interface with tabs for Files, Transfers, and Chat.
  - Status bar shows network, transfer, and bandwidth information.
  - All actions (refresh peers, send files, send chat) are accessible from the
    GUI.

- **Controller & Logic Integration:**
  - The GUI is fully wired to the app logic via a controller and logic modules.
  - All network and chat operations are handled by dedicated classes
    (`NetworkManager`, `ChatManager`, `AppLogic`).

## How It Works

1. **Startup:**
   - The app starts network and chat managers, begins peer discovery, and
     initializes the GUI.
2. **Peer Discovery:**
   - Peers are discovered and listed in the GUI. You can refresh the list at any
     time.
3. **File Sharing:**
   - Select a file and a peer, then send the file. Transfers are shown in the
     Transfers tab.
4. **Chat:**
   - Type and send messages to other peers in real time.

## Requirements

- Python 3.x
- PyQt5
- Other dependencies listed in `requirements.txt`

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py` - Entry point for the application
- `gui/` - Modular GUI components
- `src/network/` - Network and peer logic
- `src/logic/` - Application logic and controller

## License

MIT

## Contributing

Feel free to modify and expand the README as needed for your project!
