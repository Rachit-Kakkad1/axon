from typing import List, Iterable
import os
from agi_cli.adapters.base import BaseAdapter
from agi_cli.models import Message, Role

from agi_cli.auth import load_creds, is_logged_in

class GeminiAdapter(BaseAdapter):
    def __init__(self, model_id: str = "gemini-1.5-flash"):
        self._model_id = model_id
        self.model = None
        
        try:
            if is_logged_in():
                import google.generativeai as genai
                creds = load_creds()
                genai.configure(credentials=creds)
                self.model = genai.GenerativeModel(model_id)
        except Exception as e:
            # Fallback to API Key if OAuth fails or client_secret is missing
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_id)

    def generate_response(self, messages: List[Message], stream: bool = False) -> Iterable[str]:
        if not self.model:
            yield f"[Gemini {self._model_id} - UNAUTHORIZED] Please run 'python -m agi_cli.main login' or set GEMINI_API_KEY."
            return

        # Convert our standard Messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg.role == Role.USER else "model"
            # Gemini system instructions are usually passed separately, 
            # but for simplicity we'll handle them as model turns or skip
            if msg.role == Role.SYSTEM:
                contents.append({"role": "user", "parts": [f"System Instruction: {msg.content}"]})
                contents.append({"role": "model", "parts": ["Acknowledged."]})
            else:
                contents.append({"role": role, "parts": [msg.content]})

        response = self.model.generate_content(contents, stream=stream)
        
        if stream:
            for chunk in response:
                yield chunk.text
        else:
            yield response.text

    def get_token_count(self, messages: List[Message]) -> int:
        # Placeholder estimation
        return sum(len(m.content) // 4 for m in messages)

    @property
    def model_name(self) -> str:
        return self._model_id

    @property
    def context_limit(self) -> int:
        return 1000000 # 1M for Gemini 1.5 Flash
