import re
from typing import Dict, Any, List
from .state import AgentState, ReplaceList

def normalize_evidence(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []
    for ev in evidence:
        sig = f"{ev.get('source')}:{ev.get('type')}:{ev.get('resource')}:{ev.get('observation')}"
        if sig not in seen:
            seen.add(sig)
            deduped.append(ev)
    return deduped

def clean_fact(fact: str) -> str:
    split_match = re.split(r'\s+(due to|caused by|because of|resulting in)\s+', fact, flags=re.IGNORECASE)
    if len(split_match) > 1:
        return split_match[0].strip()
    return fact.strip()

def normalize_facts(facts: List[str]) -> List[str]:
    seen = set()
    deduped = []
    for f in facts:
        cf = clean_fact(f)
        cf_lower = cf.lower()
        if cf_lower not in seen and cf:
            seen.add(cf_lower)
            deduped.append(cf)
    return deduped

def normalize_history(history: List[str]) -> List[str]:
    cleaned = []
    current_tools = []
    
    for h in history:
        if h.startswith("Called "):
            parts = h.split(" with args ")
            tool_name = parts[0].replace("Called ", "").strip()
            if tool_name not in current_tools:
                current_tools.append(tool_name)
        else:
            if current_tools:
                cleaned.append(f"Tools executed: {', '.join(current_tools)}")
                current_tools = []
            if not cleaned or h != cleaned[-1]:
                cleaned.append(h)
                
    if current_tools:
        cleaned.append(f"Tools executed: {', '.join(current_tools)}")
        
    return cleaned

def normalize_node(state: AgentState) -> Dict[str, Any]:
    new_evidence = normalize_evidence(state.get("evidence", []))
    new_facts = normalize_facts(state.get("observed_facts", []))
    
    # Preserve uncertainties but deduplicate
    seen_unc = set()
    deduped_unc = []
    for u in state.get("uncertainties", []):
        if u.lower() not in seen_unc:
            seen_unc.add(u.lower())
            deduped_unc.append(u)
            
    # Preserve alternatives but deduplicate. Do not blindly mark as ruled out.
    seen_alts = set()
    deduped_alts = []
    for a in state.get("alternative_explanations", []):
        if a.lower() not in seen_alts:
            seen_alts.add(a.lower())
            deduped_alts.append(a)
    
    new_history = normalize_history(state.get("investigation_history", []))
    
    return {
        "evidence": ReplaceList(new_evidence),
        "observed_facts": ReplaceList(new_facts),
        "uncertainties": ReplaceList(deduped_unc),
        "alternative_explanations": ReplaceList(deduped_alts),
        "investigation_history": ReplaceList(new_history)
    }
