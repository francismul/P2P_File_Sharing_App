class P2PFileShare {
  constructor() {
    this.socket = null;
    this.discoveredPeers = new Set();
    this.selectedPeer = null;
    this.init();
  }

  init() {
    this.log("P2P File Share initialized");
    this.connectToWebSocket();
  }

  connectToWebSocket() {
    this.socket = io('http://localhost:8080');

    this.socket.on('connect', () => {
      this.log("Connected to local P2P server");
      this.updateStatus("connected", "Connected to P2P network");
    });

    this.socket.on('disconnect', () => {
      this.log("Disconnected from local P2P server");
      this.updateStatus("disconnected", "Disconnected from P2P network");
    });

    this.socket.on('peers_update', (data) => {
      this.updatePeersList(data.peers);
    });

    this.socket.on('connection_request_ack', (data) => {
      this.log(`Connection request acknowledged for peer: ${data.peer_ip}`);
    });

    this.socket.on('file_send_result', (data) => {
      if (data.success) {
        this.log(`File sent successfully: ${data.file_path}`);
      } else {
        this.log(`Failed to send file: ${data.file_path}`);
      }
    });
  }

  updatePeersList(peers) {
    this.discoveredPeers = new Set(peers);
    const peersList = document.getElementById("peersList");
    peersList.innerHTML = "";

    if (peers.length === 0) {
      peersList.innerHTML = "<p>No peers discovered on the network.</p>";
      return;
    }

    peers.forEach(peer => {
      const peerItem = document.createElement("div");
      peerItem.className = "peer-item";
      peerItem.innerHTML = `
        <div class="peer-info">
          <div class="peer-ip">${peer}</div>
          <div class="peer-status">Available</div>
        </div>
        <button class="btn btn-small" onclick="p2pFileShare.selectPeer('${peer}')">Select</button>
      `;
      peersList.appendChild(peerItem);
    });

    this.log(`Discovered ${peers.length} peer(s) on the network`);
  }

  selectPeer(peerIp) {
    this.selectedPeer = peerIp;
    document.querySelectorAll('.peer-item').forEach(item => {
      item.classList.remove('selected');
    });
    event.target.closest('.peer-item').classList.add('selected');
    this.log(`Selected peer: ${peerIp}`);
    document.getElementById("fileSection").style.display = "block";
    this.updateStatus("connected", `Connected to peer: ${peerIp}`);
  }

  async connectToPeer() {
    // Connection is handled automatically when peer is selected
    // Files are sent directly through the backend
  }

  handleFileSelect(event) {
    const files = Array.from(event.target.files);
    this.processFiles(files);
  }

  handleDrop(event) {
    event.preventDefault();
    event.target.classList.remove("dragover");
    const files = Array.from(event.dataTransfer.files);
    this.processFiles(files);
  }

  processFiles(files) {
    // Group files by directory
    const fileGroups = {};
    const individualFiles = [];

    files.forEach(file => {
      if (file.webkitRelativePath) {
        // File from directory selection
        const pathParts = file.webkitRelativePath.split('/');
        const dirName = pathParts[0];

        if (!fileGroups[dirName]) {
          fileGroups[dirName] = [];
        }
        fileGroups[dirName].push(file);
      } else {
        // Individual file
        individualFiles.push(file);
      }
    });

    // Send individual files
    individualFiles.forEach(file => this.sendFile(file));

    // Send directories (as zip via backend)
    Object.entries(fileGroups).forEach(([dirName, dirFiles]) => {
      this.sendDirectory(dirName, dirFiles);
    });
  }

  sendDirectory(dirName, files) {
    if (!this.selectedPeer) {
      alert("Please select a peer first.");
      return;
    }

    if (!this.socket || !this.socket.connected) {
      alert("Not connected to P2P network.");
      return;
    }

    // Create a zip file in memory and upload
    this.createZipAndUpload(dirName, files);
  }

  async createZipAndUpload(dirName, files) {
    const zip = new JSZip();

    files.forEach(file => {
      const relativePath = file.webkitRelativePath;
      zip.file(relativePath, file);
    });

    const zipBlob = await zip.generateAsync({ type: 'blob' });
    const zipFile = new File([zipBlob], dirName + '.zip', { type: 'application/zip' });

    this.uploadFileToBackend(zipFile);
  }

  sendFile(file) {
    if (!this.selectedPeer) {
      alert("Please select a peer first.");
      return;
    }

    if (!this.socket || !this.socket.connected) {
      alert("Not connected to P2P network.");
      return;
    }

    // For web app, we need to upload the file to the backend first
    // Then the backend will handle sending to the peer
    this.uploadFileToBackend(file);
  }

  async uploadFileToBackend(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('peer_ip', this.selectedPeer);

    try {
      const response = await fetch('http://localhost:8080/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        this.log(`File uploaded and sent to peer: ${file.name}`);
        this.addFileToUI(file, file.name, "sending");
      } else {
        this.log(`Failed to upload file: ${file.name}`);
      }
    } catch (error) {
      this.log(`Error uploading file: ${error}`);
    }
  }

  async sendFileChunks(fileId) {
    const transfer = this.fileTransfers.get(fileId);
    if (!transfer) return;

    const { file, sentChunks, totalChunks } = transfer;
    const chunkSize = 16384;

    for (let i = sentChunks; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, file.size);
      const chunk = file.slice(start, end);

      const arrayBuffer = await chunk.arrayBuffer();

      const chunkData = {
        type: "file-chunk",
        fileId: fileId,
        chunkIndex: i,
        data: arrayBuffer,
      };

      this.sendMessage(chunkData);

      transfer.sentChunks = i + 1;
      this.updateFileProgress(fileId, ((i + 1) / totalChunks) * 100);

      // Small delay to prevent overwhelming the data channel
      if (i % 10 === 0) {
        await new Promise((resolve) => setTimeout(resolve, 10));
      }
    }

    this.log(`File transfer completed: ${file.name}`);
  }

  sendMessage(message) {
    if (this.dataChannel && this.dataChannel.readyState === "open") {
      this.dataChannel.send(JSON.stringify(message));
    }
  }

  handleDataChannelMessage(data) {
    try {
      const message = JSON.parse(data);

      if (message.type === "file-metadata") {
        this.handleFileMetadata(message);
      } else if (message.type === "file-chunk") {
        this.handleFileChunk(message);
      }
    } catch (error) {
      this.log("Error parsing message: " + error);
    }
  }

  handleFileMetadata(metadata) {
    this.log(
      `Receiving file: ${metadata.name} (${this.formatFileSize(metadata.size)})`
    );

    this.fileTransfers.set(metadata.fileId, {
      name: metadata.name,
      size: metadata.size,
      totalChunks: metadata.totalChunks,
      receivedChunks: 0,
      chunks: new Array(metadata.totalChunks),
    });

    this.addFileToUI(
      { name: metadata.name, size: metadata.size },
      metadata.fileId,
      "receiving"
    );
  }

  handleFileChunk(chunkMessage) {
    const transfer = this.fileTransfers.get(chunkMessage.fileId);
    if (!transfer) return;

    transfer.chunks[chunkMessage.chunkIndex] = new Uint8Array(
      chunkMessage.data
    );
    transfer.receivedChunks++;

    const progress = (transfer.receivedChunks / transfer.totalChunks) * 100;
    this.updateFileProgress(chunkMessage.fileId, progress);

    if (transfer.receivedChunks === transfer.totalChunks) {
      this.completeFileReception(chunkMessage.fileId);
    }
  }

  completeFileReception(fileId) {
    const transfer = this.fileTransfers.get(fileId);
    if (!transfer) return;

    // Combine all chunks
    const totalSize = transfer.chunks.reduce(
      (size, chunk) => size + chunk.length,
      0
    );
    const combinedArray = new Uint8Array(totalSize);
    let offset = 0;

    transfer.chunks.forEach((chunk) => {
      combinedArray.set(chunk, offset);
      offset += chunk.length;
    });

    // Create download link
    const blob = new Blob([combinedArray]);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = transfer.name;
    a.click();
    URL.revokeObjectURL(url);

    this.log(`File received and downloaded: ${transfer.name}`);
  }

  addFileToUI(file, fileId, type) {
    const fileList = document.getElementById("fileList");
    const fileItem = document.createElement("div");
    fileItem.className = "file-item";
    fileItem.id = "file-" + fileId;

    fileItem.innerHTML = `
                    <div class="file-info">
                        <div class="file-name">${
                          type === "sending" ? "📤" : "📥"
                        } ${file.name}</div>
                        <div class="file-size">${this.formatFileSize(
                          file.size
                        )}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-${fileId}"></div>
                        </div>
                    </div>
                `;

    fileList.appendChild(fileItem);
  }

  updateFileProgress(fileId, progress) {
    const progressBar = document.getElementById("progress-" + fileId);
    if (progressBar) {
      progressBar.style.width = progress + "%";
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  updateStatus(type, message) {
    const status = document.getElementById("connectionStatus");
    status.className = "status " + type;
    status.textContent = message;
  }

  log(message) {
    const logs = document.getElementById("logs");
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement("div");
    logEntry.className = "log-entry";
    logEntry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
    logs.appendChild(logEntry);
    logs.scrollTop = logs.scrollHeight;
  }
}

// Global instance
const p2pFileShare = new P2PFileShare();

// Global functions for UI interaction
function copyPeerId() {
  const peerId = document.getElementById("myPeerId").textContent;
  navigator.clipboard.writeText(peerId).then(() => {
    alert("Peer ID copied to clipboard!");
  });
}

function connectToPeer() {
  p2pFileShare.connectToPeer();
}

function handleFileSelect(event) {
  p2pFileShare.handleFileSelect(event);
}

function handleDrop(event) {
  p2pFileShare.handleDrop(event);
}

function handleDragOver(event) {
  event.preventDefault();
  event.target.classList.add("dragover");
}

function handleDragLeave(event) {
  event.target.classList.remove("dragover");
}
