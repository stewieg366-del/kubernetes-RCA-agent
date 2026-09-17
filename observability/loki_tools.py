import subprocess
import json
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Evidence

def query_loki(query: str, limit: int = 10):
    if len(query) > 500:
        raise ValueError("Query exceeds length limit.")
    if limit > 50:
        raise ValueError("Result limit cannot exceed 50.")
        
    encoded_query = urllib.parse.quote(query)
    path = f"/api/v1/namespaces/observability/services/loki:3100/proxy/loki/api/v1/query_range?query={encoded_query}&limit={limit}"
    
    try:
        out = subprocess.check_output(["kubectl", "get", "--raw", path], stderr=subprocess.DEVNULL)
        data = json.loads(out)
        results = data.get("data", {}).get("result", [])
        
        # Logs are untrusted data. We encapsulate them in evidence safely.
        # Format for Loki: [ { "stream": {...labels...}, "values": [ [timestamp, "log_line"], ... ] } ]
        logs_extracted = []
        for r in results:
            for val in r.get("values", []):
                logs_extracted.append(val[1])
                
        return Evidence(
            source="loki",
            type="log_query",
            resource=query,
            observation=f"Returned {len(logs_extracted)} log lines",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"logs": logs_extracted}
        )
    except Exception as e:
        return Evidence(
            source="loki",
            type="log_query",
            resource=query,
            observation="Error querying Loki",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"error": str(e)}
        )
