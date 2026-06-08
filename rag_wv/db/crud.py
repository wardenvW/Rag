from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from ..models import DocumentNode

#refresh не нужен т.к в database.py стоит expire_on_commit=False

def get_all_documents(db: Session):
    return db.scalars(select(DocumentNode)).all()


def get_document(db: Session, id: str):
    return db.scalar(select(DocumentNode).where(DocumentNode.id == id))

def get_active_documents(db: Session):
    return db.scalars(select(DocumentNode).where(DocumentNode.is_using == True)).all()

def toggle_document(db: Session, id: str):
    document = db.scalar(update(DocumentNode).where(DocumentNode.id == id).values(is_using= ~DocumentNode.is_using).returning(DocumentNode))
    db.commit()
    return document
    

def add_document(db: Session, document: DocumentNode):
    db.add(document)
    db.commit()
    return document
    

def delete_document(db: Session, id: str):
    stmt = delete(DocumentNode).where(DocumentNode.id == id)
    db.execute(stmt)
    db.commit()
    return id

    

