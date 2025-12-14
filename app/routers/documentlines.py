from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import SessionLocal
from app.models.models import DocumentLine, Product, StorageZone, Document
from app.schemas.schemas import DocumentLineOut, DocumentLineCreate, DocumentLineUpdate

router = APIRouter(
    prefix="/documentlines",
    tags=["documentlines"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/document/{document_id}", response_model=List[DocumentLineOut])
def get_document_lines(
    document_id: int, 
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Проверяем существование документа
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Получаем строки документа
    lines = db.query(DocumentLine)\
             .filter(DocumentLine.document_id == document_id)\
             .offset(skip)\
             .limit(limit)\
             .all()
    
    return lines

@router.post("/", response_model=DocumentLineOut)
def create_document_line(document_line: DocumentLineCreate, db: Session = Depends(get_db)):
    # Проверяем существование документа
    document = db.query(Document).filter(Document.id == document_line.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Проверяем существование товара
    product = db.query(Product).filter(Product.id == document_line.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверяем зону отправителя (если указана)
    if document_line.storage_zone_sender_id:
        sender_zone = db.query(StorageZone).filter(StorageZone.id == document_line.storage_zone_sender_id).first()
        if not sender_zone:
            raise HTTPException(status_code=404, detail="Sender storage zone not found")
    
    # Проверяем зону получателя (если указана)
    if document_line.storage_zone_receiver_id:
        receiver_zone = db.query(StorageZone).filter(StorageZone.id == document_line.storage_zone_receiver_id).first()
        if not receiver_zone:
            raise HTTPException(status_code=404, detail="Receiver storage zone not found")
    
    # Создаем строку документа
    db_line = DocumentLine(**document_line.dict())
    db.add(db_line)
    db.commit()
    db.refresh(db_line)
    
    return db_line

@router.put("/{line_id}", response_model=DocumentLineOut)
def update_document_line(
    line_id: int, 
    document_line: DocumentLineUpdate,  # Используем схему для обновления
    db: Session = Depends(get_db)
):
    db_line = db.query(DocumentLine).filter(DocumentLine.id == line_id).first()
    if not db_line:
        raise HTTPException(status_code=404, detail="Document line not found")
    
    # Проверяем существование товара (если обновляется)
    if document_line.product_id:
        product = db.query(Product).filter(Product.id == document_line.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверяем зону отправителя (если обновляется)
    if document_line.storage_zone_sender_id:
        sender_zone = db.query(StorageZone).filter(StorageZone.id == document_line.storage_zone_sender_id).first()
        if not sender_zone:
            raise HTTPException(status_code=404, detail="Sender storage zone not found")
    
    # Проверяем зону получателя (если обновляется)
    if document_line.storage_zone_receiver_id:
        receiver_zone = db.query(StorageZone).filter(StorageZone.id == document_line.storage_zone_receiver_id).first()
        if not receiver_zone:
            raise HTTPException(status_code=404, detail="Receiver storage zone not found")
    
    # Обновляем только переданные поля
    update_data = document_line.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_line, key, value)
    
    db.commit()
    db.refresh(db_line)
    
    return db_line

@router.delete("/{line_id}")
def delete_document_line(line_id: int, db: Session = Depends(get_db)):
    db_line = db.query(DocumentLine).filter(DocumentLine.id == line_id).first()
    if not db_line:
        raise HTTPException(status_code=404, detail="Document line not found")
    
    db.delete(db_line)
    db.commit()
    
    return {"message": f"Document line {line_id} deleted successfully"}