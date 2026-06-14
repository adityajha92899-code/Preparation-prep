from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass
class Problem:
    id: int
    title: str
    difficulty: Difficulty
    patterns: List[str]
    companies: List[str]
    frequency: float
    key_insight: str
    url: str = ""

    @property
    def leetcode_url(self):
        slug = self.title.lower().replace(" ", "-").replace("'", "")
        return f"https://leetcode.com/problems/{slug}/"


LEETCODE_PROBLEMS: List[Problem] = [
    Problem(1, "Two Sum", Difficulty.EASY, ["Hash Map"], ["Google", "Amazon"], 0.95, "Use hashmap: complement = target - num"),
    Problem(15, "3Sum", Difficulty.MEDIUM, ["Two Pointers"], ["Meta", "Amazon"], 0.91, "Sort + two pointers"),
    Problem(704, "Binary Search", Difficulty.EASY, ["Binary Search"], ["Google", "Amazon"], 0.9, "Classic binary search template"),
]

PATTERN_PROBLEMS: Dict[str, List[int]] = {
    "Sliding Window": [3, 76, 239],
    "Two Pointers": [1, 15, 11],
    "Binary Search": [704, 33, 34],
}

COMPANY_TOP_PROBLEMS: Dict[str, List[int]] = {"Google": [1, 3, 15, 42, 76]}

STUDY_PLAN_20_WEEKS = []
STUDY_PLAN_20_WEEKS = [
    {"week": 1, "theme": "Arrays & Hashing", "patterns": ["Hash Map", "Two Pointers"], "must_solve": [1, 15], "daily_problems": 3},
    {"week": 2, "theme": "Sliding Window", "patterns": ["Sliding Window"], "must_solve": [3, 76], "daily_problems": 3},
    {"week": 3, "theme": "Binary Search", "patterns": ["Binary Search"], "must_solve": [704, 33], "daily_problems": 3},
    {"week": 4, "theme": "Linked List", "patterns": ["Linked List"], "must_solve": [206, 21], "daily_problems": 3},
]
