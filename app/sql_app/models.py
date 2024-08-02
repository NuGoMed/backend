from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Book(Base):
    __tablename__ ="book"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    mail_from = Column(String, index=True)
    mail_to = Column(String, index=True)
    subject = Column(String)
    message = Column(String)