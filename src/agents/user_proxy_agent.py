from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from .order_agent import OrderAgent

class UserProxyAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("UserProxyAgent", "Initiates McDonald's ordering process", 9001)

    def _create_agent_card(self) -> AgentCard:
        skill = AgentSkill(
            id="initiate_order",
            name="Initiate Food Order",
            description="Starts the McDonald's ordering process",
            tags=["order", "initiate", "mcdonalds"],
            examples=["order my usual", "get me something spicy", "order wednesday special"]
        )

        return AgentCard(
            name="User Proxy Agent",
            description="Entry point for McDonald's ordering system",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=AgentCapabilities(streaming=True),
            skills=[skill]
        )

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Received order request: {message}")

        order_request = {
            "type": "order_request",
            "user_input": message.get("content", ""),
            "timestamp": datetime.now().isoformat(),
            "source": "user_proxy"
        }

        return await self._send_to_order_agent(order_request)

    async def _send_to_order_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        order_agent = OrderAgent()
        return await order_agent.process_message(request)
