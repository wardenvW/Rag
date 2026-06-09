from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from collections.abc import Iterable
from ...models import QueryRequest
from ...db.crud import get_active_documents
from ...db import get_session

chat_router = APIRouter()

@chat_router.post("/ask")
def stream_response(query: QueryRequest, request: Request, session: Session = Depends(get_session)) -> Iterable[str]:
    used_documents = get_active_documents(session)
        
    return StreamingResponse(
        content=(chunk for chunk in request.app.state.pipeline.stream_answer(query.query, used_documents) if chunk is not None),  #Иногда поток передаёт None чанки
        media_type="text/plain"
        )
#TODO: посмотреть вариант media_type="text/event-stream" он позволит более красиво выводить ответ LLM