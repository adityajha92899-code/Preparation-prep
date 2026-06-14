from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.api.routes import router
from app.api.websocket_handler import websocket_endpoint
from app.config import settings
from training.rag_pipeline import PlacementKnowledgeBase

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MAANG Prep Builder...")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"DB init may be skipped: {e}")

    try:
        kb = PlacementKnowledgeBase(settings.CHROMA_PERSIST_DIR)
        kb.build_complete_knowledge_base()
    except Exception as e:
        logger.warning(f"KB init failed: {e}")

    yield
    logger.info("Shutting down...")


app = FastAPI(title="MAANG Prep Builder", version="0.1.0", lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(router)


@app.websocket("/ws/{user_id}")
async def websocket_route(websocket: WebSocket, user_id: str):
    await websocket_endpoint(websocket, user_id)


@app.get("/")
async def root():
    return {"app": "MAANG Prep Builder", "version": "0.1.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
