import unittest
import time
from unittest.mock import Mock
from src.logic.file_manager import FileManager, FileTransfer


class TestFileTransfer(unittest.TestCase):
    def setUp(self):
        self.filename = "test.txt"
        self.peer_ip = "192.168.1.100"
        self.size = 1024
        self.transfer = FileTransfer(self.filename, self.peer_ip, self.size)

    def test_initialization(self):
        """Test FileTransfer initialization"""
        self.assertEqual(self.transfer.filename, self.filename)
        self.assertEqual(self.transfer.peer_ip, self.peer_ip)
        self.assertEqual(self.transfer.size, self.size)
        self.assertEqual(self.transfer.progress, 0)
        self.assertEqual(self.transfer.status, "Queued")
        self.assertFalse(self.transfer.paused)
        self.assertFalse(self.transfer.cancelled)

    def test_update_progress_partial(self):
        """Test updating progress to partial completion"""
        self.transfer.update_progress(50)
        self.assertEqual(self.transfer.progress, 50)
        self.assertEqual(self.transfer.status, "Downloading")

    def test_update_progress_complete(self):
        """Test updating progress to completion"""
        self.transfer.update_progress(100)
        self.assertEqual(self.transfer.progress, 100)
        self.assertEqual(self.transfer.status, "Completed")

    def test_update_progress_speed_calculation(self):
        """Test speed calculation during progress update"""
        # First update
        self.transfer.update_progress(25)
        time.sleep(0.1)  # Small delay for speed calculation

        # Second update
        self.transfer.update_progress(50)

        # Speed should be calculated and non-empty
        self.assertNotEqual(self.transfer.speed, "")
        self.assertTrue("KB/s" in self.transfer.speed)


class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.file_manager = FileManager()
        self.filename = "test.txt"
        self.peer_ip = "192.168.1.100"
        self.size = 1024

    def test_initialization(self):
        """Test FileManager initialization"""
        self.assertEqual(self.file_manager.transfers, {})

    def test_add_transfer(self):
        """Test adding a new transfer"""
        transfer = self.file_manager.add_transfer(self.filename, self.peer_ip, self.size)

        self.assertIsInstance(transfer, FileTransfer)
        self.assertEqual(transfer.filename, self.filename)
        self.assertEqual(transfer.peer_ip, self.peer_ip)
        self.assertEqual(transfer.size, self.size)

        # Check it's stored in transfers dict
        key = (self.filename, self.peer_ip)
        self.assertIn(key, self.file_manager.transfers)
        self.assertEqual(self.file_manager.transfers[key], transfer)

    def test_get_active_transfers(self):
        """Test getting active transfers"""
        # Add a queued transfer
        transfer1 = self.file_manager.add_transfer(self.filename, self.peer_ip, self.size)

        # Add a downloading transfer
        transfer2 = self.file_manager.add_transfer("file2.txt", "192.168.1.101", 2048)
        transfer2.status = "Downloading"

        # Add a completed transfer
        transfer3 = self.file_manager.add_transfer("file3.txt", "192.168.1.102", 512)
        transfer3.status = "Completed"

        active = self.file_manager.get_active_transfers()

        # Should only include queued and downloading transfers
        self.assertEqual(len(active), 2)
        self.assertIn(transfer1, active)
        self.assertIn(transfer2, active)
        self.assertNotIn(transfer3, active)

    def test_pause_transfer(self):
        """Test pausing a transfer"""
        self.file_manager.add_transfer(self.filename, self.peer_ip, self.size)

        self.file_manager.pause_transfer(self.filename, self.peer_ip)

        key = (self.filename, self.peer_ip)
        transfer = self.file_manager.transfers[key]
        self.assertTrue(transfer.paused)
        self.assertEqual(transfer.status, "Paused")

    def test_pause_nonexistent_transfer(self):
        """Test pausing a nonexistent transfer"""
        # Should not raise an error
        self.file_manager.pause_transfer("nonexistent.txt", "192.168.1.100")

    def test_resume_transfer(self):
        """Test resuming a transfer"""
        self.file_manager.add_transfer(self.filename, self.peer_ip, self.size)
        self.file_manager.pause_transfer(self.filename, self.peer_ip)

        self.file_manager.resume_transfer(self.filename, self.peer_ip)

        key = (self.filename, self.peer_ip)
        transfer = self.file_manager.transfers[key]
        self.assertFalse(transfer.paused)
        self.assertEqual(transfer.status, "Downloading")

    def test_resume_nonexistent_transfer(self):
        """Test resuming a nonexistent transfer"""
        # Should not raise an error
        self.file_manager.resume_transfer("nonexistent.txt", "192.168.1.100")

    def test_cancel_transfer(self):
        """Test cancelling a transfer"""
        self.file_manager.add_transfer(self.filename, self.peer_ip, self.size)

        self.file_manager.cancel_transfer(self.filename, self.peer_ip)

        key = (self.filename, self.peer_ip)
        transfer = self.file_manager.transfers[key]
        self.assertTrue(transfer.cancelled)
        self.assertEqual(transfer.status, "Cancelled")

    def test_cancel_nonexistent_transfer(self):
        """Test cancelling a nonexistent transfer"""
        # Should not raise an error
        self.file_manager.cancel_transfer("nonexistent.txt", "192.168.1.100")

    def test_update_progress(self):
        """Test updating transfer progress"""
        self.file_manager.add_transfer(self.filename, self.peer_ip, self.size)

        self.file_manager.update_progress(self.filename, self.peer_ip, 75)

        key = (self.filename, self.peer_ip)
        transfer = self.file_manager.transfers[key]
        self.assertEqual(transfer.progress, 75)
        self.assertEqual(transfer.status, "Downloading")

    def test_update_progress_nonexistent(self):
        """Test updating progress for nonexistent transfer"""
        # Should not raise an error
        self.file_manager.update_progress("nonexistent.txt", "192.168.1.100", 50)

    def test_remove_completed_transfers(self):
        """Test removing completed and cancelled transfers"""
        # Add various transfers
        transfer1 = self.file_manager.add_transfer("active.txt", self.peer_ip, self.size)
        transfer2 = self.file_manager.add_transfer("completed.txt", "192.168.1.101", 2048)
        transfer2.status = "Completed"
        transfer3 = self.file_manager.add_transfer("cancelled.txt", "192.168.1.102", 512)
        transfer3.status = "Cancelled"

        self.file_manager.remove_completed()

        # Only active transfer should remain
        self.assertEqual(len(self.file_manager.transfers), 1)
        self.assertIn(("active.txt", self.peer_ip), self.file_manager.transfers)

    def test_transfers_changed_signal(self):
        """Test that transfers_changed signal is emitted"""
        signal_emitted = False

        def signal_handler():
            nonlocal signal_emitted
            signal_emitted = True

        self.file_manager.transfers_changed.connect(signal_handler)

        # Add a transfer (should emit signal)
        self.file_manager.add_transfer(self.filename, self.peer_ip, self.size)

        self.assertTrue(signal_emitted)

    def test_thread_safety(self):
        """Test that operations are thread-safe"""
        import threading
        import time

        results = []
        results_lock = threading.Lock()
        transfer_count = 0
        count_lock = threading.Lock()

        def add_transfers(thread_id):
            nonlocal transfer_count
            for i in range(10):
                filename = f"file{thread_id}_{i}.txt"
                peer_ip = f"192.168.1.{thread_id * 10 + i}"
                transfer = self.file_manager.add_transfer(filename, peer_ip, 1024)
                with results_lock:
                    results.append(transfer.filename)
                with count_lock:
                    transfer_count += 1
                time.sleep(0.001)  # Very small delay

        # Start multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=add_transfers, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Debug output
        print(f"Transfer count: {transfer_count}")
        print(f"Results length: {len(results)}")
        print(f"FileManager transfers length: {len(self.file_manager.transfers)}")

        # Should have 30 transfers
        self.assertEqual(len(self.file_manager.transfers), 30)
        self.assertEqual(len(results), 30)
        self.assertEqual(transfer_count, 30)


if __name__ == "__main__":
    unittest.main()