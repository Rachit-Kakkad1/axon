from typing import List, Iterable, Optional, Tuple, Any, Dict
from agi_cli.adapters.base import BaseAdapter
from agi_cli.memory.manager import MemoryManager
from agi_cli.models import Message, Role, State
from agi_cli.skills.manager import SkillManager, SkillConfig
from agi_cli.tools.system import ShellTool, FileTool
import sys
import json
import os

class Orchestrator:
    def __init__(self, memory: MemoryManager, adapters: List[BaseAdapter], summary_threshold: int = 5000):
        self.memory = memory
        self.adapters = adapters
        self.current_adapter_index = 0
        self.summary_threshold = summary_threshold
        self.skill_manager = SkillManager()
        self.active_skill: Optional[SkillConfig] = None
        
        # Initialize Core Intelligence Tools
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tools = {
            "execute_shell": ShellTool(project_root).execute,
            "read_file": FileTool(project_root).read_file,
            "write_file": FileTool(project_root).write_file
        }
        
        # Map tools for Gemini SDK
        self.gemini_tools = [
            {"function_declarations": [
                {
                    "name": "execute_shell",
                    "description": "Execute a terminal command in the project environment.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "command": {"type": "STRING", "description": "The shell command to run."}
                        },
                        "required": ["command"]
                    }
                },
                {
                    "name": "read_file",
                    "description": "Read the contents of a file from the workspace.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "path": {"type": "STRING", "description": "The relative path to the file."}
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "write_file",
                    "description": "Write or overwrite a file in the workspace.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "path": {"type": "STRING", "description": "The relative path to the file."},
                            "content": {"type": "STRING", "description": "The full content to write."}
                        },
                        "required": ["path", "content"]
                    }
                }
            ]}
        ]

    @property
    def active_adapter(self) -> BaseAdapter:
        return self.adapters[self.current_adapter_index]

    def chat(self, user_input: str) -> Iterable[Tuple[State, str]]:
        # 1. Skill Detection
        detected_skill = self.skill_manager.detect_skill(user_input)
        if detected_skill:
            self.active_skill = detected_skill
        
        # 2. Store user message
        user_msg = Message(role=Role.USER, content=user_input)
        self.memory.add_message(user_msg)

        # ACI Recursive Loop
        while True:
            history = self.memory.get_messages()
            
            # Context Summary Check
            tokens = self.active_adapter.get_token_count(history)
            if tokens > self.summary_threshold:
                yield (State.COMPRESSING, "\n[Neural Mesh Collapsing - Summarizing...]\n")
                self._summarize_history()
                history = self.memory.get_messages()

            if self.active_skill:
                skill_prompt = Message(role=Role.SYSTEM, content=self.active_skill.system_prompt)
                history.insert(0, skill_prompt)

            yield (State.THINKING, "")

            full_response = ""
            tool_call_found = False
            
            try:
                # Use Gemini with autonomy tools
                for chunk in self.active_adapter.generate_response(history, stream=True, tools=self.gemini_tools):
                    if chunk.startswith("__TOOL_CALL__:"):
                        tool_call_found = True
                        _, tool_name, tool_args = chunk.split(":", 2)
                        args_dict = eval(tool_args) # Safety note: In production use json.loads
                        
                        yield (State.ACTING, f"\n[ACI EXECUTION]: Running {tool_name}({args_dict})...\n")
                        
                        # Execute Tool
                        result = self.tools[tool_name](**args_dict)
                        
                        # Save Tool Call and Response to Memory
                        assistant_msg = Message(role=Role.ASSISTANT, content="", tool_calls=[{"name": tool_name, "args": args_dict}])
                        self.memory.add_message(assistant_msg)
                        
                        response_msg = Message(role=Role.USER, content=f"Result of {tool_name}: {result}")
                        self.memory.add_message(response_msg)
                        
                        # Break streaming and loop back for re-prompting with tool result
                        break
                    
                    full_response += chunk
                    yield (State.STREAMING, chunk)

                if not tool_call_found:
                    # Successful completion
                    assistant_msg = Message(role=Role.ASSISTANT, content=full_response)
                    self.memory.add_message(assistant_msg)
                    yield (State.SUCCESS, "")
                    return

            except Exception as e:
                yield (State.SWITCHING, f"\n[Rerouting Signal: {self.active_adapter.model_name} failed ({e}). Trying next node...]\n")
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
