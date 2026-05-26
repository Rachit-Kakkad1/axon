from abc import ABC, abstractmethod
from typing import List, Iterable
from agi_cli.models import Message

class BaseAdapter(ABC):
    @abstractmethod
    def generate_response(self, messages: List[Message], stream: bool = False) -> Iterable[str]:
        """
        Generates a response from the AI model.
        Should return an iterable of strings (for streaming support).
        """
        pass

    @abstractmethod
    def get_token_count(self, messages: List[Message]) -> int:
        """
        Estimates the token count for the given messages.
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def context_limit(self) -> int:
        pass
