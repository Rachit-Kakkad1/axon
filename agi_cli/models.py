from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class State(str, Enum):
    IDLE = "idle"
    TYPING = "typing"
    THINKING = "thinking"
    STREAMING = "streaming"
    SWITCHING = "switching"
    COMPRESSING = "compressing"
    ACTING = "acting"
    ERROR = "error"
    SUCCESS = "success"

@dataclass
class Message:
    role: Role
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_response: Optional[str] = None
    tool_call_id: Optional[str] = None

    def to_dict(self):
        d = {
            "role": self.role.value,
            "content": self.content,
            "metadata": self.metadata
        }
        if self.tool_calls: d["tool_calls"] = self.tool_calls
        if self.tool_response: d["tool_response"] = self.tool_response
        if self.tool_call_id: d["tool_call_id"] = self.tool_call_id
        return d
