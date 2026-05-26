from typing import List, Iterable, Optional, List, Any
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

    def _ensure_model(self, tools: Optional[List[Any]] = None):
        """Lazy initialization of the Gemini model with optional tool support."""
        if self.model and not tools:
            return True
            
        try:
            if is_logged_in():
                import google.generativeai as genai
                creds = load_creds()
                genai.configure(credentials=creds)
                # Pass tools if provided
                self.model = genai.GenerativeModel(self._model_id, tools=tools)
                return True
        except Exception:
            pass
            
        # Fallback to API Key
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self._model_id, tools=tools)
            return True
            
        return False

    def generate_response(self, messages: List[Message], stream: bool = False, tools: Optional[List[Any]] = None) -> Iterable[str]:
        if not self._ensure_model(tools=tools):
            yield f"[Gemini {self._model_id} - UNAUTHORIZED] Please run 'python -m agi_cli.main login' or set GEMINI_API_KEY."
            return

        # Convert our standard Messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg.role == Role.USER else "model"
            
            parts = []
            if msg.content:
                parts.append(msg.content)
            
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    # Map to Gemini tool call format
                    parts.append(tc) # Simplified for now, assuming adapter receives correct objects
            
            if msg.tool_response:
                # Gemini tool responses use a specific role or part
                role = "function" # This is a conceptual mapping, Gemini SDK uses specific response objects
                parts.append(msg.tool_response)

            contents.append({"role": role, "parts": parts})

        # Tool-use often requires non-streaming for the final decision
        # but the SDK supports streaming text + function calls
        response = self.model.generate_content(contents, stream=stream)
        
        if stream:
            for chunk in response:
                if chunk.candidates[0].content.parts:
                    for part in chunk.candidates[0].content.parts:
                        if hasattr(part, "text"):
                            yield part.text
                        elif hasattr(part, "function_call"):
                            # Yield function call as a special string or handle in orchestrator
                            yield f"__TOOL_CALL__:{part.function_call.name}:{part.function_call.args}"
        else:
            # Handle non-streaming candidate
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
