import json
from datetime import datetime

LOG_FILE = "tool_calls.log"

def log_tool_call(function_name: str, arguments: dict, result):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "function": function_name,
        "arguments": arguments,
        "result": result
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_log_entries(limit: int = 100):
    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
            return [json.loads(line.strip()) for line in lines]
    except FileNotFoundError:
        return []
