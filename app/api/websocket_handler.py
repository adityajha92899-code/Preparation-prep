from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging

from app.core.llm_engine import LLMOrchestrator, AgentContext, AgentRole, ChatMessage
from app.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_histories: Dict[str, List[ChatMessage]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if user_id not in self.conversation_histories:
            self.conversation_histories[user_id] = []
        logger.info(f"User {user_id} connected")

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        logger.info(f"User {user_id} disconnected")

    async def send_json(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def add_to_history(self, user_id: str, role: str, content: str):
        if user_id not in self.conversation_histories:
            self.conversation_histories[user_id] = []
        self.conversation_histories[user_id].append(ChatMessage(role=role, content=content))
        if len(self.conversation_histories[user_id]) > 20:
            self.conversation_histories[user_id] = self.conversation_histories[user_id][-20:]

    def get_history(self, user_id: str) -> List[ChatMessage]:
        return self.conversation_histories.get(user_id, [])


manager = ConnectionManager()
orchestrator = LLMOrchestrator(settings)


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    await manager.send_json(websocket, {"type": "connected", "message": "Connected", "user_id": user_id})

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "").strip()
            if not message:
                continue

            agent_name = data.get("agent", "auto")
            context_data = data.get("context", {})

            history = manager.get_history(user_id)
            context = AgentContext(
                user_id=user_id,
                user_profile=context_data.get("profile", {}),
                current_phase=context_data.get("phase", "foundation"),
                target_companies=context_data.get("companies", ["Google"]),
                strengths=context_data.get("strengths", []),
                weaknesses=context_data.get("weaknesses", []),
                solved_problems=context_data.get("solved", []),
                projects=context_data.get("projects", []),
                timeline_weeks=context_data.get("weeks", 20),
                conversation_history=history,
            )

            force_agent = None
            if agent_name and agent_name != "auto":
                try:
                    force_agent = AgentRole[agent_name.upper()]
                except KeyError:
                    pass

            manager.add_to_history(user_id, "user", message)

            full_response = ""
            try:
                async for chunk in orchestrator.stream_query(message, context, force_agent):
                    await manager.send_json(websocket, chunk)
                    if chunk.get("type") == "chunk":
                        full_response += chunk["content"]

                manager.add_to_history(user_id, "assistant", full_response)
            except Exception as e:
                logger.error(f"Error streaming response: {e}")
                await manager.send_json(websocket, {"type": "error", "message": "An error occurred."})

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(user_id)
