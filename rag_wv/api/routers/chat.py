from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from collections.abc import Iterable

chat_router = APIRouter()

@chat_router.get("/")
def get_chat():
    pass

@chat_router.get("/stream", response_class=StreamingResponse)
def stream_response(response: str) -> Iterable[str]:
    for line in response.splitlines():
        yield line