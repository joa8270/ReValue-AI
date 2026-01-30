import importlib
import inspect
import os
import pkgutil
from typing import Dict, List, Type
from app.skills.base import BaseSkill

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")

    def discover_skills(self):
        """
        Scans the skills directory and registers all valid skills.
        """
        print(f"[SkillRegistry] Scanning for skills in {self._skills_dir}...")
        self._skills.clear()

        # Iterate through all files in the skills directory
        for _, name, _ in pkgutil.iter_modules([self._skills_dir]):
            if name == "base":
                continue
            
            try:
                # Dynamically import the module
                module = importlib.import_module(f"app.skills.{name}")
                
                # Inspect module for classes
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    
                    if (inspect.isclass(attribute) and 
                        issubclass(attribute, BaseSkill) and 
                        attribute is not BaseSkill):
                        
                        # Instantiate the skill
                        try:
                            skill_instance = attribute()
                            self.register_skill(skill_instance)
                        except Exception as e:
                            print(f"[ERR] [SkillRegistry] Failed to instantiate skill {attribute_name}: {e}")

            except Exception as e:
                print(f"[ERR] [SkillRegistry] Failed to load module {name}: {e}")

        print(f"[SkillRegistry] Discovered {len(self._skills)} skills.")

    def register_skill(self, skill: BaseSkill):
        """
        Registers a single skill instance.
        """
        if skill.slug in self._skills:
            print(f"[WARN] [SkillRegistry] Duplicate skill slug detected: {skill.slug}. Overwriting.")
        
        self._skills[skill.slug] = skill
        print(f"[SkillRegistry] Registered skill: {skill.name} ({skill.slug})")

    def get_skill(self, slug: str) -> BaseSkill | None:
        """
        Retrieves a skill by its slug.
        """
        return self._skills.get(slug)

    def list_skills(self) -> List[Dict[str, str]]:
        """
        Returns a list of all registered skills metadata.
        """
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "slug": skill.slug
            }
            for skill in self._skills.values()
        ]

# Global instance
skill_registry = SkillRegistry()
