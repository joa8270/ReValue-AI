from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseSkill(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The display name of the skill."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the skill does."""
        pass
    
    @property
    @abstractmethod
    def slug(self) -> str:
        """Unique identifier for the skill (URL-friendly)."""
        pass

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill logic.
        :param context: Dictionary containing input parameters.
        :return: Dictionary containing the execution result.
        """
        pass
