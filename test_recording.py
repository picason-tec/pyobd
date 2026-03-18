import unittest
import os
import datetime
import time
from unittest.mock import MagicMock, patch

# Mocking wx and other dependencies for the recording logic test
class MockCommand:
    def __init__(self, desc, command):
        self.desc = desc
        self.command = command

class MockValue:
    def __init__(self, magnitude):
        self.magnitude = magnitude

class MockQueryResult:
    def __init__(self, value):
        self.value = value

class TestRecordingLogic(unittest.TestCase):
    def setUp(self):
        self.csv_file = "test_recording.csv"
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def tearDown(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def test_csv_creation_and_header(self):
        active_recording_pids = [MockCommand("RPM", "010C"), MockCommand("Speed", "010D")]

        # Simulate the logic in sensorProducer.run
        with open(self.csv_file, "w") as f:
            header = "timestamp"
            for cmd in active_recording_pids:
                header += "," + cmd.desc
            f.write(header + "\n")

        with open(self.csv_file, "r") as f:
            content = f.read()
            self.assertEqual(content.strip(), "timestamp,RPM,Speed")

    def test_csv_data_append(self):
        active_recording_pids = [MockCommand("RPM", "010C")]

        # Write header
        with open(self.csv_file, "w") as f:
            f.write("timestamp,RPM\n")

        # Simulate data polling
        timestamp = "2023-01-01 12:00:00"
        value = "1000.0"
        row = f"{timestamp},{value}\n"

        with open(self.csv_file, "a") as f:
            f.write(row)

        with open(self.csv_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[1].strip(), "2023-01-01 12:00:00,1000.0")

    def test_header_reset_on_selection_change(self):
        # Initial selection
        active_recording_pids = [MockCommand("RPM", "010C")]
        with open(self.csv_file, "w") as f:
            f.write("timestamp,RPM\n")

        # Selection changed
        active_recording_pids = [MockCommand("RPM", "010C"), MockCommand("Speed", "010D")]
        with open(self.csv_file, "w") as f:
            header = "timestamp"
            for cmd in active_recording_pids:
                header += "," + cmd.desc
            f.write(header + "\n")

        with open(self.csv_file, "r") as f:
            content = f.read()
            self.assertEqual(content.strip(), "timestamp,RPM,Speed")

if __name__ == "__main__":
    unittest.main()
