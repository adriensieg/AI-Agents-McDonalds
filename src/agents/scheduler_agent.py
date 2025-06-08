from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from .user_proxy_agent import UserProxyAgent

class SchedulerAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("SchedulerAgent", "Automated scheduling for regular orders", 9006)
        self.is_running = False

    def _create_agent_card(self) -> AgentCard:
        skills = [
            AgentSkill(
                id="schedule_orders",
                name="Schedule Regular Orders",
                description="Schedules recurring McDonald's orders",
                tags=["schedule", "cron", "automation", "recurring"],
                examples=["schedule wednesday order", "set recurring delivery"]
            ),
            AgentSkill(
                id="time_management",
                name="Time-based Triggers",
                description="Manages time-based order triggers",
                tags=["time", "trigger", "automation"],
                examples=["trigger at lunch time", "weekly scheduling"]
            )
        ]

        return AgentCard(
            name="Scheduler Agent",
            description="Automated scheduling for food orders",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["json"],
            defaultOutputModes=["json"],
            capabilities=AgentCapabilities(streaming=False),
            skills=skills
        )

    async def start_scheduling(self):
        self.is_running = True
        self.logger.info("Starting Wednesday McDonald's scheduler...")

        while self.is_running:
            now = datetime.now()

            if now.weekday() == 2 and now.hour == 12 and now.minute == 0:
                self.logger.info("Wednesday lunch time! Triggering order...")
                await self._trigger_weekly_order()

            await asyncio.sleep(60)

    async def _trigger_weekly_order(self):
        user_proxy = UserProxyAgent()
        order_message = {
            "content": "Order my usual Wednesday McDonald's Global Menu special",
            "scheduled": True,
            "trigger_time": datetime.now().isoformat()
        }

        result = await user_proxy.process_message(order_message)
        self.logger.info(f"Scheduled order result: {result}")

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        command = message.get("command", "")

        if command == "start_scheduling":
            if not self.is_running:
                asyncio.create_task(self.start_scheduling())
                return {"status": "scheduler_started", "message": "Wednesday scheduling activated"}
            else:
                return {"status": "already_running", "message": "Scheduler is already active"}

        elif command == "stop_scheduling":
            self.is_running = False
            return {"status": "scheduler_stopped", "message": "Scheduling deactivated"}

        return {"status": "unknown_command", "message": f"Unknown command: {command}"}
