import json
from pathlib import Path
from typing import List, Dict, Any

def export_audit_log(
    log_file: str = "veltra_audit.log", 
    output_file: str = "veltra_siem_export.json"
) -> Dict[str, Any]:
    """
    Parses veltra_audit.log and converts raw log entries into a 
    structured JSON payload formatted for enterprise SIEM ingestion.
    """
    log_path = Path(log_file)
    if not log_path.exists():
        return {"status": "error", "message": f"Log file '{log_file}' not found."}

    records: List[Dict[str, Any]] = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                # Attempt JSON log parsing
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Fallback for plain text log entries
                records.append({"raw_entry": line})

    export_payload = {
        "service": "veltra-agent",
        "schema_version": "1.0",
        "total_records": len(records),
        "events": records
    }

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(export_payload, out, indent=2)

    return {
        "status": "success",
        "exported_records": len(records),
        "output_file": output_file
    }
