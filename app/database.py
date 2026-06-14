from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
from datetime import datetime
from typing import Optional, List
import uuid


DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/maang_prep"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)

    current_role: Mapped[str] = mapped_column(String, default="student")
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    target_companies: Mapped[list] = mapped_column(JSON, default=list)
    target_role: Mapped[str] = mapped_column(String, default="sde1")
    target_salary_lpa: Mapped[int] = mapped_column(Integer, default=50)
    current_skills: Mapped[dict] = mapped_column(JSON, default=dict)

    leetcode_solved: Mapped[int] = mapped_column(Integer, default=0)
    prep_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    target_interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    available_hours_per_day: Mapped[int] = mapped_column(Integer, default=6)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    progress_records: Mapped[List["ProgressRecord"]] = relationship(back_populates="user")
    solved_problems: Mapped[List["SolvedProblem"]] = relationship(back_populates="user")
    projects: Mapped[List["Project"]] = relationship(back_populates="user")
    interviews: Mapped[List["MockInterview"]] = relationship(back_populates="user")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="user")


class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    problems_solved_today: Mapped[int] = mapped_column(Integer, default=0)
    patterns_practiced: Mapped[list] = mapped_column(JSON, default=list)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)

    system_designs_done: Mapped[int] = mapped_column(Integer, default=0)
    mock_interviews_done: Mapped[int] = mapped_column(Integer, default=0)
    behavioral_stories: Mapped[int] = mapped_column(Integer, default=0)
    study_hours: Mapped[float] = mapped_column(Float, default=0.0)

    dsa_score: Mapped[float] = mapped_column(Float, default=0.0)
    sd_score: Mapped[float] = mapped_column(Float, default=0.0)
    behavioral_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_readiness: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["User"] = relationship(back_populates="progress_records")


class SolvedProblem(Base):
    __tablename__ = "solved_problems"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    problem_id: Mapped[int] = mapped_column(Integer)
    problem_title: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)
    patterns: Mapped[list] = mapped_column(JSON, default=list)
    companies: Mapped[list] = mapped_column(JSON, default=list)

    language: Mapped[str] = mapped_column(String, default="python")
    solution_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    time_complexity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    space_complexity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    time_taken_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    needed_hints: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_score: Mapped[int] = mapped_column(Integer, default=3)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    solved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    next_review: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="solved_problems")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    tech_stack: Mapped[list] = mapped_column(JSON, default=list)
    github_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    live_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    impact_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String, default="in_progress")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="projects")


class MockInterview(Base):
    __tablename__ = "mock_interviews"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    company: Mapped[str] = mapped_column(String)
    round_type: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)

    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hire_signal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    improvements: Mapped[list] = mapped_column(JSON, default=list)

    conversation: Mapped[list] = mapped_column(JSON, default=list)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    conducted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="interviews")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    agent_type: Mapped[str] = mapped_column(String)
    messages: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped["User"] = relationship(back_populates="conversations")


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")
