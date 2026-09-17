from typing_extensions import TypedDict, List, Dict, Any, Annotated
import operator

class ReplaceList(list):
    """A special list type that tells the reducer to overwrite instead of merge."""
    pass

def merge_list(a: List, b: List) -> List:
    if isinstance(b, ReplaceList):
        return list(b)
    return (a or []) + (b or [])

class AgentState(TypedDict):
    incident: str
    status: str
    hypotheses: Annotated[List[str], merge_list]
    investigation_history: Annotated[List[str], merge_list]
    evidence: Annotated[List[Dict[str, Any]], merge_list]
    observed_facts: Annotated[List[str], merge_list]
    uncertainties: Annotated[List[str], merge_list]
    alternative_explanations: Annotated[List[str], merge_list]
    root_cause: str
    confidence: float
    iteration: int
    next_action: str
    tool_calls: List[Dict[str, Any]]
    total_tool_calls: int
    executed_tools: Annotated[List[str], merge_list]
