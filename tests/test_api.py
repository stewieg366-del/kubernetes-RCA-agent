import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import httpx
original_init = httpx.Client.__init__

def patched_init(self, *args, **kwargs):
    if "app" in kwargs:
        kwargs.pop("app")
    original_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_init

from fastapi.testclient import TestClient
from api.main import app
from agent import graph as agent_graph

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_investigate_demo():
    # Test POST endpoint with demo_mode=True
    response = client.post("/api/investigate", json={"incident": "The frontend is returning HTTP 502 errors.", "demo_mode": True})
    assert response.status_code == 200
    
    # It's a streaming response, read lines
    lines = response.iter_lines()
    final_state = None
    for line in lines:
        if line.startswith("data: "):
            data = json.loads(line.replace("data: ", ""))
            final_state = data
            
    assert final_state is not None
    assert final_state["status"] == "ROOT_CAUSE_CONFIRMED"
    assert "Missing Kubernetes Service: payment" in final_state["root_cause"]

    # Restore the global state polluted by the endpoint to not break subsequent tests
    if hasattr(agent_graph.GeminiModelProvider, "_original_invoke"):
        agent_graph.GeminiModelProvider.invoke_with_fallback = agent_graph.GeminiModelProvider._original_invoke
    
if __name__ == "__main__":
    print("Running API tests...")
    test_health()
    test_investigate_demo()
    print("API tests passed!")
