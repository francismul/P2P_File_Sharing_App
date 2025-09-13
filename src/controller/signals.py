from PyQt5.QtCore import pyqtSignal, QObject


class PeerSignal(QObject):
    peers_changed = pyqtSignal()


peer_signal = PeerSignal()


class ChatSignal(QObject):
    message_received = pyqtSignal(str, str)  # sender, message


chat_signal = ChatSignal()


class BandwidthSignal(QObject):
    bandwidth_changed = pyqtSignal(float, float)  # download, upload in MB/s


bandwidth_signal = BandwidthSignal()


class TransferRequestSignal(QObject):
    # sender_ip, filename, file_size, request_id
    transfer_request_received = pyqtSignal(str, str, str, str)
    # request_id, response (accept/decline)
    transfer_response_received = pyqtSignal(str, str)


transfer_request_signal = TransferRequestSignal()
