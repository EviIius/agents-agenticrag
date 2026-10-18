"""One direct oracle-evidence answer through the same admitted local proxy."""

import json
import sys
import urllib.request
from pathlib import Path

settings = json.loads(Path(sys.argv[1]).read_text())
body = {
    "model": settings["model"],
    "stream": True,
    "options": {"num_ctx": 65536},
    "messages": [
        {"role": "system", "content": settings["system_prompt"]},
        {"role": "user", "content": settings["question"]},
    ],
}
request = urllib.request.Request(
    f"http://127.0.0.1:{settings['port']}/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"},
)
answer = ""
with urllib.request.urlopen(request, timeout=180) as response:
    for raw in response:
        if raw.startswith(b"data: ") and raw.strip() != b"data: [DONE]":
            data = json.loads(raw[6:])
            for choice in data.get("choices", []):
                answer += choice.get("delta", {}).get("content") or ""
Path(settings["trial_dir"], "worker-result.json").write_text(
    json.dumps({"final_response": answer}, indent=2) + "\n"
)
