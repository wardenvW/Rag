from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from collections.abc import Iterable
from ...models import QueryRequest
from ...db.crud import get_active_documents
from ...db import get_session
import logging

logger = logging.getLogger(__name__)
chat_router = APIRouter()

@chat_router.post("/ask")
def stream_response(query: QueryRequest, request: Request, session: Session = Depends(get_session)) -> Iterable[str]:
    used_documents = get_active_documents(session)
    logger.debug(f"Used documents: {used_documents}")
    headers = {'X-Content-Type-Options:': 'nosniff'}
    return StreamingResponse(
        content=(chunk for chunk in request.app.state.pipeline.stream_answer(query.query, used_documents) if chunk is not None),  #Иногда поток передаёт None чанки
        headers=headers,
        media_type="text/plain"
        )