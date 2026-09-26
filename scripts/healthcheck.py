#!/usr/bin/env python3

import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


target_url = os.environ.get("TARGET_URL")

if not target_url:
    print("ERROR: TARGET_URL is not set.", fule=sys.stderr)
    sys.exit(2)

timeout = float(os.environ.get("TIMEOUT_SECONDS", "5"))

result = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "url": target_url,
    "service_status": "DOWN",
    "http_status": None,
    "response_time_ms": None,
    "error": None,
}

start = time.perf_counter()

try:
    request = Request(
        target_url,
        headers={"User-Agent": "infrastructure-operations-lab/1.0"},
    )

    with urlopen(request, timeout=timeout) as response:
        result["http_status"] = response.status
        result["response_time_ms"] = round(
            (time.perf_counter() - start) * 1000, 2
        )

        if response.status == 200:
            result["service_status"] = "UP"

except HTTPError as error:
    result["http_status"] = error.code
    result["response_time_ms"] = round(
            (time.perf_counter() - start) * 1000, 2
    )
    result["error"] = str(error)

except (URLError, TimeoutError) as error:
    result["error"] = str(error)

print(json.dumps(result, ensure_ascii=False))

sys.exit(0 if result["service_status"] == "UP" else 1)
