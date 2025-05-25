from typing import List, Dict, Any, Tuple

class JobMatchingVectorizer:
    def __init__(self):
        # Maximum skill level (levels are 1-3)
        self.max_level = 3

    def _normalize_level(self, level: int) -> float:
        """Normalize skill level to range [0, 1]."""
        return round(level / self.max_level, 2)

    def create_skill_vector(self, skills: List[Dict[str, Any]]) -> List[Tuple[int, float]]:
        """
        Create a vector of skills in format [(skillId, normalized_level), (skillId, normalized_level), ...]
        where normalized_level is in range [0, 1]
        """
        return [(skill['id'], self._normalize_level(skill['level'])) for skill in skills]
