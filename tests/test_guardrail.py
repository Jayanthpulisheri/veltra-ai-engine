import pytest
from veltra_agent.guardrail import is_command_safe

def test_safe_command():
    is_safe, _ = is_command_safe("echo 'Hello World'")
    assert is_safe is True

def test_blocked_rf():
    is_safe, reason = is_command_safe("rm -rf /")
    assert is_safe is False
    assert "forbidden pattern" in reason.lower()

def test_blocked_chaining():
    is_safe, reason = is_command_safe("ls -la && rm -rf /tmp/dir")
    assert is_safe is False
    assert "forbidden pattern" in reason.lower() or "chain" in reason.lower()
