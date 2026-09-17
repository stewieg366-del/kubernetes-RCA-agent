import subprocess
import json
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Evidence

def query_prometheus(query: str):
    if len(query) > 500:
        raise ValueError("Query exceeds length limit.")
    
    encoded_query = urllib.parse.quote(query)
    path = f"/api/v1/namespaces/observability/services/prometheus:9090/proxy/api/v1/query?query={encoded_query}"
    
    try:
        out = subprocess.check_output(["kubectl", "get", "--raw", path], stderr=subprocess.DEVNULL)
        data = json.loads(out)
        results = data.get("data", {}).get("result", [])
        return Evidence(
            source="prometheus",
            type="metric_query",
            resource=query,
            observation=f"Returned {len(results)} results",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"results": results[:10]} # Limit to first 10 for safety
        )
    except Exception as e:
        return Evidence(
            source="prometheus",
            type="metric_query",
            resource=query,
            observation="Error querying Prometheus",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"error": str(e)}
        )

def query_prometheus_range(query: str, start: str, end: str, step: str = "15s"):
    if len(query) > 500:
        raise ValueError("Query exceeds length limit.")
        
    encoded_query = urllib.parse.quote(query)
    path = f"/api/v1/namespaces/observability/services/prometheus:9090/proxy/api/v1/query_range?query={encoded_query}&start={start}&end={end}&step={step}"
    
    try:
        out = subprocess.check_output(["kubectl", "get", "--raw", path], stderr=subprocess.DEVNULL)
        data = json.loads(out)
        results = data.get("data", {}).get("result", [])
        return Evidence(
            source="prometheus",
            type="metric_query_range",
            resource=query,
            observation=f"Returned {len(results)} results",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"results": results[:10]}
        )
    except Exception as e:
        return Evidence(
            source="prometheus",
            type="metric_query_range",
            resource=query,
            observation="Error querying Prometheus range",
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            metadata={"error": str(e)}
        )
