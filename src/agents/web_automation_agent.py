from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent

class WebAutomationAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("WebAutomationAgent", "Browser automation for UberEats ordering", 9003)
        self.selenium_tools = None

    def _create_agent_card(self) -> AgentCard:
        skills = [
            AgentSkill(
                id="web_automation",
                name="Web Browser Automation",
                description="Automates browser interactions for food ordering",
                tags=["selenium", "browser", "automation", "ubereats"],
                examples=["navigate to restaurant", "add items to cart", "fill forms"]
            ),
            AgentSkill(
                id="site_navigation",
                name="Site Navigation",
                description="Navigates UberEats website structure",
                tags=["navigation", "search", "menu"],
                examples=["find mcdonalds", "search menu items", "locate add to cart"]
            )
        ]

        return AgentCard(
            name="Web Automation Agent",
            description="Browser automation specialist for food ordering",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["json"],
            defaultOutputModes=["json"],
            capabilities=AgentCapabilities(streaming=False),
            skills=skills
        )

    async def get_selenium_tools(self):
        if not self.selenium_tools:
            mcp_params = StdioServerParameters(
                command="selenium-mcp-server",
                args=["--headless", "--ubereats-mode"]
            )

            toolset = MCPToolset("selenium_automation", mcp_params)
            self.selenium_tools, _ = await toolset.get_tools_async()

        return self.selenium_tools

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Starting web automation: {message}")

        try:
            tools = await self.get_selenium_tools()

            web_agent = LlmAgent(
                model='gemini-2.0-flash',
                name='ubereats_automation',
                instruction=(
                    "You are a UberEats web automation specialist. Navigate to UberEats.com, "
                    "search for McDonald's, add specified items to cart, and prepare for checkout. "
                    "Use browser tools methodically: navigate -> search -> select items -> add to cart. "
                    "Always confirm each step before proceeding to the next."
                ),
                tools=tools
            )

            order_details = message.get("order_details", [])
            automation_prompt = f"""
            Please automate the following UberEats order:
            1. Navigate to UberEats.com
            2. Search for McDonald's restaurants in Chicago
            3. Select the McDonald's Global Menu Restaurant
            4. Add these items to cart: {', '.join(order_details)}
            5. Proceed to cart review (but don't complete checkout yet)

            Return the cart ID and status when ready for checkout.
            """

            result = await web_agent.process_message(automation_prompt)

            return {
                "status": "ready_for_checkout",
                "cart_id": "cart_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
                "items_added": order_details,
                "automation_log": result
            }

        except Exception as e:
            self.logger.error(f"Web automation failed: {str(e)}")
            return {
                "status": "automation_failed",
                "error": str(e)
            }
