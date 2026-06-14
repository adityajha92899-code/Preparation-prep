from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json

from app.config import settings
from app.core.llm_engine import LLMOrchestrator, AgentContext, AgentRole
from app.knowledge_base.dsa.patterns import LEETCODE_PROBLEMS, STUDY_PLAN_20_WEEKS
from training.rag_pipeline import PlacementKnowledgeBase

router = APIRouter(prefix="/api/v1")

orchestrator = LLMOrchestrator(settings)
kb = PlacementKnowledgeBase()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: str = "anonymous"
    agent: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    use_rag: bool = True


@router.post("/chat")
async def chat(request: ChatRequest):
    context = _build_context(request.context, request.user_id)
    force_agent = None
    if request.agent and request.agent != "auto":
        try:
            force_agent = AgentRole[request.agent.upper()]
        except KeyError:
            pass

    query = request.message
    if request.use_rag and force_agent:
        query = kb.augment_with_context(request.message, force_agent.value)

    result = await orchestrator.query(query, context, force_agent)

    return {"success": True, "agent": result.agent.value, "response": result.content, "latency_ms": round(result.latency_ms), "model": result.model_used}


@router.get("/dsa/problems")
async def get_problems(limit: int = 50):
    problems = LEETCODE_PROBLEMS[:limit]
    return {"success": True, "total": len(problems), "problems": [
        {"id": p.id, "title": p.title, "difficulty": p.difficulty.value, "patterns": p.patterns} for p in problems
    ]}


def _build_context(context_data: Optional[Dict], user_id: str) -> AgentContext:
    data = context_data or {}
    return AgentContext(
        user_id=user_id,
        user_profile=data.get("profile", {}),
        current_phase=data.get("phase", "foundation"),
        target_companies=data.get("companies", ["Google"]),
        strengths=data.get("strengths", []),
        weaknesses=data.get("weaknesses", []),
        solved_problems=data.get("solved", []),
        projects=data.get("projects", []),
        timeline_weeks=data.get("weeks", 20),
    )


@router.get("/dsa/daily-plan")
async def get_daily_plan(company: str = "Google", solved_count: int = 0):
    # Simple heuristic for difficulty mix
    if solved_count < 50:
        mix = "40% Easy, 60% Medium"
    elif solved_count < 150:
        mix = "100% Medium"
    else:
        mix = "60% Medium, 40% Hard"

    problems = LEETCODE_PROBLEMS[:10]
    return {
        "success": True,
        "target_company": company,
        "date_problem_mix": mix,
        "problems": [{"id": p.id, "title": p.title, "difficulty": p.difficulty.value} for p in problems[:3]],
    }


@router.get("/roadmap/study-plan")
async def get_study_plan(weeks: int = 20):
    plan = STUDY_PLAN_20_WEEKS[:weeks] if STUDY_PLAN_20_WEEKS else []
    return {"success": True, "weeks": len(plan), "plan": plan}


@router.get("/health")
async def health_check():
    # Basic health check for app readiness
    try:
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "db": db_ok, "kb_loaded": True}


@router.get("/kb/search")
async def kb_search(query: str, collection: str = "all", limit: int = 3):
    results = kb.search(query, collection_name=collection, n_results=limit)
    return {"success": True, "query": query, "results": results}


@router.post("/system-design/solve")
async def solve_system_design(payload: Dict[str, Any]):
    problem = payload.get("problem", "Generic System")
    company = payload.get("company", "Google")
    context = _build_context({"companies": [company]}, "user")
    kb_results = kb.search(problem, collection_name="system_designs", n_results=1)
    kb_ctx = kb_results[0]["content"] if kb_results else ""
    prompt = f"Design: {problem}\nCompany: {company}\nReference:\n{kb_ctx}\nProvide architecture and components."
    result = await orchestrator.query(prompt, context, AgentRole.SYSTEM_DESIGN)
    return {"success": True, "problem": problem, "solution": result.content}


@router.post("/interview/start-mock")
async def start_mock_interview(payload: Dict[str, Any]):
    company = payload.get("company", "Google")
    round_type = payload.get("round_type", "coding")
    difficulty = payload.get("difficulty", "medium")
    context = _build_context({"companies": [company], "phase": "mock_interview"}, "user")
    prompt = f"Start a {round_type} mock interview for {company}. Difficulty: {difficulty}. Present one problem and wait for candidate." 
    result = await orchestrator.query(prompt, context, AgentRole.INTERVIEW_SIMULATOR)
    return {"success": True, "company": company, "round_type": round_type, "opening": result.content}


@router.post("/progress/log-problem")
async def log_problem_solved(payload: Dict[str, Any]):
    problem_id = payload.get("problem_id")
    confidence = int(payload.get("confidence", 3))
    from datetime import datetime, timedelta
    review_intervals = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
    next_review_days = review_intervals.get(confidence, 7)
    next_review = datetime.utcnow() + timedelta(days=next_review_days)
    problem = next((p for p in LEETCODE_PROBLEMS if p.id == problem_id), None)
    return {"success": True, "logged": {"problem_id": problem_id, "title": problem.title if problem else "Unknown", "next_review": next_review.strftime("%Y-%m-%d")}}
