from typing import List, Iterable
from agi_cli.adapters.base import BaseAdapter
from agi_cli.models import Message

class ClaudeAdapter(BaseAdapter):
    def __init__(self, model_id: str = "claude-3-5-sonnet"):
        self._model_id = model_id

    def generate_response(self, messages: List[Message], stream: bool = False) -> Iterable[str]:
        # Mock implementation
        last_msg = messages[-1].content if messages else "nothing"
        yield f"[Claude {self._model_id}] (Fallback) Hello! I've taken over with the same context. You just said: {last_msg}"

    def get_token_count(self, messages: List[Message]) -> int:
        return sum(len(m.content) // 4 for m in messages)

    @property
    def model_name(self) -> str:
        return self._model_id

    @property
    def context_limit(self) -> int:
        return 200000
