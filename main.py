import os
import json
import subprocess
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing in .env!")

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """You are Veltra AI, an enterprise-grade autonomous software and VFX execution engine.
You accomplish multi-step technical workflows, system administration, code generation, and media asset production cleanly and safely.

You operate in an autonomous loop using valid JSON actions:

1. Execute Shell Command:
{"action": "COMMAND", "command": "bash_command", "thought": "reasoning"}

2. Write/Overwrite File:
{"action": "FILE_WRITE", "filepath": "path/to/file", "content": "file_content", "thought": "reasoning"}

3. Chat Response to User:
{"action": "CHAT", "message": "message_text", "thought": "reasoning"}

4. Complete Task:
{"action": "COMPLETE", "summary": "final_summary", "thought": "reasoning"}

OUTPUT FORMAT RULE: Provide ONLY valid raw JSON without markdown code blocks."""

print("=" * 60)
print("   VELTRA AI ENGINE v1.0 MVP - PROTOTYPE PRODUCTION READY")
print("   System Architecture: Autonomous Loop | Guardrails | Audit Log")
print("=" * 60 + "\n")


def log_audit(entry):
    entry["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("veltra_audit.log", "a") as log_file:
        log_file.write(json.dumps(entry) + "\n")


def is_safe_command(cmd):
    dangerous_patterns = ["rm -rf /", "mkfs", "dd if=", ":(){:|:&};:"]
    return not any(p in cmd for p in dangerous_patterns)


def parse_and_execute(response_text):
    try:
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        data = json.loads(clean_text.strip())
        action = data.get("action")
        thought = data.get("thought", "No thought provided.")

        print(f"\n[Veltra Thought] > {thought}")
        log_audit({"action": action, "thought": thought})

        if action == "CHAT":
            msg = data.get("message")
            print(f"[Veltra AI] > {msg}")
            return "USER_INPUT_REQUIRED", None

        elif action == "COMPLETE":
            summary = data.get("summary")
            print(f"\n[Task Complete] > {summary}")
            log_audit({"status": "COMPLETE", "summary": summary})
            return "FINISHED", None

        elif action == "COMMAND":
            cmd = data.get("command")
            if not is_safe_command(cmd):
                print(f"[Safety Sandbox Violation] > Blocked dangerous command: {cmd}")
                log_audit({"status": "BLOCKED", "command": cmd})
                return (
                    "CONTINUE",
                    f'Security Alert: Command "{cmd}" blocked by execution guardrails.',
                )

            print(f"[Action: Command] > {cmd}")
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            output = (
                result.stdout or result.stderr or "Command completed with no output."
            )
            print(f"[Execution Output] >\n{output.strip()}")
            log_audit({"status": "EXECUTED", "command": cmd, "output": output.strip()})
            return "CONTINUE", f"System Output:\n{output.strip()}"

        elif action == "FILE_WRITE":
            filepath = data.get("filepath")
            content = data.get("content")
            print(f"[Action: Writing File] > {filepath}")
            with open(filepath, "w") as f:
                f.write(content)
            print(f"[File Status] > Successfully written: {filepath}")
            log_audit({"status": "FILE_WRITE", "filepath": filepath})
            return "CONTINUE", f"File written successfully: {filepath}"

        else:
            print(f"\n[Veltra AI] > {response_text}")
            return "USER_INPUT_REQUIRED", None

    except Exception as e:
        print(f"\n[Error] > {e}")
        log_audit({"status": "ERROR", "error": str(e)})
        return (
            "CONTINUE",
            f"System Alert: Response parsing error ({e}). Respond ONLY in valid JSON.",
        )


while True:
    user_input = input("\n[You] > ")
    if user_input.lower().strip() in ["exit", "quit"]:
        print("Shutting down Veltra AI Engine...")
        break

    if not user_input.strip():
        continue

    conversation_history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    step_count = 0
    max_steps = 10

    while step_count < max_steps:
        step_count += 1
        print(f"\n--- [Autonomous Step {step_count}/{max_steps}] ---")

        try:
            response = client.chat.completions.create(
                messages=conversation_history,
                model="qwen/qwen3.8-27b",
                max_tokens=500,
            )

            bot_reply = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": bot_reply})

            status, feedback = parse_and_execute(bot_reply)

            if status in ["USER_INPUT_REQUIRED", "FINISHED"]:
                break

            if feedback:
                conversation_history.append({"role": "system", "content": feedback})

        except Exception as e:
            print(f"\n[API Exception] > {e}")
            break
