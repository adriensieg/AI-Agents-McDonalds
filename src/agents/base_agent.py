import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any

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

class BaseA2AAgent(ABC):
    def __init__(self, name: str, description: str, port: int):
        self.name = name
        self.description = description
        self.port = port
        self.agent_card = self._create_agent_card()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(f'[{self.name}] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @abstractmethod
    def _create_agent_card(self) -> AgentCard:
        pass

    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        pass
