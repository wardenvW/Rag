from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse, FileResponse
from collections.abc import Iterable
from ...models import QueryRequest
from ...db.crud import get_active_documents
from ...db import get_session

chat_router = APIRouter()

@chat_router.get("/")
def get_chat():
    return FileResponse("index.html")

@chat_router.post("/ask")
def stream_response(query: QueryRequest, request: Request, session: Session = Depends(get_session)) -> Iterable[str]:
    used_documents = get_active_documents(session)
        
    return StreamingResponse(
        content=request.app.pipeline.stream_answer(query.query, used_documents),
        media_type="text/plain"
        )
#TODO: посмотреть вариант media_type="text/event-stream" он позволит более красиво выводить ответ LLM