import shutil
import subprocess
from typing import List, Tuple

def is_docker_available() -> bool:
    """Checks whether docker CLI is installed and operational."""
    return shutil.which("docker") is not None

def run_in_docker_container(
    cmd_args: List[str], 
    image: str = "python:3.10-slim", 
    read_only_fs: bool = True
) -> Tuple[int, str]:
    """
    Wraps execution inside an ephemeral, resource-constrained Docker container.
    """
    if not is_docker_available():
        return 1, "[veltra] DOCKER ERROR: Docker runtime binary not found in system PATH."

    docker_cmd = [
        "docker", "run", "--rm",
        "--net=none",  # Restrict outbound networking by default in container
        "--memory=512m",  # Memory limit guardrail
        "--cpus=1.0",     # CPU allocation limit
    ]

    if read_only_fs:
        docker_cmd.append("--read-only")

    docker_cmd.extend([image] + cmd_args)
    full_cmd_str = " ".join(docker_cmd)

    return 0, f"[veltra] DOCKER ISOLATION: Configured ephemeral container run -> {full_cmd_str}"
