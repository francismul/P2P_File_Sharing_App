import os
import logging
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import threading
import tempfile

logger = logging.getLogger("ShareSync.WebServer")


class WebServer:
    def __init__(self, app_logic, port=8080):
        self.app_logic = app_logic
        self.port = port
        self.app = Flask(__name__, static_folder='../web', static_url_path='')
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Routes
        @self.app.route('/')
        def index():
            return send_from_directory('../web', 'index.html')

        @self.app.route('/<path:path>')
        def static_files(path):
            return send_from_directory('../web', path)

        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                return {'error': 'No file provided'}, 400

            file = request.files['file']
            peer_ip = request.form.get('peer_ip')

            if not peer_ip:
                return {'error': 'No peer IP provided'}, 400

            # Save file temporarily
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)

            # Send file via app logic
            success = self.app_logic.send_file(peer_ip, temp_path)

            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass

            if success:
                return {'success': True, 'message': f'File sent to {peer_ip}'}
            else:
                return {'error': 'Failed to send file'}, 500

        # SocketIO events
        @self.socketio.on('connect')
        def handle_connect():
            logger.info("Web client connected")
            # Send current peers
            peers = self.app_logic.get_peers()
            emit('peers_update', {'peers': list(peers)})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("Web client disconnected")

        @self.socketio.on('get_peers')
        def handle_get_peers():
            peers = self.app_logic.get_peers()
            emit('peers_update', {'peers': list(peers)})

        @self.socketio.on('connect_to_peer')
        def handle_connect_to_peer(data):
            peer_ip = data.get('peer_ip')
            if peer_ip:
                logger.info(f"Web client requesting connection to {peer_ip}")
                # For now, just acknowledge. WebRTC connection will be handled in JS
                emit('connection_request_ack', {'peer_ip': peer_ip})

        @self.socketio.on('send_file')
        def handle_send_file(data):
            peer_ip = data.get('peer_ip')
            file_path = data.get('file_path')
            if peer_ip and file_path:
                success = self.app_logic.send_file(peer_ip, file_path)
                emit('file_send_result', {
                     'success': success, 'file_path': file_path})

    def start(self):
        logger.info(f"Starting web server on port {self.port}")
        # Run in a separate thread
        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()

    def _run_server(self):
        self.socketio.run(self.app, host='0.0.0.0',
                          port=self.port, debug=False)

    def broadcast_peers_update(self):
        """Broadcast updated peer list to all connected web clients"""
        peers = self.app_logic.get_peers()
        self.socketio.emit('peers_update', {'peers': list(peers)})
