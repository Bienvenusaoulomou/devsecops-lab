from pathlib import Path
import json
import sys

if len(sys.argv) < 6:
    print(
        "Usage: write_status.py "
        "CONTROL CATEGORY STATUS MESSAGE BLOCKING"
    )
    sys.exit(1)

control = sys.argv[1]
category = sys.argv[2]
status = sys.argv[3]
message = sys.argv[4]
blocking = sys.argv[5].lower() == "true"

output = Path("reports/status") / f"{control}.json"
output.parent.mkdir(parents=True, exist_ok=True)

data = {
    "control": control,
    "category": category,
    "status": status,
    "message": message,
    "blocking": blocking
}

output.write_text(
    json.dumps(data, indent=2),
    encoding="utf-8"
)

print(f"Status written: {output}")
