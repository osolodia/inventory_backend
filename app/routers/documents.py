from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import date
from app.db.database import SessionLocal
from app.models.models import Document, Company, DocumentType  # Убраны лишние импорты
from app.schemas.schemas import DocumentOut, DocumentCreate, DocumentUpdate
import logging
import traceback

logger = logging.getLogger(__name__)

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

@router.get("/", response_model=List[DocumentOut])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    document_type_id: Optional[int] = None,
    company_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    
    # Фильтры
    if document_type_id:
        query = query.filter(Document.document_type_id == document_type_id)
    if company_id:
        query = query.filter(Document.company_id == company_id)
    if start_date:
        query = query.filter(Document.date >= start_date)
    if end_date:
        query = query.filter(Document.date <= end_date)
    
    docs = query.offset(skip).limit(limit).all()
    
    return docs

@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc

@router.post("/", response_model=DocumentOut)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    # Проверяем существование типа документа
    doc_type = db.query(DocumentType).filter(DocumentType.id == document.document_type_id).first()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    
    # Проверяем существование компании (если указана)
    if document.company_id:
        company = db.query(Company).filter(Company.id == document.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
    
    # Создаем документ
    db_doc = Document(**document.dict(exclude={"zone_id", "employee_id"}))
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    return db_doc

@router.post("/create_inv_doc")
def create_inventory_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"🎯 Начало создания документа. Данные: {doc.dict()}")
        
        # Логируем отдельные поля
        logger.info(f"📄 Номер: {doc.number}")
        logger.info(f"📅 Дата: {doc.date}")
        logger.info(f"🔢 Тип документа: {doc.document_type_id}")
        logger.info(f"🏢 company_id: {doc.company_id}")
        logger.info(f" employee_id: {doc.employee_id}")

        sql = text("""
            CALL create_inventory_document(
                :p_zone_id, :p_employee_id)
        """)
        
        result = db.execute(sql, {
            'p_zone_id': doc.zone_id,
            'p_employee_id': doc.employee_id,
        })

        db.commit()

        row = result.fetchone()
        if row:
            document_id = row[0]
            logger.info(f"✅ Документ создан с ID: {document_id}")
            
            # Получаем полные данные документа
            document = db.query(Document).filter(Document.id == document_id).first()
            
            return {
                "success": True,
                "document": document,
                "message": "Document inventory created successfully"
            }
        else:
            logger.error("❌ Процедура не вернула ID документа")
            raise HTTPException(status_code=500, detail="Failed to create document")
            
    except Exception as e:
        logger.error(f"🔥 КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        logger.error(f"🔥 Трассировка:\n{traceback.format_exc()}")
        
        # Откатываем транзакцию
        db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )

@router.post("/create_rec_doc")
def create_receipt_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"🎯 Начало создания документа. Данные: {doc.dict()}")
        
        # Логируем отдельные поля
        logger.info(f"📄 Номер: {doc.number}")
        logger.info(f"📅 Дата: {doc.date}")
        logger.info(f"🔢 Тип документа: {doc.document_type_id}")
        logger.info(f"🏢 company_id: {doc.company_id}")
        logger.info(f" employee_id: {doc.employee_id}")

        sql = text("""
            CALL create_receipt_document(
                :p_company_id, :p_employee_id)
        """)
        
        result = db.execute(sql, {
            'p_company_id': doc.company_id,
            'p_employee_id': doc.employee_id,
        })

        db.commit()

        row = result.fetchone()
        if row:
            document_id = row[0]
            logger.info(f"✅ Документ создан с ID: {document_id}")
            
            # Получаем полные данные документа
            document = db.query(Document).filter(Document.id == document_id).first()
            
            return {
                "success": True,
                "document": document,
                "message": "Document receipt created successfully"
            }
        else:
            logger.error("❌ Процедура не вернула ID документа")
            raise HTTPException(status_code=500, detail="Failed to create document")
            
    except Exception as e:
        logger.error(f"🔥 КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        logger.error(f"🔥 Трассировка:\n{traceback.format_exc()}")
        
        # Откатываем транзакцию
        db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
    
@router.post("/create_trn_doc")
def create_transfer_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"🎯 Начало создания документа. Данные: {doc.dict()}")
        
        # Логируем отдельные поля
        logger.info(f"📄 Номер: {doc.number}")
        logger.info(f"📅 Дата: {doc.date}")
        logger.info(f"🔢 Тип документа: {doc.document_type_id}")
        logger.info(f"🏢 company_id: {doc.company_id}")
        logger.info(f" employee_id: {doc.employee_id}")

        sql = text("""
            CALL create_transfer_document(
                :p_employee_id)
        """)
        
        result = db.execute(sql, {
            'p_employee_id': doc.employee_id,
        })

        db.commit()

        row = result.fetchone()
        if row:
            document_id = row[0]
            logger.info(f"✅ Документ создан с ID: {document_id}")
            
            # Получаем полные данные документа
            document = db.query(Document).filter(Document.id == document_id).first()
            
            return {
                "success": True,
                "document": document,
                "message": "Document transfer created successfully"
            }
        else:
            logger.error("❌ Процедура не вернула ID документа")
            raise HTTPException(status_code=500, detail="Failed to create document")
            
    except Exception as e:
        logger.error(f"🔥 КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        logger.error(f"🔥 Трассировка:\n{traceback.format_exc()}")
        
        # Откатываем транзакцию
        db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
    
@router.post("/create_wrf_doc")
def create_writeoff_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"🎯 Начало создания документа. Данные: {doc.dict()}")
        
        # Логируем отдельные поля
        logger.info(f"📄 Номер: {doc.number}")
        logger.info(f"📅 Дата: {doc.date}")
        logger.info(f"🔢 Тип документа: {doc.document_type_id}")
        logger.info(f"🏢 company_id: {doc.company_id}")
        logger.info(f" employee_id: {doc.employee_id}")

        sql = text("""
            CALL create_writeoff_document(
                :p_company_id, :p_employee_id)
        """)
        
        result = db.execute(sql, {
            'p_company_id': doc.company_id,
            'p_employee_id': doc.employee_id,
        })

        db.commit()

        row = result.fetchone()
        if row:
            document_id = row[0]
            logger.info(f"✅ Документ создан с ID: {document_id}")
            
            # Получаем полные данные документа
            document = db.query(Document).filter(Document.id == document_id).first()
            
            return {
                "success": True,
                "document": document,
                "message": "Document writeoff created successfully"
            }
        else:
            logger.error("❌ Процедура не вернула ID документа")
            raise HTTPException(status_code=500, detail="Failed to create document")
            
    except Exception as e:
        logger.error(f"🔥 КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        logger.error(f"🔥 Трассировка:\n{traceback.format_exc()}")
        
        # Откатываем транзакцию
        db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
    

@router.put("/{document_id}", response_model=DocumentOut)
def update_document(document_id: int, document: DocumentUpdate, db: Session = Depends(get_db)):
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Проверяем существование типа документа (если обновляется)
    if document.document_type_id is not None:  # Изменено на is not None
        doc_type = db.query(DocumentType).filter(DocumentType.id == document.document_type_id).first()
        if not doc_type:
            raise HTTPException(status_code=404, detail="Document type not found")
    
    # Проверяем существование компании (если обновляется)
    if document.company_id is not None:  # Изменено на is not None
        company = db.query(Company).filter(Company.id == document.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
    
    # ВАЖНО: Если документ становится приходным (type_id=1), должен быть указан поставщик
    if document.document_type_id == 1 or (document.document_type_id is None and db_doc.document_type_id == 1):
        if document.company_id is None and db_doc.company_id is None:
            raise HTTPException(
                status_code=400, 
                detail="Для приходного документа должен быть указан поставщик"
            )
    
    # Обновляем поля
    update_data = document.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doc, key, value)
    
    db.commit()
    db.refresh(db_doc)
    
    return db_doc

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Удаляем документ
    db.delete(db_doc)
    db.commit()
    
    return {
        "detail": "Document deleted",
        "document_id": document_id
    }

@router.get("/stats/count")
def get_documents_stats(db: Session = Depends(get_db)):
    # Получаем общее количество документов
    total = db.query(Document).count()
    
    # Получаем количество по типам
    types_stats = db.query(
        DocumentType.name,
        db.func.count(Document.id)
    ).join(Document, DocumentType.id == Document.document_type_id)\
     .group_by(DocumentType.name).all()
    
    return {
        "total_documents": total,
        "by_type": [{"type": name, "count": count} for name, count in types_stats]
    }