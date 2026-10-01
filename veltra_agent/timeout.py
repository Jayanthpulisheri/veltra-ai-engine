import subprocess
import sys
from typing import List, Tuple

def execute_with_timeout(cmd_args: List[str], timeout_seconds: int = 30) -> Tuple[int, str, str]:
    """
    Executes a command under a strict time limit. If execution exceeds 
    timeout_seconds, the process is forcefully terminated.
    """
    try:
        process = subprocess.run(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds
        )
        return process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        return (
            124, 
            "", 
            f"[veltra] TIMEOUT EXCEEDED: Process forcefully terminated after exceeding {timeout_seconds} seconds threshold."
        )
