import argparse
import json
import sys
from .graph import build_graph

def run_agent(incident: str):
    graph = build_graph()
    initial_state = {
        "incident": incident,
        "status": "INVESTIGATING",
        "hypotheses": [],
        "investigation_history": [f"Incident received: {incident}"],
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
    
    print(f"--- Starting RCA Investigation ---")
    print(f"Incident: {incident}\n")
    
    final_state = initial_state
    
    # We use stream_mode="updates" to print the discrete actions and invoke to get full state,
    # OR we can just use stream_mode="values" and track the previous iteration to know what's new.
    # Actually, tracking what changed in "values" mode is slightly annoying. 
    # Let's just use "updates" for printing and manually merge state for our local variable, 
    # OR use invoke() and just print after it finishes. 
    # For simplicity and correctness, let's use stream_mode="values" and just print the last history entry if it grew.
    
    history_len = 1
    for state in graph.stream(initial_state, stream_mode="values"):
        final_state = state
        curr_history = state.get("investigation_history", [])
        if len(curr_history) > history_len:
            # Print the newest history entries
            for i in range(history_len, len(curr_history)):
                print(curr_history[i])
            history_len = len(curr_history)
            
        if state.get("tool_calls") and state.get("next_action") == "INVESTIGATE":
            # Print tool calls only if we just planned them
            # Wait, tool_calls is part of the state, so it will print every time state is yielded if we're not careful.
            pass

    print("\n--- Final RCA Report ---")
    
    # Clean up evidence to ensure it's structured properly and handles missing timestamps
    cleaned_evidence = []
    for ev in (final_state.get("evidence") or []):
        if not isinstance(ev, dict):
            cleaned_evidence.append({"source": "unknown", "observation": str(ev), "timestamp": "Unavailable"})
            continue
        
        if "timestamp" not in ev or not ev["timestamp"]:
            ev["timestamp"] = "Unavailable"
        cleaned_evidence.append(ev)
    
    rca_json = {
        "incident": final_state.get("incident", incident),
        "status": final_state.get("status"),
        "root_cause": final_state.get("root_cause"),
        "confidence": final_state.get("confidence"),
        "timeline": final_state.get("investigation_history"),
        "observed_facts": final_state.get("observed_facts"),
        "hypotheses": final_state.get("hypotheses"),
        "evidence": cleaned_evidence,
        "alternative_explanations": final_state.get("alternative_explanations"),
        "uncertainty": final_state.get("uncertainties"),
        "investigation_history": final_state.get("investigation_history")
    }
    
    print(json.dumps(rca_json, indent=2))
    
    print("\n[Human Readable Summary]")
    print(f"Status: {rca_json['status']} (Confidence: {rca_json['confidence']})")
    print(f"Root Cause: {rca_json['root_cause']}")
    print("Observed Facts:")
    for f in (rca_json['observed_facts'] or []):
        print(f"  - {f}")
    if rca_json['alternative_explanations']:
        print("Alternative Explanations:")
        for a in rca_json['alternative_explanations']:
            print(f"  - {a}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Kubernetes RCA Agent")
    parser.add_argument("--incident", type=str, required=True, help="Incident description")
    args = parser.parse_args()
    run_agent(args.incident)
