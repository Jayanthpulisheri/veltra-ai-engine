import json
import subprocess
import re
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Veltra AI Security Engine", version="1.0.0")

# Valid API key set for authentication
VALID_API_KEYS = {"demo_key_xyz"}


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Veltra AI Security Engine"}


@app.get("/api/v1/scan")
def scan_get():
    return {
        "status": "active",
        "message": (
            "Veltra Scan Endpoint is Live. Use POST with 'X-API-Key' header"
            " and a command payload to run security scans."
        ),
    }


@app.post("/api/v1/scan")
def scan_post(payload: dict, x_api_key: str = Header(None)):
    # 1. Validate API Key
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )

    # 2. Extract command string
    target_command = payload.get("command") or payload.get("cmd")
    if not target_command:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No command provided in request payload.",
        )

    # 3. Security Check Pattern Matching
    is_violation = bool(re.search(r"rm\s+-rf", target_command, re.IGNORECASE))

    if is_violation:
        return {
            "status": "completed",
            "result": {
                "status": "SECURITY_VIOLATION",
                "error": (
                    "Blocked by Veltra Guardrail: Matches forbidden pattern"
                    " 'rm -rf'"
                ),
            },
        }

    return {"status": "completed", "result": {"status": "ALLOWED"}}