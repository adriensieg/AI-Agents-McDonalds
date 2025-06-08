from .base_agent import BaseA2AAgent, AgentCard, AgentSkill, AgentCapabilities
from google.adk.agents.llm_agent import LlmAgent

class MenuUnderstandingAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("MenuUnderstandingAgent", "AI-powered menu understanding", 9004)

    def _create_agent_card(self) -> AgentCard:
        skills = [
            AgentSkill(
                id="parse_menu_intent",
                name="Parse Menu Intent",
                description="Understands natural language food requests",
                tags=["nlp", "menu", "parsing", "gemini"],
                examples=["something spicy", "my usual", "healthy option", "chicken nuggets"]
            ),
            AgentSkill(
                id="menu_recommendation",
                name="Menu Recommendations",
                description="Suggests items based on preferences",
                tags=["recommendation", "preference", "suggest"],
                examples=["recommend spicy items", "suggest healthy options"]
            )
        ]

        return AgentCard(
            name="Menu Understanding Agent",
            description="AI-powered menu parser and recommender",
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=["text"],
            defaultOutputModes=["json"],
            capabilities=AgentCapabilities(streaming=True),
            skills=skills
        )

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        user_input = message.get("user_input", "")
        self.logger.info(f"Parsing menu intent: {user_input}")

        menu_agent = LlmAgent(
            model='gemini-2.0-flash',
            name='menu_parser',
            instruction=(
                "You are a McDonald's Global Menu expert. Parse user requests into specific menu items. "
                "Available items include: Spicy Black Garlic Chicken McNuggets (Japan), "
                "Pistachio McFlurry (Italy), Cheese & Bacon Loaded Fries (Australia), "
                "plus standard McDonald's menu. Return a JSON list of specific items to order."
            ),
            tools=[]
        )

        parsing_prompt = f"""
        Parse this McDonald's order request into specific menu items:
        "{user_input}"

        Consider:
        - If they say "spicy" -> suggest Spicy Black Garlic Chicken McNuggets
        - If they say "usual" or "wednesday special" -> suggest global menu rotation items
        - If they want dessert -> suggest Pistachio McFlurry
        - If they want sides -> suggest Cheese & Bacon Loaded Fries

        Return JSON format: {{"parsed_items": ["item1", "item2"], "reasoning": "why these items"}}
        """

        try:
            result = await menu_agent.process_message(parsing_prompt)

            if "Spicy Black Garlic Chicken McNuggets" not in result:
                parsed_items = [
                    "Spicy Black Garlic Chicken McNuggets",
                    "Pistachio McFlurry",
                    "Medium Fries"
                ]
            else:
                parsed_items = ["Spicy Black Garlic Chicken McNuggets", "Pistachio McFlurry"]

            return {
                "parsed_items": parsed_items,
                "original_request": user_input,
                "reasoning": "Selected global menu favorites for Wednesday tradition"
            }

        except Exception as e:
            self.logger.error(f"Menu parsing failed: {str(e)}")
            return {
                "parsed_items": ["Spicy Black Garlic Chicken McNuggets"],
                "error": str(e)
            }
