import unittest
import os
import datetime
from unittest.mock import MagicMock

class MockCommand:
    def __init__(self, desc, command):
        self.desc = desc
        self.command = command

class TestImprovedRecordingLogic(unittest.TestCase):
    def setUp(self):
        self.csv_file = "test_improved_recording.csv"
        self.recorded_pids_shared = []
        self.active_recording_pids = []
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def tearDown(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def simulate_loop_iteration(self, recorded_pids, query_mock):
        # Replicating logic from pyobd.py sensorProducer.run
        selected_commands = recorded_pids
        if selected_commands != self.active_recording_pids:
            self.active_recording_pids = list(selected_commands)
            if self.active_recording_pids:
                try:
                    with open(self.csv_file, "w") as f:
                        header = "timestamp"
                        for cmd in self.active_recording_pids:
                            header += "," + cmd.desc
                        f.write(header + "\n")
                except Exception as e:
                    pass

        if self.active_recording_pids:
            row = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for cmd in self.active_recording_pids:
                r = query_mock(cmd)
                val = str(r.value.magnitude) if hasattr(r.value, 'magnitude') else str(r.value)
                row += "," + val
            try:
                with open(self.csv_file, "a") as f:
                    f.write(row + "\n")
            except Exception as e:
                pass

    def test_caching_and_recording(self):
        cmd1 = MockCommand("RPM", "010C")
        query_mock = MagicMock()
        query_mock.return_value.value.magnitude = 1000

        # Iteration 1
        self.simulate_loop_iteration([cmd1], query_mock)
        self.assertTrue(os.path.exists(self.csv_file))
        with open(self.csv_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(lines[0].strip(), "timestamp,RPM")
            self.assertIn("1000", lines[1])

        # Iteration 2 (no change)
        query_mock.return_value.value.magnitude = 1100
        self.simulate_loop_iteration([cmd1], query_mock)
        with open(self.csv_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 3)
            self.assertIn("1100", lines[2])

        # Iteration 3 (change selection -> reset)
        cmd2 = MockCommand("Speed", "010D")
        query_mock.return_value.value.magnitude = 50
        self.simulate_loop_iteration([cmd1, cmd2], query_mock)
        with open(self.csv_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(lines[0].strip(), "timestamp,RPM,Speed")
            self.assertEqual(len(lines), 2)
            self.assertIn("50,50", lines[1])

if __name__ == "__main__":
    unittest.main()
