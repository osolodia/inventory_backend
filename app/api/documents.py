from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import Document

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", tags=["documents"])
def get_documents(db: Session = Depends(get_db)):
    # return [{"name":"hello documents"}]
    docs = db.query(Document).all()
    return [
        {
            "id" : doc.id,
            "number" : doc.number,
            "date" : doc.date.isoformat(),
            "comment" : doc.comment,
            "company": doc.company.name if doc.company else None,
            "document_type": doc.document_type.name if doc.document_type else None
        }
        for doc in docs
    ]
@router.get("/{document_id}", tags=["documents"])
def get_document_by_id(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
      
    return {
        "id": doc.id,
        "number": doc.number,
        "date": doc.date.isoformat(),
        "comment": doc.comment,
        "company": doc.company.name if doc.company else None,
        "document_type": doc.document_type.name if doc.document_type else None
    }
    