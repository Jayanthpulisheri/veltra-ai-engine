🛡️ Veltra AI Engine

> **Microsecond Pre-Execution Security Layer for AI Agents & CLI Automation**

Veltra intercepts, inspects, and blocks malicious subshell execution payloads, prompt injection attacks, and unauthorized system tool calls before they run.

---

## ⚡ Quickstart (Python)

Protect your AI agent's tool execution loops in 3 lines of code:

```python
import requests


def validate_agent_command(command: str, api_key: str) -> bool:
    response = requests.post(
        "[https://veltra-core--veltraofficiala.replit.app/api/v1/scan](https://veltra-core--veltraofficiala.replit.app/api/v1/scan)",
        headers={"X-API-Key": api_key},
        json={"command": command},
    )
    return response.status_code == 200
🧪 Quick Test (cURL)
Run a microsecond scan directly from your terminal:

Bash
curl -X POST [https://veltra-core--veltraofficiala.replit.app/api/v1/scan](https://veltra-core--veltraofficiala.replit.app/api/v1/scan) \
  -H "X-API-Key: demo_key_xyz" \
  -H "Content-Type: application/json" \
  -d '{"command": "rm -rf /"}'
Response Example
JSON
{
  "status": "completed",
  "result": {
    "status": "SECURITY_VIOLATION",
    "error": "Blocked by Veltra Guardrail: Matches forbidden pattern 'rm\\s+-rf'"
  }
}
🌐 Endpoints & Resources
Live Documentation: https://veltra.is-a.dev

API Base: https://veltra-core--veltraofficiala.replit.app

Primary Scan Route: /api/v1/scan.
