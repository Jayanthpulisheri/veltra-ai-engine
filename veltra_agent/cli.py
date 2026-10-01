import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional
from veltra_agent.config import init_config
from veltra_agent.logger import log_event
from veltra_agent.benchmark import run_benchmark
from veltra_agent.telemetry import generate_telemetry_report
from veltra_agent.network import inspect_network_rules
from veltra_agent.sandbox import inspect_filesystem_rules
from veltra_agent.sanitizer import inspect_environment_leak
from veltra_agent.streamer import run_command_async
from veltra_agent.watcher import PolicyHotReloader
from veltra_agent.docker_adapter import run_in_docker_container
from veltra_agent.exporter import export_audit_log

def main(args: Optional[List[str]] = None) -> None:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="veltra",
        description="Veltra AI - Deterministic Guardrail for Autonomous AI Agents",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 'init' subcommand
    parser_init = subparsers.add_parser("init", help="Initialize Veltra configuration in workspace")
    parser_init.add_argument("--force", "-f", action="store_true", help="Overwrite existing configuration")

    # 'run' subcommand
    parser_run = subparsers.add_parser("run", help="Run a command under the Veltra agent guardrail")
    parser_run.add_argument("--timeout", "-t", type=int, default=None, help="Override subprocess timeout in seconds")
    parser_run.add_argument("--container", "-c", action="store_true", help="Isolate execution inside ephemeral Docker container")
    parser_run.add_argument("cmd_args", nargs=argparse.REMAINDER, help="Command and arguments to execute")

    # 'benchmark' subcommand
    parser_bench = subparsers.add_parser("benchmark", help="Run performance benchmark on guardrail latency")
    parser_bench.add_argument("--iterations", "-i", type=int, default=50, help="Number of benchmark iterations")

    # 'export' subcommand
    parser_export = subparsers.add_parser("export", help="Export telemetry and SIEM audit log summary")

    parsed = parser.parse_args(args)

    if parsed.command == "init":
        msg = init_config(force=parsed.force)
        print(msg)
    elif parsed.command == "benchmark":
        run_benchmark(iterations=parsed.iterations)
    elif parsed.command == "export":
        report = generate_telemetry_report()
        siem_res = export_audit_log()
        print("[veltra] Telemetry report exported to 'veltra_deck_summary.json'")
        print(f"[veltra] SIEM Audit payload exported: {siem_res}")
    elif parsed.command == "run":
        cmd = parsed.cmd_args
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        if not cmd:
            print("[veltra] Error: No command provided to run.", file=sys.stderr)
            sys.exit(1)
            
        reloader = PolicyHotReloader()
        config = reloader.cached_config

        logging_cfg = config.get("logging", {})
        log_enabled = logging_cfg.get("enabled", True)
        log_file = logging_cfg.get("log_file", "veltra_audit.log")
        
        guardrails = config.get("guardrails", {})
        blocked_commands = guardrails.get("blocked_commands", [])
        allowed_ports = guardrails.get("allowed_outbound_ports", [80, 443])
        read_only_root = guardrails.get("enforce_read_only_root", True)
        default_timeout = guardrails.get("max_subprocess_timeout_seconds", 5)
        
        timeout_val = parsed.timeout if parsed.timeout is not None else default_timeout
        full_cmd_str = " ".join(cmd)
        
        # Security Guardrail Checks
        if any(blocked in full_cmd_str for blocked in blocked_commands):
            if log_enabled:
                log_event(full_cmd_str, "BLOCKED", reason="Matched blocked command list", log_file=log_file)
            print(f"[veltra] SECURITY VIOLATION: Command '{full_cmd_str}' blocked by policy engine.", file=sys.stderr)
            sys.exit(1)

        net_passed, net_reason = inspect_network_rules(full_cmd_str, allowed_ports)
        if not net_passed:
            if log_enabled:
                log_event(full_cmd_str, "BLOCKED", reason=net_reason, log_file=log_file)
            print(f"[veltra] NETWORK SECURITY VIOLATION: {net_reason}", file=sys.stderr)
            sys.exit(1)

        fs_passed, fs_reason = inspect_filesystem_rules(full_cmd_str, read_only_root)
        if not fs_passed:
            if log_enabled:
                log_event(full_cmd_str, "BLOCKED", reason=fs_reason, log_file=log_file)
            print(f"[veltra] FILESYSTEM VIOLATION: {fs_reason}", file=sys.stderr)
            sys.exit(1)

        env_passed, env_reason = inspect_environment_leak(full_cmd_str)
        if not env_passed:
            if log_enabled:
                log_event(full_cmd_str, "BLOCKED", reason=env_reason, log_file=log_file)
            print(f"[veltra] ENVIRONMENT LEAK VIOLATION: {env_reason}", file=sys.stderr)
            sys.exit(1)

        if parsed.container:
            code, msg = run_in_docker_container(cmd, read_only_fs=read_only_root)
            print(msg)
            if log_enabled:
                log_event(full_cmd_str, "CONTAINER_ISOLATED", reason="Executed via Docker container adapter", log_file=log_file)
            sys.exit(code)

        if log_enabled:
            log_event(full_cmd_str, "ALLOWED", reason="Passed all security guardrail inspections", log_file=log_file)

        print(f"[veltra] Policy verified. Streaming async execution (Timeout: {timeout_val}s): {full_cmd_str}")
        
        returncode, duration = asyncio.run(run_command_async(cmd, timeout_seconds=timeout_val))
        print(f"[veltra] Stream completed in {duration:.3f}s with exit code {returncode}")
        sys.exit(returncode)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
