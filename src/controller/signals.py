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
