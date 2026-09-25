import json
import subprocess
from guardrails import is_command_safe, log_audit_event

def execute_agent_command(command: str):
    print(f"\n[AGENT REQUEST] Executing: '{command}'")
    
    # 1. Deterministic Security Interception
    is_safe, reason = is_command_safe(command)
    if not is_safe:
        print(f"❌ {reason}")
        return {"status": "SECURITY_VIOLATION", "error": reason}
        
    # 2. Subprocess Execution
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        output_str = result.stdout.strip() if result.stdout else "Command completed (no output)"
        print(f"✅ [EXECUTED] Output: {output_str}")
        return {"status": "SUCCESS", "output": output_str}
        
    except Exception as e:
        error_msg = f"Execution Error: {str(e)}"
        log_audit_event(command, status="ERROR", reason=error_msg)
        print(f"⚠️ {error_msg}")
        return {"status": "ERROR", "error": error_msg}

if __name__ == "__main__":
    print("--- STARTING VELTRA AI EXECUTION ENGINE ---")
    
    # Safe commands
    execute_agent_command("echo 'Veltra Guardrail Active'")
    execute_agent_command("git status")
    
    # Unsafe command (Blocked by interceptor)
    execute_agent_command("echo 'hello' && rm -rf /tmp/test_dir")
