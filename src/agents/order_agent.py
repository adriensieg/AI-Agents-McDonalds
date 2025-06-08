from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from .menu_understanding_agent import MenuUnderstandingAgent
from .web_automation_agent import WebAutomationAgent
from .checkout_agent import CheckoutAgent

class OrderAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("OrderAgent", "Processes and orchestrates food orders", 9002)

    def _create_agent_card(self) -> AgentCard:
        skills = [
            AgentSkill(
                id="process_order",
                name="Process Food Order",
                description="Orchestrates the complete ordering process",
                tags=["order", "process", "orchestrate"],
                examples=["process my order", "handle food request"]
            ),
            AgentSkill(
                id="delegate_tasks",
                name="Delegate Order Tasks",
                description="Delegates tasks to specialized agents",
                tags=["delegate", "coordinate"],
                examples=["coordinate with web agent", "handle menu parsing"]
            )
        ]

        return AgentCard(
            name="Order Processing Agent",
            description="Main orchestrator for McDonald's orders",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["text", "json"],
            defaultOutputModes=["text", "json"],
            capabilities=AgentCapabilities(streaming=True),
            skills=skills
        )

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Processing order: {message}")

        try:
            menu_agent = MenuUnderstandingAgent()
            parsed_order = await menu_agent.process_message({
                "type": "parse_intent",
                "user_input": message.get("user_input", "")
            })

            web_agent = WebAutomationAgent()
            automation_result = await web_agent.process_message({
                "type": "place_order",
                "order_details": parsed_order.get("parsed_items", []),
                "restaurant": "mcdonalds"
            })

            if automation_result.get("status") == "ready_for_checkout":
                checkout_agent = CheckoutAgent()
                checkout_result = await checkout_agent.process_message({
                    "type": "complete_checkout",
                    "cart_id": automation_result.get("cart_id")
                })

                return {
                    "status": "order_completed",
                    "order_id": checkout_result.get("order_id"),
                    "message": "Your McDonald's order has been placed successfully!"
                }

            return {
                "status": "order_failed",
                "message": "Failed to complete the order process",
                "details": automation_result
            }

        except Exception as e:
            self.logger.error(f"Order processing failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Order processing error: {str(e)}"
            }
