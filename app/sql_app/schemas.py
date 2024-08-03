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

class SurgeryCreate(BaseModel):
    surgery: str
    surgery_description: str

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
    hospital_accomodations: str
    hotel: str
    duration_stay: str
    tourism_package: str
    post_surgery_monitoring: str
    price: str

class TierList(BaseModel):
    tier: str
    surgery_id: int
    visa_sponsorship: str
    flight_type: str
    number_family_members: str
    hospital_accomodations: str
    hotel: str
    duration_stay: str
    tourism_package: str
    post_surgery_monitoring: str
    price: str

class TierListResponse(BaseModel):
    status: str
    code: str
    message: str
    result: int
    data: List[TierList]


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

class PartnerCreate(PartnerBase):
    pass

class Partner(PartnerBase):
    id: int

    class Config:
        orm_mode = True


class PartnerResponse(BaseModel):
    status: str
    code: str
    message: str
    result: int
    data: List[Partner]
