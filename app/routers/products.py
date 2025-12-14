from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.db.database import SessionLocal
from app.models.models import Product
from app.schemas.schemas import ProductOut, ProductCreate, ProductUpdate
from typing import Dict, Any
from decimal import Decimal

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = []
    for p in products:
        result.append(
            ProductOut(
                id=p.id,
                article=p.article,
                name=p.name,
                purchase_price=float(p.purchase_price) if p.purchase_price else None,
                sell_price=float(p.sell_price) if p.sell_price else None,
                is_active=bool(p.is_active),
                category_id=p.category_id,
                unit_id=p.unit_id
            )
        )
    return result

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductOut(
        id=p.id,
        article=p.article,
        name=p.name,
        purchase_price=float(p.purchase_price) if p.purchase_price else None,
        sell_price=float(p.sell_price) if p.sell_price else None,
        is_active=bool(p.is_active),
        category_id=p.category_id if p.category_id else None,
        unit_id=p.unit_id if p.unit_id else None
    )
    
@router.post("/create")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        # Вызов хранимой процедуры
        sql = text("""
            CALL create_product(
                :article, :name, :purchase_price, :sell_price,
                :category_id, :unit_id
            )
        """)
        
        result = db.execute(sql, {
            'article': product.article,
            'name': product.name,
            'purchase_price': product.purchase_price,
            'sell_price': product.sell_price,
            'is_active': 1,
            'category_id': product.category_id,
            'unit_id': product.unit_id,
        })
        
        db.commit()
        
        # Получаем сообщение из процедуры
        message = result.fetchone()
        
        return {
            "success": True,
            "message": message[0] if message else "Продукт создан успешно"
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        import traceback
        error_details = traceback.format_exc()
        print(f"Полная ошибка: {error_details}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания товара: {str(e)}"
        )
    
@router.put("/{product_id}/update")
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    try:
        sql = text("""
            CALL update_product(
                :p_id, :p_article, :p_name, :p_purchase, :p_sell, :p_active,
                :p_category, :p_unit
            )
        """)
        
        params = {
            'p_id': product_id,
            'p_article': product.article,
            'p_name': product.name,
            'p_purchase': product.purchase_price,
            'p_sell': product.sell_price,
            'p_active': product.is_active,
            'p_category': product.category_id,
            'p_unit': product.unit_id
        }
    
        result = db.execute(sql, params)
        db.commit()
        
        message_row = result.fetchone()
        message = message_row[0] if message_row else "Товар обновлён"
        
        get_sql = text("""
            SELECT 
                id, article, name, purchase_price, sell_price,
                is_active, category_id, unit_id
            FROM Products 
            WHERE id = :product_id
        """)
        
        updated_product = db.execute(get_sql, {'product_id': product_id}).fetchone()
        
        if not updated_product:
            raise HTTPException(
                status_code=404,
                detail=f"Товар с ID {product_id} не найден после обновления"
            )
        
        # 4. Возвращаем полный ответ
        return {
            "success": True,
            "message": message,
            "product": {
                "id": updated_product.id,
                "article": updated_product.article,
                "name": updated_product.name,
                "purchase_price": float(updated_product.purchase_price),
                "sell_price": float(updated_product.sell_price),
                "is_active": bool(updated_product.is_active),
                "category_id": updated_product.category_id,
                "unit_id": updated_product.unit_id
            }
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        import traceback
        error_details = traceback.format_exc()
        print(f"Полная ошибка: {error_details}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления товара: {str(e)}")

@router.delete("/{product_id}/delete")
def delete_product( product_id: int, db: Session = Depends(get_db)):
    try:

        # 1. Вызываем процедуру удаления
        sql = text("CALL delete_product(:p_id)")
        
        result = db.execute(sql, {'p_id': product_id})
        db.commit()
        
        # 2. Получаем сообщение из процедуры
        message_row = result.fetchone()
        message = message_row[0] if message_row else "Товар помечен как удалённый"
        
        print(f"✅ {message}")
        
        # 3. Возвращаем успешный ответ
        return {
            "success": True,
            "message": message,
            "product_id": product_id,
            "deleted_at": None,  # мягкое удаление, можно добавить поле deleted_at если есть
            "is_active": False
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        error_details = traceback.format_exc()
        
        print(f"Ошибка удаления товара {product_id}: {error_details}")
        
        # Обработка SQL ошибок из процедуры
        if "Товар с указанным ID не найден" in error_msg:
            raise HTTPException(
                status_code=404,
                detail=f"Товар с ID {product_id} не найден"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка удаления товара: {error_msg}"
            )

@router.get("/{product_id}/quantity")
def get_product_quantity(
    product_id: int,
    zone_id: int,
    db: Session = Depends(get_db)
):
    try:
        sql = text("""
            SELECT get_inventory_quantity(:product_id, :zone_id) as quantity
            """)
            
        result = db.execute(sql, {
            'product_id': product_id,
            'zone_id': zone_id
        })
            
        quantity = result.scalar()
            
        return {
            "quantity": int(quantity) if quantity is not None else 0
        }
        
            
    except Exception as e:
        # Для отладки выведем полную ошибку
        import traceback
        error_details = traceback.format_exc()
        print(f"Ошибка в get_product_quantity: {error_details}")
        
        # Возвращаем 0 при ошибке, чтобы фронтенд не падал
        return {
            "quantity": 0,
            "error": str(e)
        }
    
@router.get("/{product_id}/fullquantity")
def get_product_full_quantity(
    product_id: int,
    db: Session = Depends(get_db)
):
    try:
        sql = text("""
            SELECT 
                SUM(
                    get_inventory_quantity(
                        :product_id,
                        z.id
                    )
                ) as total_quantity_on_warehouse
            FROM StorageZones z;
            """)
            
        result = db.execute(sql, {
            'product_id': product_id,
        })
        
        quantity = result.scalar()
        print(f"Scalar результат: {quantity}")
        print(f"Тип scalar: {type(quantity)}")

        if isinstance(quantity, Decimal):
            quantity_int = int(quantity)
        else:
            quantity_int = int(quantity) if quantity is not None else 0

        return {
            "quantity": quantity_int
        }
        
            
    except Exception as e:
        # Для отладки выведем полную ошибку
        import traceback
        error_details = traceback.format_exc()
        print(f"Ошибка в get_product_quantity: {error_details}")
        
        # Возвращаем 0 при ошибке, чтобы фронтенд не падал
        return {
            "quantity": 0,
            "error": str(e)
        }    