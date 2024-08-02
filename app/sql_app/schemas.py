from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel , Field, EmailStr
from pydantic.generics import GenericModel

T = TypeVar('T')


class BookSchema(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True

class EmailSchema(BaseModel):
    id: Optional[int] = None
    mail_from: str
    mail_to: str
    subject: str
    message: str

    class Config:
        orm_mode = True

class Book(BookSchema):
    id: int

    class Config:
        orm_mode = True


class Request(GenericModel, Generic[T]):
    parameter: Optional[T] = Field(...)


class RequestBook(BaseModel):
    parameter: BookSchema = Field(...)


class Response(GenericModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]