from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(45), nullable=False)
    date = Column(Date, nullable=False)
    comment = Column(String(45))

    company_id = Column(Integer, ForeignKey("companies.id"))
    document_type_id = Column(Integer, ForeignKey("documenttypes.id"), nullable=False)
   
    company = relationship("Company", back_populates="documents")
    
    document_type = relationship("DocumentType", back_populates="documents")

class DocumentType(Base):
    __tablename__ = "documenttypes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(45), nullable=False)

    documents = relationship("Document", back_populates="document_type")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(45), nullable=False)
    
    company_type_id = Column(Integer, ForeignKey("companytypes.id"), nullable=False)

    documents = relationship("Document", back_populates="company")
    
    company_type = relationship("CompanyType", back_populates="companies")

class CompanyType(Base):
    __tablename__ = "companytypes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(45), nullable=False)

    companies = relationship("Company", back_populates="company_type")