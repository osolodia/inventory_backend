from pydantic import BaseModel
from datetime import date
from typing import Optional, List

# CompanyType
class CompanyTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class CompanyTypeCreate(BaseModel):
    name: str

# Company
class CompanyOut(BaseModel):
    id: int
    name: str
    company_type: Optional[str] = None

    class Config:
        orm_mode = True

class CompanyCreate(BaseModel):
    name: str
    company_type_id: int

# DocumentType
class DocumentTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class DocumentTypeCreate(BaseModel):
    name: str

# DocumentLine
class DocumentLineOut(BaseModel):
    id: int
    quantity: int
    actual_quantity: Optional[int] = None
    product_id: int
    document_id: int
    storage_zone_sender_id: Optional[int] = None
    storage_zone_receiver_id: Optional[int] = None

    class Config:
        orm_mode = True

class DocumentLineCreate(BaseModel):
    quantity: int
    actual_quantity: Optional[int] = None
    product_id: int
    document_id: int
    storage_zone_sender_id: Optional[int] = None
    storage_zone_receiver_id: Optional[int] = None

class DocumentLineUpdate(BaseModel):
    quantity: Optional[int] = None
    actual_quantity: Optional[int] = None
    product_id: Optional[int] = None
    storage_zone_sender_id: Optional[int] = None
    storage_zone_receiver_id: Optional[int] = None

# Document
class DocumentOut(BaseModel):
    id: int
    number: str
    date: date
    comment: Optional[str] = None
    company_id: Optional[int] = None
    document_type_id: int

    class Config:
        orm_mode = True

class DocumentCreate(BaseModel):
    number: str
    date: date
    comment: Optional[str] = None
    company_id: Optional[int] = None
    document_type_id: int

class DocumentUpdate(BaseModel):
    number: Optional[str] = None
    date: Optional[str] = None
    comment: Optional[str] = None
    company_id: Optional[int] = None
    document_type_id: Optional[int] = None

# Category 
class CategoryOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class CategoryCreate(BaseModel):
    name: str

# Employee
class EmployeeOut(BaseModel):
    id: int
    login: str
    password: str
    first_name: str
    last_name: str
    passport_series: int
    passport_number: int
    email: Optional[str] = None
    number_phone: Optional[str] = None
    date_birth: Optional[date] = None
    position_id: int
    subdivision_id: int
    role_id: int

    class Config:
        orm_mode = True

class EmployeeCreate(EmployeeOut):
    pass

class EmployeeUpdate(BaseModel):
    id: Optional[int] = None
    login: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    passport_series: Optional[int] = None
    passport_number: Optional[int] = None
    email: Optional[str] = None
    number_phone: Optional[str] = None
    date_birth: Optional[str] = None
    position_id: Optional[int] = None
    subdivision_id: Optional[int] = None
    role_id: Optional[int] = None

# Unit
class UnitOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class UnitCreate(BaseModel):
    name: str

# Product 
class ProductOut(BaseModel):
    id: int
    article: int
    name: str
    purchase_price: Optional[float] = None
    sell_price: Optional[float] = None
    is_active: Optional[bool] = None
    category_id: int
    unit_id: int

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    article: int
    name: str
    purchase_price: Optional[float] = None
    sell_price: Optional[float] = None
    is_active: bool = True
    category_id: int
    unit_id: int

class ProductUpdate(BaseModel):
    article: Optional[int] = None
    name: Optional[str] = None
    purchase_price: Optional[float] = None
    sell_price: Optional[float] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None

# StorageCondition
class StorageConditionOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class StorageConditionCreate(BaseModel):
    name: str

# StorageZone
class StorageZoneOut(BaseModel):
    id: int
    name: str
    comment: str
    storage_condition: Optional[str] = None

    class Config:
        orm_mode = True

class StorageZoneCreate(BaseModel):
    name: str
    comment: str
    storage_condition_id: int

class Role(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Position(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Subdivision(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True