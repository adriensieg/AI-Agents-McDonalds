from agents.user_proxy_agent import UserProxyAgent
from agents.order_agent import OrderAgent
from agents.web_automation_agent import WebAutomationAgent
from agents.menu_understanding_agent import MenuUnderstandingAgent
from agents.checkout_agent import CheckoutAgent
from agents.scheduler_agent import SchedulerAgent
from agents.logger_agent import LoggerAgent

class McDonaldsA2AOrchestrator:
    def __init__(self):
        self.agents = {
            "user_proxy": UserProxyAgent(),
            "order_agent": OrderAgent(),
            "web_automation": WebAutomationAgent(),
            "menu_understanding": MenuUnderstandingAgent(),
            "checkout": CheckoutAgent(),
            "scheduler": SchedulerAgent(),
            "logger": LoggerAgent()
        }

    async def start_system(self):
        print("🍟 Starting McDonald's A2A Ordering System...")

        await self.agents["scheduler"].process_message({"command": "start_scheduling"})

        await self.agents["logger"].process_message({
            "agent": "orchestrator",
            "level": "info",
            "message": "McDonald's A2A system started successfully",
            "data": {"agents_count": len(self.agents)}
        })

        print("✅ All agents initialized and ready!")
        print("📅 Wednesday scheduling activated!")

    async def process_user_order(self, user_input: str) -> Dict[str, Any]:
        return await self.agents["user_proxy"].process_message({
            "content": user_input,
            "manual_trigger": True
        })

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "agents_active": len(self.agents),
            "scheduler_running": self.agents["scheduler"].is_running,
            "analytics": self.agents["logger"].get_analytics(),
            "timestamp": datetime.now().isoformat()
        }
