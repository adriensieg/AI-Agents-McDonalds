from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from datetime import datetime, timedelta

class CheckoutAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("CheckoutAgent", "Secure checkout and payment processing", 9005)

    def _create_agent_card(self) -> AgentCard:
        skills = [
            AgentSkill(
                id="secure_checkout",
                name="Secure Checkout",
                description="Handles login, address, and payment securely",
                tags=["checkout", "payment", "security", "login"],
                examples=["complete checkout", "process payment", "handle login"]
            ),
            AgentSkill(
                id="address_management",
                name="Address Management",
                description="Manages delivery addresses",
                tags=["address", "delivery", "location"],
                examples=["set delivery address", "confirm location"]
            )
        ]

        return AgentCard(
            name="Checkout Agent",
            description="Secure payment and checkout specialist",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["json"],
            defaultOutputModes=["json"],
            capabilities=AgentCapabilities(streaming=False),
            skills=skills
        )

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        cart_id = message.get("cart_id", "")
        self.logger.info(f"Processing checkout for cart: {cart_id}")

        try:
            checkout_steps = [
                "Authenticating user credentials",
                "Verifying delivery address in Chicago",
                "Processing payment method",
                "Confirming order details",
                "Placing order with restaurant"
            ]

            for step in checkout_steps:
                self.logger.info(f"Checkout step: {step}")
                await asyncio.sleep(0.5)

            order_id = f"MC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return {
                "status": "checkout_completed",
                "order_id": order_id,
                "estimated_delivery": (datetime.now() + timedelta(minutes=30)).isoformat(),
                "total_amount": "$12.99"
            }

        except Exception as e:
            self.logger.error(f"Checkout failed: {str(e)}")
            return {
                "status": "checkout_failed",
                "error": str(e)
            }
