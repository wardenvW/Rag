from fastapi import APIRouter, UploadFile, Depends, HTTPException, BackgroundTasks, Request, Form, File
from sqlalchemy.orm import Session
from qdrant_client.http import models
from ...db.database import get_session
from ...db.crud import get_all_documents, get_document, add_document, delete_document, toggle_document
from ...models import DocumentResponse, DeleteResponse, DocumentNode
from ...utils import get_doc_hash, save_to_local, remove_local_file
from ...pipeline import Pipeline
from ...vectorbd import VectorStorage
from ...config import COLLECTION_NAME, ALLOWED_FILE_EXTENSIONS
from pathlib import Path

document_router = APIRouter()

def get_pipeline(request: Request) -> Pipeline:
    return request.app.state.pipeline

def get_vdatabase(request: Request) -> VectorStorage:
    return request.app.state.vector_db

@document_router.get("/", response_model=list[DocumentResponse], status_code=200)
def list_documents(session: Session = Depends(get_session)):
    return get_all_documents(session)

@document_router.get("/{doc_id}", response_model=DocumentResponse, status_code=200)
def read_document(doc_id: str, session: Session = Depends(get_session)):
    doc = get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@document_router.post("/upload", response_model=DocumentResponse, status_code=201)
def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...), file_type: str = Form(...), ppl: Pipeline = Depends(get_pipeline), session: Session = Depends(get_session)):
    file_extension = Path(file.filename).suffix
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Not allowed document extension")

    doc_hash = get_doc_hash(file.file)
    exist_doc = get_document(session, doc_hash)
    if exist_doc:
        raise HTTPException(status_code=400, detail="Document already exists")

    file.file.seek(0)
    doc_path = save_to_local(file, doc_hash)
    file.file.seek(0)
    doc = DocumentNode(id=doc_hash, filename=file.filename, filesize=file.size, doc_type=file_type)
    background_tasks.add_task(ppl.process, [Path(doc_path)], file_type)
    
    return add_document(session, doc)
        
@document_router.delete("/{doc_id}", response_model=DeleteResponse, status_code=200)
def remove_document(doc_id: str, background_tasks: BackgroundTasks, vdb: VectorStorage = Depends(get_vdatabase), session: Session = Depends(get_session)):

    exist_doc = get_document(session, doc_id)
    if not exist_doc:
        raise HTTPException(status_code=400, detail="Document doesn't exist")
    
    background_tasks.add_task(
        vdb.client.delete,
        COLLECTION_NAME,
        points_selector = models.FilterSelector(
            filter = models.Filter(
                must = [
                    models.FieldCondition(
                        key="doc_hash",
                        match=models.MatchValue(value=doc_id)
                    )
                ]
            )
        )
    )
    deleted_id =  delete_document(session, doc_id)
    doc_path = f"{exist_doc.id}_{exist_doc.filename}"
    remove_local_file(doc_path)

    return {"id": deleted_id}

@document_router.patch("/{doc_id}/toggle", response_model=DocumentResponse, status_code=200)
def change_document_state(doc_id: str, session: Session = Depends(get_session)):
    doc = toggle_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
