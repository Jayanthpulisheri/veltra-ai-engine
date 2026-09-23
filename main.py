import os
import re
import json
import subprocess
from dotenv import load_dotenv
from groq import Groq

# Attempt to load json_repair for handling unescaped LLM outputs gracefully
try:
    from json_repair import repair_json
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

# Load environment variables
load_dotenv()

# Initialize Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("[Error] GROQ_API_KEY environment variable not set.")
    exit(1)

client = Groq(api_key=GROQ_API_KEY)

# Log file setup
AUDIT_LOG_FILE = "veltra_audit.log"

def log_audit(event_type: str, details: str):
    """Appends security and execution events to a local audit log."""
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(f"[{event_type}] {details}\n")

# Destructive command patterns to block
BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+\*",
    r"mkfs",
    r"dd\s+if=",
    r">:?\s*/dev/sd",
    r"cat\s+/etc/passwd",
    r"chmod\s+-R\s+777\s+/"
]

def is_command_safe(command_str: str) -> tuple[bool, str]:
    """
    Splits chained commands (&&, ;, |) and evaluates each sub-command 
    against blocked regex security patterns.
    """
    sub_commands = re.split(r'&&|;|\|', command_str)
    for sub_cmd in sub_commands:
        clean_cmd = sub_cmd.strip()
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, clean_cmd, re.IGNORECASE):
                return False, clean_cmd
    return True, ""

def execute_shell_command(command_str: str) -> str:
    """Executes validated shell commands securely via subprocess."""
    try:
        result = subprocess.run(
            command_str,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        output = result.stdout if result.stdout else result.stderr
        return output.strip() if output else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "[Error] Command execution timed out after 15 seconds."
    except Exception as e:
        return f"[Error] Subprocess execution failed: {str(e)}"

SYSTEM_PROMPT = """
You are Veltra AI Engine v1.0 MVP, an autonomous execution engine.
Always respond in strict, valid JSON format using the exact schema below. Do not wrap output in markdown code blocks.

Schema:
{
  "thought": "Reasoning for the current step",
  "action": "EXECUTE_SHELL_COMMAND" | "COMPLETE",
  "command": "shell command to run (if action is EXECUTE_SHELL_COMMAND)"
}
"""

def parse_llm_json(raw_text: str) -> dict:
    """Robust JSON parser that sanitizes markdown and repairs malformed LLM outputs."""
    clean_str = raw_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_str)
    except json.JSONDecodeError as standard_err:
        if HAS_JSON_REPAIR:
            try:
                repaired = repair_json(clean_str)
                return json.loads(repaired)
            except Exception:
                pass
        raise standard_err

def run_agentic_loop(user_input: str, max_steps: int = 10):
    """Main autonomous loop running task planning, guardrail check, and execution."""
    print(f"\n[You] > {user_input}")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Task: {user_input}"}
    ]

    for step in range(1, max_steps + 1):
        print(f"\n--- [Autonomous Step {step}/{max_steps}] ---")
        
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0.1
            )
            raw_response = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Error] API Request failed: {e}")
            break

        try:
            parsed = parse_llm_json(raw_response)
        except json.JSONDecodeError as e:
            print(f"[Error] Failed to parse JSON response: {e}")
            print(f"Raw Output: {raw_response}")
            log_audit("JSON_PARSE_ERROR", f"Raw: {raw_response}")
            print("[Veltra AI] Terminating loop due to invalid JSON schema response.")
            break

        thought = parsed.get("thought", "")
        action = parsed.get("action", "")
        command = parsed.get("command", "")

        if thought:
            print(f"[Veltra Thought] > {thought}")

        if action == "COMPLETE":
            print("[Veltra AI] > Task execution completed successfully.")
            log_audit("TASK_COMPLETE", user_input)
            break

        elif action == "EXECUTE_SHELL_COMMAND":
            if not command:
                print("[Error] Action EXECUTE_SHELL_COMMAND was requested but no command was provided.")
                break

            is_safe, flagged_subcmd = is_command_safe(command)
            if not is_safe:
                error_msg = f"SECURITY_BLOCK: Intercepted destructive command containing '{flagged_subcmd}' in: {command}"
                print(f"[BLOCKED] > {error_msg}")
                log_audit("SECURITY_VIOLATION", error_msg)
                
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": f"System guardrail blocked command execution: {error_msg}"})
                break

            print(f"[Executing Command] > {command}")
            log_audit("EXECUTE_COMMAND", command)
            
            exec_output = execute_shell_command(command)
            print(f"[Output] >\n{exec_output}")

            messages.append({"role": "assistant", "content": raw_response})
            messages.append({"role": "user", "content": f"Command output:\n{exec_output}"})

        else:
            print(f"[Error] Unknown action type '{action}'. Terminating loop.")
            break

def main():
    print("=" * 65)
    print("VELTRA AI ENGINE v1.0 MVP - PROTOTYPE PRODUCTION READY")
    print("System Architecture: Autonomous Loop | Guardrails | Audit Log")
    print("=" * 65)

    if not HAS_JSON_REPAIR:
        print("[Note] Tip: Run 'pip install json-repair' for automatic JSON string healing.")

    while True:
        try:
            user_prompt = input("\n[You] > ").strip()
            if not user_prompt:
                continue
            if user_prompt.lower() in ["exit", "quit"]:
                print("Exiting Veltra AI Engine.")
                break
            run_agentic_loop(user_prompt)
        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            break
