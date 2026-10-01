import unittest
import json
import subprocess
import sys
from pathlib import Path

class TestVeltraIntegration(unittest.TestCase):

    def test_01_init_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "init", "--force"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(Path("veltra.config.json").exists())

    def test_02_allowed_run_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "run", "--", "echo", "Integration Test"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Policy verified", result.stdout)

    def test_03_blocked_run_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "run", "--", "rm", "-rf", "/"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("SECURITY VIOLATION", result.stderr)

    def test_04_network_port_guardrail(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "run", "--", "nc", "-p", "8080", "127.0.0.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("NETWORK SECURITY VIOLATION", result.stderr)

    def test_05_filesystem_sandbox(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "run", "--", "echo 'data' > /etc/config"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("FILESYSTEM VIOLATION", result.stderr)

    def test_06_environment_leak_protection(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "run", "--", "echo $OPENAI_API_KEY"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("ENVIRONMENT LEAK VIOLATION", result.stderr)

    def test_07_process_timeout(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "run", "--timeout", "1", "--", "sleep", "3"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 124)
        self.assertIn("TIMEOUT EXCEEDED", result.stderr)

    def test_08_benchmark_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "benchmark", "-i", "5"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(Path("veltra_benchmark.json").exists())

    def test_09_export_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "veltra_agent.cli", "export"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(Path("veltra_deck_summary.json").exists())

if __name__ == "__main__":
    unittest.main()
