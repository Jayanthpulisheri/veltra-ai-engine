import asyncio
import sys
import time
from typing import List, Tuple

async def _stream_stream(stream, color_prefix: str = ""):
    """Reads lines from an asyncio stream and prints them in real time."""
    while True:
        line = await stream.readline()
        if not line:
            break
        decoded = line.decode('utf-8', errors='replace')
        sys.stdout.write(f"{color_prefix}{decoded}")
        sys.stdout.flush()

async def run_command_async(cmd_args: List[str], timeout_seconds: int = 30) -> Tuple[int, float]:
    """
    Executes a command asynchronously, streaming I/O in real time 
    while enforcing non-blocking execution timeouts.
    """
    start_time = time.perf_counter()
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except Exception as e:
        sys.stderr.write(f"[veltra] FAILED TO LAUNCH PROCESS: {e}\n")
        return 1, 0.0

    stdout_task = asyncio.create_task(_stream_stream(process.stdout))
    stderr_task = asyncio.create_task(_stream_stream(process.stderr, color_prefix="[ERR] "))

    try:
        await asyncio.wait_for(
            asyncio.gather(process.wait(), stdout_task, stderr_task),
            timeout=timeout_seconds
        )
        duration = time.perf_counter() - start_time
        return process.returncode, duration
    except asyncio.TimeoutError:
        try:
            process.kill()
        except OSError:
            pass
        sys.stderr.write(f"\n[veltra] TIMEOUT EXCEEDED: Process killed after exceeding {timeout_seconds}s limit.\n")
        duration = time.perf_counter() - start_time
        return 124, duration
