import json
from pathlib import Path
from datetime import datetime, timezone

def generate_telemetry_report() -> dict:
    config_path = Path("veltra.config.json")
    audit_path = Path("veltra_audit.log")
    benchmark_path = Path("veltra_benchmark.json")

    total_audits = 0
    blocked_count = 0
    allowed_count = 0

    if audit_path.exists():
        with open(audit_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    total_audits += 1
                    if data.get("status") == "BLOCKED":
                        blocked_count += 1
                    elif data.get("status") == "ALLOWED":
                        allowed_count += 1
                except json.JSONDecodeError:
                    continue

    benchmark_data = {}
    if benchmark_path.exists():
        with open(benchmark_path, "r", encoding="utf-8") as f:
            benchmark_data = json.load(f)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product": "veltra-agent",
        "version": "0.1.5",
        "summary": {
            "total_intercepted_commands": total_audits,
            "allowed_executions": allowed_count,
            "blocked_security_violations": blocked_count,
            "block_rate_pct": round((blocked_count / total_audits * 100), 2) if total_audits > 0 else 0.0
        },
        "performance": benchmark_data,
        "policy_active": config_path.exists()
    }

    with open("veltra_deck_summary.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report
