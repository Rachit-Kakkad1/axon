import subprocess
import os
from typing import Dict, Any

class ShellTool:
    """Executes system commands in the project environment."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root

    def execute(self, command: str) -> str:
        """Runs a shell command and returns stdout + stderr."""
        try:
            # Always run from project root for consistency
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60 # Safety timeout
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            return output if output.strip() else "[Command executed successfully with no output]"
        except Exception as e:
            return f"[Error executing command]: {str(e)}"

class FileTool:
    """Manages filesystem operations: read, write, and patch."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root

    def read_file(self, path: str) -> str:
        full_path = self._get_path(path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file]: {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        full_path = self._get_path(path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"[Successfully wrote to {path}]"
        except Exception as e:
            return f"[Error writing file]: {str(e)}"

    def _get_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(self.project_root, path)
