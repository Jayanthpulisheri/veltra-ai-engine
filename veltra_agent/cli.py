import sys
import subprocess
from veltra_agent.guardrail import is_command_safe

def main():
    if len(sys.argv) < 2:
        print("Usage: veltra <command_to_run>")
        print("Example: veltra \"git status\"")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    print(f"[VELTRA INTERCEPTOR] Checking command: '{command}'")

    is_safe, reason = is_command_safe(command)
    if not is_safe:
        print(f"❌ SECURITY VIOLATION: {reason}")
        sys.exit(1)

    print("✅ Passed security checks. Executing command...")
    result = subprocess.run(command, shell=True)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
