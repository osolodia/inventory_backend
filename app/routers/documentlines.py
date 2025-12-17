from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
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

from sqlalchemy import text

@router.get("/document/{document_id}")
def get_document_lines_debug(
    document_id: int, 
    db: Session = Depends(get_db)
):
    """Версия с правильным использованием text()"""
    print(f"=== DEBUG: Getting lines for document {document_id} ===")
    
    try:
        # 1. Проверяем подключение к БД (правильно)
        print("1. Testing DB connection...")
        db.execute(text("SELECT 1")).fetchone()
        print("   ✓ DB connection OK")
        
        # 2. Проверяем документ
        print(f"2. Looking for document ID={document_id}...")
        document = db.query(Document).filter(Document.id == document_id).first()
        print(f"   Document found: {bool(document)}")
        
        if not document:
            print(f"   ✗ Document {document_id} NOT FOUND")
            return {"error": f"Document {document_id} not found", "status": 404}
        
        # 3. Проверяем таблицу document_lines
        print("3. Checking document_lines table...")
        try:
            count = db.query(DocumentLine).count()
            print(f"   Total lines in DB: {count}")
        except Exception as e:
            print(f"   ✗ Error counting lines: {str(e)}")
            print(f"   Error type: {type(e)}")
            import traceback
            traceback.print_exc()
        
        # 4. Получаем строки
        print(f"4. Getting lines for document {document_id}...")
        lines = db.query(DocumentLine)\
                 .filter(DocumentLine.document_id == document_id)\
                 .all()
        
        print(f"   Found {len(lines)} lines")
        
        # 5. Преобразуем в словари
        result = []
        for line in lines:
            result.append({
                "id": line.id,
                "document_id": line.document_id,
                "product_id": line.product_id,
                "quantity": line.quantity,
                "actual_quantity": line.actual_quantity,
                "storage_zone_sender_id": line.storage_zone_sender_id,
                "storage_zone_receiver_id": line.storage_zone_receiver_id
            })
            print(f"   - Line {line.id}: product={line.product_id}, qty={line.quantity}, actual_qty={line.actual_quantity}")
        
        return {
            "document_id": document_id,
            "lines_count": len(lines),
            "lines": result
        }
        
    except Exception as e:
        print(f"=== CRITICAL ERROR ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "type": type(e).__name__, "status": 500}

@router.post("/", response_model=dict)
def create_document_line(document_line: DocumentLineCreate, db: Session = Depends(get_db)):
    """
    Создание строки документа через хранимую процедуру add_document_line
    """
    try:
        print(f"📝 Creating line: doc={document_line.document_id}, product={document_line.product_id}")
        
        # Подготавливаем параметры
        params = {
            "p_document_id": document_line.document_id,
            "p_product_id": document_line.product_id,
            "p_quantity": document_line.quantity,
            "p_actual_quantity": document_line.actual_quantity,
            "p_storage_from": document_line.storage_zone_sender_id or None,
            "p_storage_to": document_line.storage_zone_receiver_id or None
        }
        
        print(f"🔍 Procedure params: {params}")
        
        # ВАРИАНТ 1: Вызов процедуры с получением результата
        sql = text("""
            CALL add_document_line(
                :p_document_id, 
                :p_product_id, 
                :p_quantity, 
                :p_actual_quantity, 
                :p_storage_from, 
                :p_storage_to
            )
        """)
        
        result = db.execute(sql, params)
        
        # Получаем результат из процедуры
        procedure_result = result.fetchone()
        
        # Процедура возвращает: message, new_id
        if procedure_result:
            message = procedure_result[0]  # 'Строка добавлена к документу'
            new_id = procedure_result[1] if len(procedure_result) > 1 else None
        else:
            # Если процедура не вернула результат, получаем последний ID
            message = "Строка добавлена"
            result = db.execute(text("SELECT LAST_INSERT_ID()"))
            new_id = result.scalar()
        
        # Фиксируем изменения
        db.commit()
        
        # Получаем созданную строку
        if new_id:
            last_line = db.query(DocumentLine).filter(DocumentLine.id == new_id).first()
        else:
            # Если не получили ID, ищем последнюю строку для этого документа
            last_line = db.query(DocumentLine)\
                         .filter(DocumentLine.document_id == document_line.document_id)\
                         .order_by(DocumentLine.id.desc())\
                         .first()
        
        return {
            "message": message,
            "line_id": last_line.id if last_line else new_id,
            "line": DocumentLineOut.from_orm(last_line) if last_line else None
        }
            
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        print(f"❌ Error creating document line: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Обработка ошибок
        error_lower = error_msg.lower()
        if "документ с таким id не найден" in error_lower:
            raise HTTPException(status_code=404, detail="Document not found")
        elif "товар с таким id не найден" in error_lower:
            raise HTTPException(status_code=404, detail="Product not found or inactive")
        elif "этот товар уже есть в документе" in error_lower:
            raise HTTPException(status_code=409, detail="Product already exists in document")
        elif "не найден" in error_lower:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=f"Error creating document line: {error_msg}")

@router.post("/test-sql/", response_model=dict)
def test_direct_sql(
    document_id: int,
    product_id: int,
    quantity: int = 1,
    actual_quantity: Optional[int] = None,
    storage_from: Optional[int] = None,
    storage_to: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Тестовый прямой SQL запрос"""
    print(f"🧪 TEST SQL: doc={document_id}, product={product_id}")
    
    try:
        # 1. Сначала просто проверьте доступность таблицы
        test_query = text("SELECT 1 FROM documentlines LIMIT 1")
        db.execute(test_query)
        print("✅ Таблица documentlines доступна")
        
        # 2. Простой INSERT
        sql = text("""
            INSERT INTO documentlines 
            (document_id, product_id, quantity, actual_quantity, storage_zone_sender_id, storage_zone_receiver_id)
            VALUES 
            (:doc_id, :prod_id, :qty, :actual_qty, :from_zone, :to_zone)
        """)
        
        params = {
            "doc_id": document_id,
            "prod_id": product_id,
            "qty": quantity,
            "actual_qty": actual_quantity,
            "from_zone": storage_from,
            "to_zone": storage_to
        }
        
        print(f"🔍 SQL: {sql}")
        print(f"🔍 Параметры: {params}")
        
        result = db.execute(sql, params)
        db.commit()
        
        print(f"✅ Успешно! ID строки: {result.lastrowid}")
        
        return {
            "success": True,
            "message": "Строка создана",
            "line_id": result.lastrowid
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.put("/{line_id}", response_model=dict)
def update_document_line(
    line_id: int, 
    document_line: DocumentLineUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление строки документа через хранимую процедуру update_document_line
    """
    # Проверяем, что есть хотя бы одно поле для обновления
    if all(value is None for value in document_line.dict().values()):
        raise HTTPException(status_code=400, detail="No fields to update")
    
    try:
        # Используем текущие значения, если новые не предоставлены
        existing_line = db.query(DocumentLine).filter(DocumentLine.id == line_id).first()
        if not existing_line:
            raise HTTPException(status_code=404, detail="Document line not found")
        
        # Подготавливаем параметры с actual_quantity
        params = {
            "p_line_id": line_id,
            "p_quantity": document_line.quantity if document_line.quantity is not None else existing_line.quantity,
            "p_actual_quantity": document_line.actual_quantity if document_line.actual_quantity is not None else existing_line.actual_quantity,
            "p_storage_from": document_line.storage_zone_sender_id if document_line.storage_zone_sender_id is not None else existing_line.storage_zone_sender_id,
            "p_storage_to": document_line.storage_zone_receiver_id if document_line.storage_zone_receiver_id is not None else existing_line.storage_zone_receiver_id
        }
        
        # Вызываем обновленную хранимую процедуру update_document_line
        result = db.execute(
            text("CALL update_document_line(:p_line_id, :p_quantity, :p_actual_quantity, :p_storage_from, :p_storage_to)"),
            params
        )
        
        # Получаем результат процедуры
        message = result.fetchone()[0] if result.rowcount > 0 else "Строка документа обновлена"
        
        # Фиксируем изменения
        db.commit()
        
        # Получаем обновленную строку
        updated_line = db.query(DocumentLine).filter(DocumentLine.id == line_id).first()
        
        return {
            "message": message,
            "line_id": line_id,
            "line": DocumentLineOut.from_orm(updated_line) if updated_line else None
        }
            
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        if "Строка документа с таким ID не найдена" in error_msg:
            raise HTTPException(status_code=404, detail="Document line not found")
        elif "не найдена" in error_msg.lower() or "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=f"Error updating document line: {error_msg}")

@router.delete("/{line_id}")
def delete_document_line(line_id: int, db: Session = Depends(get_db)):
    """
    Удаление строки документа
    """
    db_line = db.query(DocumentLine).filter(DocumentLine.id == line_id).first()
    if not db_line:
        raise HTTPException(status_code=404, detail="Document line not found")
    
    try:
        db.delete(db_line)
        db.commit()
        return {"message": f"Document line {line_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting document line: {str(e)}")

@router.get("/{line_id}", response_model=DocumentLineOut)
def get_document_line(line_id: int, db: Session = Depends(get_db)):
    """
    Получение конкретной строки документа по ID
    """
    db_line = db.query(DocumentLine).filter(DocumentLine.id == line_id).first()
    if not db_line:
        raise HTTPException(status_code=404, detail="Document line not found")
    
    return db_line