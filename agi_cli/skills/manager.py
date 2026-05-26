import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SkillConfig:
    name: str
    description: str
    preferredProviders: List[str]
    memoryPriority: List[str]
    tools: List[str]
    mascotState: str
    hudTheme: str
    system_prompt: str = ""

class SkillManager:
    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            # Default to the skills directory relative to this file
            skills_dir = os.path.join(os.path.dirname(__file__))
        
        self.skills_dir = skills_dir
        self.skills: Dict[str, SkillConfig] = {}
        self._load_skills()

    def _load_skills(self):
        if not os.path.exists(self.skills_dir):
            return

        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            if os.path.isdir(skill_path):
                config_path = os.path.join(skill_path, "skill.json")
                prompt_path = os.path.join(skill_path, "prompt.md")
                
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                    
                    system_prompt = ""
                    if os.path.exists(prompt_path):
                        with open(prompt_path, "r") as f:
                            system_prompt = f.read()
                    
                    self.skills[skill_name.lower()] = SkillConfig(
                        name=config_data["name"],
                        description=config_data["description"],
                        preferredProviders=config_data["preferredProviders"],
                        memoryPriority=config_data["memoryPriority"],
                        tools=config_data["tools"],
                        mascotState=config_data["mascotState"],
                        hudTheme=config_data["hudTheme"],
                        system_prompt=system_prompt
                    )

    def detect_skill(self, user_input: str) -> Optional[SkillConfig]:
        """Detect the appropriate skill based on user input."""
        input_lower = user_input.lower()
        
        # Simple keyword-based detection
        keywords = {
            "coding": ["code", "python", "javascript", "function", "bug", "refactor", "repo", "git", "implement"],
            "research": ["research", "summarize", "find", "explain", "how does", "what is", "study", "analysis"],
            "architecture": ["architecture", "design", "scale", "system", "infrastructure", "distributed", "bottleneck"],
            "debug": ["debug", "error", "exception", "traceback", "crash", "fix", "logs", "failed"],
            "memory": ["memory", "remember", "context", "synapse", "forget", "compress", "history"]
        }
        
        for skill_id, triggers in keywords.items():
            if any(trigger in input_lower for trigger in triggers):
                return self.skills.get(skill_id)
        
        # Default to Coding if no clear match but technical-looking, or just return None
        return None

    def get_skill(self, name: str) -> Optional[SkillConfig]:
        return self.skills.get(name.lower())
