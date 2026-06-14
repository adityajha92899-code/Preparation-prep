try:
    import google.generativeai as genai
except Exception:
    genai = None
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from functools import wraps

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator


class AgentRole(Enum):
    MASTER_ADVISOR = "master_advisor"
    DSA_EXPERT = "dsa_expert"
    SYSTEM_DESIGN = "system_design"
    PROJECT_ADVISOR = "project_advisor"
    HACKATHON_COACH = "hackathon_coach"
    INTERVIEW_SIMULATOR = "interview_simulator"
    BEHAVIORAL_COACH = "behavioral_coach"
    CODE_REVIEWER = "code_reviewer"
    CAREER_STRATEGIST = "career_strategist"


@dataclass
class ChatMessage:
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentContext:
    user_id: str
    user_profile: Dict[str, Any]
    current_phase: str
    target_companies: List[str]
    strengths: List[str]
    weaknesses: List[str]
    solved_problems: List[int]
    projects: List[Dict]
    timeline_weeks: int
    conversation_history: List[ChatMessage] = field(default_factory=list)


@dataclass
class AgentResponse:
    agent: AgentRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens_used: int = 0
    latency_ms: float = 0.0
    model_used: str = ""


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict], **kwargs) -> str:
        pass

    @abstractmethod
    async def stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        pass


class GoogleAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "models/chat-bison-001"):
        if genai:
            self.client = genai
            self.client.configure(api_key=api_key)
        else:
            self.client = None
        self.model = model

    @retry_with_backoff(max_retries=3)
    async def generate(self, messages: List[Dict], **kwargs) -> str:
        if not self.client:
            raise RuntimeError("Google Generative AI client is not available.")

        start = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_output_tokens=kwargs.get("max_tokens", 1024),
        )
        latency = (time.time() - start) * 1000
        logger.info(f"GoogleAI {self.model}: {latency:.0f}ms")

        content = ""
        if hasattr(response, "last") and response.last is not None:
            try:
                content = response.last.output_text
            except Exception:
                try:
                    content = response.last.response
                except Exception:
                    content = str(response.last)
        elif isinstance(response, dict):
            content = response.get("output_text") or response.get("response", "")
        else:
            content = str(response)
        return content

    async def stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        text = await self.generate(messages, **kwargs)
        for i in range(0, len(text), 80):
            yield text[i : i + 80]
            await asyncio.sleep(0.01)


class FallbackProvider(BaseLLMProvider):
    def __init__(self, primary: BaseLLMProvider, fallback: BaseLLMProvider):
        self.primary = primary
        self.fallback = fallback

    async def generate(self, messages: List[Dict], **kwargs) -> str:
        try:
            return await self.primary.generate(messages, **kwargs)
        except Exception as e:
            logger.warning(f"Primary provider failed: {e}. Using fallback.")
            return await self.fallback.generate(messages, **kwargs)

    async def stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        try:
            async for chunk in self.primary.stream(messages, **kwargs):
                yield chunk
        except Exception as e:
            logger.warning(f"Primary provider stream failed: {e}. Using fallback.")
            async for chunk in self.fallback.stream(messages, **kwargs):
                yield chunk


class DummyProvider(BaseLLMProvider):
    """Simple provider used when real SDKs or API keys are not available."""
    def __init__(self, name: str = "dummy"):
        self.name = name

    async def generate(self, messages: List[Dict], **kwargs) -> str:
        user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_msg = m.get("content")
                break
        return f"[placeholder response from {self.name}] I received: {user_msg[:200]}"

    async def stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        # yield a few chunks to simulate streaming
        text = await self.generate(messages, **kwargs)
        for i in range(0, len(text), 80):
            yield text[i : i + 80]
            await asyncio.sleep(0.01)


SYSTEM_PROMPTS = {AgentRole.MASTER_ADVISOR: "You are an ELITE Placement Preparation Advisor."}


class LLMOrchestrator:
    def __init__(self, settings):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.agent_configs: Dict[AgentRole, Dict] = {}
        self._setup(settings)

    def _setup(self, settings):
        # Prefer Google Generative AI when the key is available
        if settings.GOOGLE_AI_KEY and genai:
            try:
                google_provider = GoogleAIProvider(settings.GOOGLE_AI_KEY, settings.GOOGLE_AI_MODEL)
                self.providers["google"] = google_provider
            except Exception as e:
                logger.warning(f"Failed to initialize Google AI provider: {e}")

        # If no real provider available, register a DummyProvider
        if not self.providers:
            dummy = DummyProvider("dummy")
            self.providers["dummy"] = dummy
            self.providers["google"] = dummy

        self.agent_configs = {
            AgentRole.MASTER_ADVISOR: {"provider": list(self.providers.keys())[0], "temperature": 0.7, "max_tokens": 1024},
            AgentRole.DSA_EXPERT: {"provider": list(self.providers.keys())[0], "temperature": 0.2, "max_tokens": 1024},
            AgentRole.SYSTEM_DESIGN: {"provider": list(self.providers.keys())[0], "temperature": 0.5, "max_tokens": 1024},
        }

        logger.info(f"LLM providers registered: {list(self.providers.keys())}")

    def list_providers(self) -> List[str]:
        return list(self.providers.keys())

    def _get_provider(self, provider_name: str) -> BaseLLMProvider:
        provider = self.providers.get(provider_name)
        if not provider:
            if self.providers:
                return list(self.providers.values())[0]
            raise RuntimeError("No LLM providers available. Check API keys.")
        return provider

    async def _route_query(self, query: str, context: AgentContext) -> AgentRole:
        provider = self._get_provider(list(self.providers.keys())[0])
        result = await provider.generate(
            [
                {"role": "system", "content": "Route queries to the most appropriate agent. Respond with only the agent name."},
                {"role": "user", "content": f"Given this query, which agent should handle it?\nQUERY: {query}"},
            ],
            temperature=0.1,
            max_tokens=30,
        )

        agent_name = result.strip().upper().replace(" ", "_")
        try:
            return AgentRole[agent_name]
        except Exception:
            return AgentRole.MASTER_ADVISOR

    def _build_messages(self, query: str, context: AgentContext, agent: AgentRole) -> List[Dict]:
        system_prompt = SYSTEM_PROMPTS.get(agent, SYSTEM_PROMPTS[AgentRole.MASTER_ADVISOR])
        context_block = f"User: {context.user_id}"
        full_system = f"{system_prompt}\n\n{context_block}"
        messages = [{"role": "system", "content": full_system}]
        for msg in context.conversation_history[-16:]:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": query})
        return messages

    async def query(self, query: str, context: AgentContext, force_agent: Optional[AgentRole] = None) -> AgentResponse:
        start = time.time()
        agent = force_agent or await self._route_query(query, context)
        config = self.agent_configs.get(agent, list(self.agent_configs.values())[0])
        provider = self._get_provider(config["provider"])
        messages = self._build_messages(query, context, agent)

        content = await provider.generate(messages, temperature=config["temperature"], max_tokens=config["max_tokens"])

        return AgentResponse(agent=agent, content=content, latency_ms=(time.time() - start) * 1000, model_used=config["provider"])

    async def stream_query(self, query: str, context: AgentContext, force_agent: Optional[AgentRole] = None) -> AsyncGenerator[Dict[str, Any], None]:
        agent = force_agent or await self._route_query(query, context)
        config = self.agent_configs.get(agent, list(self.agent_configs.values())[0])
        provider = self._get_provider(config["provider"])
        messages = self._build_messages(query, context, agent)

        yield {"type": "start", "agent": agent.value}

        async for chunk in provider.stream(messages, temperature=config["temperature"], max_tokens=config["max_tokens"]):
            yield {"type": "chunk", "content": chunk}

        yield {"type": "end", "agent": agent.value}
