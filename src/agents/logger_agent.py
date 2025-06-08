from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from datetime import datetime

class LoggerAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("LoggerAgent", "Centralized logging and monitoring", 9007)
        self.log_storage = []

    def _create_agent_card(self) -> AgentCard:
        skills = [
            AgentSkill(
                id="centralized_logging",
                name="Centralized Logging",
                description="Collects and stores logs from all agents",
                tags=["logging", "monitoring", "debugging"],
                examples=["log agent activity", "store error logs", "monitor performance"]
            ),
            AgentSkill(
                id="analytics",
                name="Order Analytics",
                description="Provides analytics on ordering patterns",
                tags=["analytics", "metrics", "reporting"],
                examples=["order success rate", "weekly statistics", "error analysis"]
            )
        ]

        return AgentCard(
            name="Logger Agent",
            description="Centralized logging and analytics",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["json"],
            defaultOutputModes=["json"],
            capabilities=AgentCapabilities(streaming=True),
            skills=skills
        )

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": message.get("agent", "unknown"),
            "level": message.get("level", "info"),
            "message": message.get("message", ""),
            "data": message.get("data", {})
        }

        self.log_storage.append(log_entry)
        self.logger.info(f"Logged: {log_entry}")

        return {"status": "logged", "entry_id": len(self.log_storage)}

    def get_analytics(self) -> Dict[str, Any]:
        total_logs = len(self.log_storage)
        error_logs = len([log for log in self.log_storage if log["level"] == "error"])

        return {
            "total_events": total_logs,
            "error_rate": error_logs / total_logs if total_logs > 0 else 0,
            "agents_active": len(set(log["agent"] for log in self.log_storage)),
            "last_activity": self.log_storage[-1]["timestamp"] if self.log_storage else None
        }
