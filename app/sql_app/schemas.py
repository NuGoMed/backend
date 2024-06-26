from pydantic import BaseModel

class SurgeriesBase(BaseModel):
    surgery: str
    description: str 

class SurgeriesCreate(SurgeriesBase):
    pass

class Surgeries(SurgeriesBase):
    id: int

    class Config:
        orm_mode: True

class TiersBase(BaseModel):
    tier: str
    visa_sponsorship: str
    flight_type: str
    number_family_numbers: str
    hospital_accomodations: str
    hotel: str
    duration_stay: str
    tourism_package: str
    post_surgery_monitoring: str
    price: str

class TiersCreate(TiersBase):
    pass

class Tiers(TiersBase):
    id: int
    surgery_id: int

    class Config:
        orm_mode: True