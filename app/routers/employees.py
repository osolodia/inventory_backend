from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.db.database import SessionLocal
from app.models.models import Employee
from app.schemas.schemas import EmployeeOut, EmployeeUpdate, EmployeeCreate

router = APIRouter(
    prefix="/employees",
    tags=["employees"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[EmployeeOut])
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    result = []
    for employee in employees:
        result.append(
            EmployeeOut(
                id=employee.id,
                login=employee.login,
                password=employee.password,
                first_name=employee.first_name,
                last_name=employee.last_name,
                passport_series = employee.passport_series,
                passport_number = employee.passport_number,
                email = employee.email,
                number_phone = employee.number_phone,
                date_birth = employee.date_birth,
                position_id=employee.position_id,
                subdivision_id=employee.subdivision_id,
                role_id=employee.role_id
            )
        )
    return result

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return EmployeeOut(
        id=employee.id,
        login=employee.login,
        password=employee.password,
        first_name=employee.first_name,
        last_name=employee.last_name,
        passport_series = employee.passport_series,
        passport_number = employee.passport_number,
        email = employee.email,
        number_phone = employee.number_phone,
        date_birth = employee.date_birth,
        position_id=employee.position_id,
        subdivision_id=employee.subdivision_id,
        role_id=employee.role_id
    )

@router.post("/create")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        # Вызов хранимой процедуры
        sql = text("""
            CALL create_employee(
                :login, :password, :first_name, :last_name,
                :passport_series, :passport_number, :email, :number_phone,
                :date_birth, :position_id, :subdivision_id, :role_id
            )
        """)
        
        result = db.execute(sql, {
            'login': employee.login,
            'password': employee.password,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'passport_series': employee.passport_series,
            'passport_number': employee.passport_number,
            'email': employee.email if employee.email else None,
            'number_phone': employee.number_phone if employee.number_phone else None,
            'date_birth': employee.date_birth if employee.date_birth else None,
            'position_id': employee.position_id,
            'subdivision_id': employee.subdivision_id,
            'role_id': employee.role_id
        })
        
        db.commit()
        
        # Получаем сообщение из процедуры
        message = result.fetchone()
        
        return {
            "success": True,
            "message": message[0] if message else "Сотрудник создан успешно"
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        import traceback
        error_details = traceback.format_exc()
        print(f"Полная ошибка: {error_details}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания сотрудника: {str(e)}"
        )

@router.put("/{product_id}/update")
def update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    try:
        # Вызов хранимой процедуры
        sql = text("""
            CALL update_employee(
                :id, :login, :password, :first_name, :last_name,
                :passport_series, :passport_number, :email, :number_phone,
                :date_birth, :position_id, :subdivision_id, :role_id
            )
        """)
        
        params = {
            'id': employee_id,
            'login': employee.login,
            'password': employee.password,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'passport_series': employee.passport_series,
            'passport_number': employee.passport_number,
            'email': employee.email,
            'number_phone': employee.number_phone,
            'date_birth': employee.date_birth,
            'position_id': employee.position_id,
            'subdivision_id': employee.subdivision_id,
            'role_id': employee.role_id
        }
        
        result = db.execute(sql, params)
        
        db.commit()
        
        # Получаем сообщение из процедуры
        message_row = result.fetchone()
        message = message_row[0] if message_row else "Сотрудник обновлён"

        get_sql = text("""
            SELECT 
                id, login, password, first_name, last_name, passport_series, passport_number,
                email, number_phone, date_birth, position_id, subdivision_id, role_id
            FROM employees 
            WHERE id = :employee_id
        """)
        
        updated_employee = db.execute(get_sql, {'employee_id': employee_id}).fetchone()
        
        if not updated_employee:
            raise HTTPException(
                status_code=404,
                detail=f"Сотрудник с ID {employee_id} не найден после обновления"
            )
        
        return {
            "success": True,
            "message": message[0] if message else "Сотрудник создан успешно"
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        import traceback
        error_details = traceback.format_exc()
        print(f"Полная ошибка: {error_details}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления сотрудника: {str(e)}"
        )
    
@router.delete("/{employee_id}/delete")
def delete_employee( employee_id: int, db: Session = Depends(get_db)):
    try:

        # 1. Вызываем процедуру удаления
        sql = text("CALL delete_employee(:p_id)")
        
        result = db.execute(sql, {'p_id': employee_id})
        db.commit()
        
        # 2. Получаем сообщение из процедуры
        message_row = result.fetchone()
        message = message_row[0] if message_row else "Сотрудник удален"
        
        print(f"✅ {message}")
        
        # 3. Возвращаем успешный ответ
        return {
            "success": True,
            "message": message,
            "product_id": employee_id,
            "deleted_at": None,  # мягкое удаление, можно добавить поле deleted_at если есть
            "is_active": False
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        print(f"Ошибка удаления товара {employee_id}")
        
        # Обработка SQL ошибок из процедуры
        if "Сотрудник с указанным ID не найден" in error_msg:
            raise HTTPException(
                status_code=404,
                detail=f"Сотрудник с ID {employee_id} не найден"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка удаления сотрудника: {error_msg}"
            )