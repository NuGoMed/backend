from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel , Field, EmailStr
from pydantic.generics import GenericModel

T = TypeVar('T')

class EmailSchema(BaseModel):
    id: Optional[int] = None
    mail_from: str
    mail_to: str
    subject: str
    message: str

    class Config:
        orm_mode = True

class SurgeryBase(BaseModel):
    surgery: str
    surgery_description: str
    partner_id: int

class SurgeryCreate(BaseModel):
    surgery: str
    surgery_description: str
    partner_id: int

class SurgeryUpdate(SurgeryBase):
    pass

class SurgeryPartialUpdate(BaseModel):
    surgery: str | None = None
    surgery_description: str | None = None

class Surgery(SurgeryBase):
    id: int    

    class Config:
        orm_mode = True


class TierListBase(BaseModel):
    tier: str
    surgery_id: int
    visa_sponsorship: str
    flight_type: str
    number_family_members: str
    hospital_accommodations: str
    hotel: str
    duration_stay: str
    tourism_package: str
    post_surgery_monitoring: str
    price: str

class TierList(TierListBase):
    pass

class TierListResponse(BaseModel):
    status: str
    code: str
    message: str
    result: int
    data: List[TierList]

class TierListUpdate(TierListBase):
    pass


class Request(GenericModel, Generic[T]):
    parameter: Optional[T] = Field(...)


class Response(GenericModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]


class PartnerBase(BaseModel):
    company_name: str
    website: str
    help_type: str
    logo: Optional[str] = None  # Base64-encoded string for logo

class PartnerCreate(BaseModel):
    company_name: str
    website: str
    help_type: str
    logo: Optional[str] = None  # Base64-encoded string for logo

    class Config:
        orm_mode = True


class PartnerUpdate(PartnerBase):
    pass

class Partner(PartnerBase):
    id: int
    surgeries: List['Surgery'] = []

    class Config:
        orm_mode = True


class PartnerResponse(BaseModel):
    status: str
    code: str
    message: str
    result: int
    data: List[Partner]

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None