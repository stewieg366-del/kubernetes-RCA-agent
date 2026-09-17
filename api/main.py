from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys
import os
import json
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.graph import build_graph
from agent import graph as agent_graph

app = FastAPI(title="K8s RCA Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvestigateRequest(BaseModel):
    incident: str
    demo_mode: bool = False

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/investigate")
async def investigate(req: InvestigateRequest):
    # Setup mock if demo mode
    if req.demo_mode:
        os.environ["USE_MOCK_LLM"] = "true"
        # We can inject a specific deterministic mock for frontend 502
        class MockLLM:
            def __init__(self, responses):
                self.responses = responses
                self.call_count = 0
            def invoke(self, messages):
                if self.call_count < len(self.responses):
                    resp = self.responses[self.call_count]
                else:
                    resp = self.responses[-1]
                self.call_count += 1
                class MockMsg:
                    def __init__(self, c): self.content = c
                import json
                return MockMsg(json.dumps(resp))

        # A realistic sequence for Frontend 502
        responses = [
            {
                "action": "INVESTIGATE",
                "reasoning": "Check pods in rca-demo namespace to see if any are crashing.",
                "tool_calls": [{"name": "get_pods", "args": {"namespace": "rca-demo"}}]
            },
            {
                "action": "INVESTIGATE",
                "reasoning": "Check logs for the frontend pod to identify the 502 source.",
                "tool_calls": [{"name": "query_loki", "args": {"query": '{app="frontend"}'}}]
            },
            {
                "action": "INVESTIGATE",
                "reasoning": "Frontend complains about resolving 'payment'. Let's check if the payment service exists.",
                "tool_calls": [{"name": "get_service", "args": {"namespace": "rca-demo", "service_name": "payment"}}]
            },
            {
                "action": "CONCLUDE",
                "reasoning": "Payment service is missing, causing frontend 502.",
                "root_cause": "Missing Kubernetes Service: payment. The payment Deployment is healthy, but the service is missing. Therefore DNS payment.rca-demo.svc.cluster.local cannot resolve.",
                "confidence": 0.95
            }
        ]
        mock_llm = MockLLM(responses)
        if not hasattr(agent_graph.GeminiModelProvider, "_original_invoke"):
            agent_graph.GeminiModelProvider._original_invoke = agent_graph.GeminiModelProvider.invoke_with_fallback
        def patched_invoke(self, messages):
            return mock_llm.invoke(messages), {"model": "security-mock", "fallback_info": None}
        agent_graph.GeminiModelProvider.invoke_with_fallback = patched_invoke
    else:
        os.environ["USE_MOCK_LLM"] = "false"
        # Restore normal invoke_with_fallback just in case
        if hasattr(agent_graph.GeminiModelProvider, "_original_invoke"):
            agent_graph.GeminiModelProvider.invoke_with_fallback = agent_graph.GeminiModelProvider._original_invoke

    graph = build_graph()
    
    initial_state = {
        "incident": req.incident, 
        "status": "INVESTIGATING", 
        "hypotheses": ["Initial triage"],
        "investigation_history": [f"Incident received: {req.incident}"], 
        "evidence": [], 
        "observed_facts": [],
        "uncertainties": [], 
        "alternative_explanations": [], 
        "root_cause": "",
        "confidence": 0.0, 
        "iteration": 0, 
        "next_action": "", 
        "tool_calls": [],
        "total_tool_calls": 0,
        "executed_tools": []
    }

    async def event_stream():
        try:
            # Run graph in thread so it doesn't block async
            def run_graph():
                for step_state in graph.stream(initial_state, stream_mode="values"):
                    yield step_state
            
            # Since graph.stream is sync, we can just yield it iteratively.
            # Fast/mock calls will stream instantly. LLM calls will block the generator which is fine.
            for step_state in run_graph():
                # We yield the full state each time.
                # Remove sensitive environment info if we had any, though we don't put it in state.
                clean_state = dict(step_state)
                # Ensure no object causes JSON errors
                yield f"data: {json.dumps(clean_state)}\n\n"
                await asyncio.sleep(0.1) # Yield control
                
        except Exception as e:
            err = str(e)
            if "GEMINI_API_KEY" in err:
                # Mask it
                err = "Failed to initialize LLM: GEMINI_API_KEY environment variable is missing."
            yield f"data: {json.dumps({'status': 'ERROR', 'root_cause': err})}\n\n"
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")

