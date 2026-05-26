from typing import List, Iterable, Optional, Tuple
from agi_cli.adapters.base import BaseAdapter
from agi_cli.memory.manager import MemoryManager
from agi_cli.models import Message, Role, State
import sys

class Orchestrator:
    def __init__(self, memory: MemoryManager, adapters: List[BaseAdapter], summary_threshold: int = 5000):
        self.memory = memory
        self.adapters = adapters
        self.current_adapter_index = 0
        self.summary_threshold = summary_threshold

    @property
    def active_adapter(self) -> BaseAdapter:
        return self.adapters[self.current_adapter_index]

    def chat(self, user_input: str) -> Iterable[Tuple[State, str]]:
        # 1. Store user message
        user_msg = Message(role=Role.USER, content=user_input)
        self.memory.add_message(user_msg)

        # 2. Check for summarization need
        history = self.memory.get_messages()
        tokens = self.active_adapter.get_token_count(history)
        if tokens > self.summary_threshold:
            yield (State.COMPRESSING, "\n[Neural Mesh Collapsing - Summarizing...]\n")
            self._summarize_history()
            history = self.memory.get_messages() # Refresh history after summary

        # 3. Try to get response from current model
        while self.current_adapter_index < len(self.adapters):
            adapter = self.active_adapter
            history = self.memory.get_messages()

            yield (State.THINKING, "")

            try:
                full_response = ""
                for chunk in adapter.generate_response(history, stream=True):
                    full_response += chunk
                    yield (State.STREAMING, chunk)

                # If successful, save assistant message and break
                assistant_msg = Message(role=Role.ASSISTANT, content=full_response)
                self.memory.add_message(assistant_msg)
                yield (State.SUCCESS, "")
                return

            except Exception as e:
                # Log error and switch to next adapter
                yield (State.SWITCHING, f"\n[Rerouting Signal: {adapter.model_name} failed. Trying next node...]\n")
                self.current_adapter_index += 1
                if self.current_adapter_index >= len(self.adapters):
                    yield (State.ERROR, f"\n[Fatal: All neural pathways exhausted.]")
                    break

    def switch_model(self, index: int):
        if 0 <= index < len(self.adapters):
            self.current_adapter_index = index

    def _summarize_history(self):
        history = self.memory.get_messages()
        # We'll keep the last 2 messages for immediate context and summarize the rest
        to_summarize = history[:-2]
        keep = history[-2:]

        if not to_summarize:
            return

        # Create a summarization prompt
        prompt = "Please provide a concise summary of the following conversation history to preserve context:\n\n"
        for msg in to_summarize:
            prompt += f"{msg.role.value}: {msg.content}\n"

        # Use the current adapter to summarize (synchronously for simplicity here)
        summary_chunks = list(self.active_adapter.generate_response([Message(role=Role.USER, content=prompt)]))
        summary_text = "".join(summary_chunks)

        # Update memory: clear all and insert summary + kept messages
        self.memory.clear_memory()
        self.memory.add_message(Message(
            role=Role.SYSTEM, 
            content=f"Summary of previous conversation: {summary_text}"
        ))
        for msg in keep:
            self.memory.add_message(msg)
