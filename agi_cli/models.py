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
    ERROR = "error"
    SUCCESS = "success"

@dataclass
class Message:
    role: Role
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "role": self.role.value,
            "content": self.content,
            "metadata": self.metadata
        }
