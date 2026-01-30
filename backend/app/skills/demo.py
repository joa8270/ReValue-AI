from .base import BaseSkill
from typing import Dict, Any

class DemoSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "Demo Skill"

    @property
    def description(self) -> str:
        return "A simple demonstration skill that returns a greeting."

    @property
    def slug(self) -> str:
        return "demo-skill"

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        user_name = context.get("name", "Traveler")
        return {
            "message": f"Hello, {user_name}! The Skill System is operational.",
            "status": "success",
            "received_context": context
        }
