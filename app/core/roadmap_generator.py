from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import date, timedelta


@dataclass
class UserProfile:
    name: str
    current_role: str = "student"
    experience_years: int = 0
    target_companies: List[str] = None
    target_role: str = "sde2"
    target_salary_lpa: int = 50
    current_skills: Dict[str, int] = None
    leetcode_solved: int = 0
    projects: List[Dict[str, Any]] = None
    available_hours_per_day: int = 6
    prep_start_date: str = "2024-01-01"
    target_interview_date: str = "2024-07-01"
    strengths: List[str] = None
    weaknesses: List[str] = None


class RoadmapGenerator:
    def generate_complete_roadmap(self, profile: UserProfile) -> Dict[str, Any]:
        # Simple deterministic roadmap generator as placeholder
        weeks = 12
        start = date.today()
        plan = []
        for i in range(weeks):
            plan.append({
                "week": i + 1,
                "start_date": (start + timedelta(weeks=i)).isoformat(),
                "theme": "Mixed DSA",
                "daily_problems": 3,
            })

        return {
            "profile": {
                "name": profile.name,
                "target_companies": profile.target_companies,
                "target_role": profile.target_role,
            },
            "weeks": weeks,
            "plan": plan,
            "notes": "This is a generated placeholder roadmap. Customize further.",
        }
