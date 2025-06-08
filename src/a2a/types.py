from dataclasses import dataclass
from typing import List

@dataclass
class AgentSkill:
    id: str
    name: str
    description: str
    tags: List[str]
    examples: List[str]

@dataclass
class AgentCapabilities:
    streaming: bool

@dataclass
class AgentCard:
    name: str
    description: str
    url: str
    version: str
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
