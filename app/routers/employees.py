from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.db.database import SessionLocal
from app.models.models import Employee
from app.schemas.schemas import EmployeeOut, EmployeeUpdate, EmployeeCreate
from sqlalchemy.exc import DBAPIError

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

MAX_LOGIN_ATTEMPTS = 10
@router.post("/create")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    base_login = employee.login
    login = base_login

    for attempt in range(MAX_LOGIN_ATTEMPTS):
        try:
            sql = text("""
                CALL create_employee(
                    :login, :password, :first_name, :last_name,
                    :passport_series, :passport_number, :email, :number_phone,
                    :date_birth, :position_id, :subdivision_id, :role_id
                )
            """)

            db.execute(sql, {
                "login": login,
                "password": employee.password,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "passport_series": employee.passport_series,
                "passport_number": employee.passport_number,
                "email": employee.email,
                "number_phone": employee.number_phone,
                "date_birth": employee.date_birth,
                "position_id": employee.position_id,
                "subdivision_id": employee.subdivision_id,
                "role_id": employee.role_id,
            })

            db.commit()

            return {
                "success": True,
                "login": login,
                "message": "Сотрудник создан успешно"
            }

        except DBAPIError as e:
            db.rollback()
            error_message = str(e.orig)

            if "логином уже существует" in error_message:
                login = f"{base_login}{attempt + 1}"
                continue

            raise HTTPException(
                status_code=400,
                detail=error_message
            )

@router.put("/{employee_id}/update")
def update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    try:
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

        # Получаем сообщение из процедуры (если есть)
        message_row = result.fetchone()
        message = message_row[0] if message_row else "Сотрудник обновлён"

        # Возвращаем обновлённого сотрудника
        get_sql = text("""
            SELECT 
                id, login, password, first_name, last_name, passport_series, passport_number,
                email, number_phone, date_birth, position_id, subdivision_id, role_id
            FROM employees 
            WHERE id = :employee_id
        """)
        updated_employee = db.execute(get_sql, {'employee_id': employee_id}).fetchone()
        if not updated_employee:
            raise HTTPException(status_code=404, detail=f"Сотрудник с ID {employee_id} не найден после обновления")

        return {
            "success": True,
            "message": message,
            "employee": dict(updated_employee._mapping)  # Преобразуем Row в dict
        }

    except pymysql.err.OperationalError as e:
        # Ловим SIGNAL SQLSTATE из процедуры
        if e.args[0] == 1644:  # SIGNAL из процедуры
            raise HTTPException(status_code=400, detail=e.args[1])
        raise HTTPException(status_code=500, detail=f"Ошибка обновления сотрудника: {str(e)}")

    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Полная ошибка: {error_details}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления сотрудника: {str(e)}")

    
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