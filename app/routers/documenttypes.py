from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.models.models import DocumentType
from app.schemas.schemas import DocumentTypeOut, DocumentTypeCreate

router = APIRouter(
    prefix="/documenttypes",
    tags=["documenttypes"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[DocumentTypeOut])
def get_document_types(db: Session = Depends(get_db)):
    return db.query(DocumentType).all()

@router.get("/{document_type_id}", response_model=DocumentTypeOut)
def get_document_type(document_type_id: int, db: Session = Depends(get_db)):
    doc_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not doc_type:
        raise HTTPException(status_code=404, detail="DocumentType not found")
    return doc_type
