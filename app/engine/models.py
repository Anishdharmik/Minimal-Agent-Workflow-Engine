from typing import Dict, Any, Optional
from pydantic import BaseModel


class NodeDefinition(BaseModel):
    name: str
    tool_name: str
    config: Dict[str, Any] = {}


class ExecutionLogEntry(BaseModel):
   
    node: str
    state_snapshot: Dict[str, Any]
    message: Optional[str] = None
