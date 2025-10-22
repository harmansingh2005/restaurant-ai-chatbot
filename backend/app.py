"""
FastAPI backend for Dlanos Family Restaurant chat widget.

Endpoints:
- GET /health  -> health check
- POST /chat   -> chat with canned replies and LLM fallback

Features:
- Loads restaurant profile from restaurant.yml
- Returns canned replies for hours/menu/address/phone
- Calls OpenAI-compatible provider via provider_adapter for other queries
- In-memory LRU cache of recent replies to reduce costs and latency
- CORS for localhost dev ports and production domain
"""
from __future__ import annotations

import asyncio
from collections import OrderedDict
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

from guardrails import load_restaurant, canned_reply, build_system_prompt, postprocess
# Load .env BEFORE importing the provider so its module reads populated env vars
load_dotenv()
from provider_adapter import ChatProvider


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    reply: str
    source: str  # "canned" | "cache" | "llm"


class LRUCache:
    """Simple in-memory LRU cache for question->reply."""

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self._data: "OrderedDict[str, str]" = OrderedDict()

    def get(self, key: str) -> Optional[str]:
        if key in self._data:
            self._data.move_to_end(key)
            return self._data[key]
        return None

    def set(self, key: str, value: str) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)


# load_dotenv here is redundant now but harmless; keeping as a fallback
load_dotenv()  # load .env if present

app = FastAPI(title="Dlanos Restaurant Chat API", version="0.1.0")

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://www.dlanosrestaurant.ca",
    "null",  # allow file:// origins for quick local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


# Global singletons
CACHE = LRUCache(capacity=128)
PROVIDER = ChatProvider()
RESTAURANT: Dict = {}


@app.on_event("startup")
async def startup_event():
    global RESTAURANT
    # Warm load the restaurant profile
    RESTAURANT = load_restaurant()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> Dict[str, object]:
    return {
        "name": "Dlanos Restaurant Chat API",
        "version": "0.1.0",
        "endpoints": ["GET /health", "POST /chat"],
    }


def _normalize_key(text: str) -> str:
    return (text or "").strip().lower()


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    user_text = (req.message or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="message is required")

    # 1) Canned replies (hours/menu/address/phone)
    canned = canned_reply(user_text, RESTAURANT)
    if canned:
        return ChatResponse(reply=canned, source="canned")

    # 2) Cache lookup
    key = _normalize_key(user_text)
    cached = CACHE.get(key)
    if cached:
        return ChatResponse(reply=cached, source="cache")

    # 3) LLM fallback via provider adapter
    system = build_system_prompt(RESTAURANT)
    messages: List[Dict[str, str]] = [{"role": "system", "content": system}]

    # Include short history if provided (capped)
    if req.conversation:
        for m in req.conversation[-6:]:
            messages.append({"role": m.role, "content": m.content})

    messages.append({"role": "user", "content": user_text})

    try:
        reply = await PROVIDER.chat(messages, temperature=0.2, max_tokens=512)
        reply = postprocess(reply)
    except Exception as e:  # noqa: BLE001 - return clean error message
        # Graceful fallback if provider fails
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")

    if reply:
        CACHE.set(key, reply)

    return ChatResponse(reply=reply, source="llm")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
