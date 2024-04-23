from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class Surgeries(Base):

    __tablename__ = "surgeries"

    id = Column(Integer, primary_key=True)
    surgery = Column(String, nullable=False)
    surgery_description = Column(String, nullable=False)

class Tiers(Base):

    __tablename__ = "tier_lists"

    id = Column(Integer, primary_key=True)
    tier = Column(String, nullable=False)
    surgery_id = Column(Integer, ForeignKey('surgeries.id', ondelete='CASCADE'), unique=True)
    visa_sponsorship = Column(String, nullable=False)
    flight_type = Column(String, nullable=False)
    number_family_members = Column(String)
    hospital_accomodations = Column(String, nullable=False)
    hotel = Column(String, nullable=False)
    duration_stay = Column(String, nullable=False)
    tourism_package = Column(String, nullable=False)
    post_surgery_monitoring = Column(String, nullable=False)
    price = Column(String, nullable=False)