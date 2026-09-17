from pydantic import BaseModel
from typing import Dict, Any, Optional

class Evidence(BaseModel):
    source: str
    type: str
    resource: str
    observation: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
