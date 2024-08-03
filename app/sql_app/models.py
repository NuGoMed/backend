from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    mail_from = Column(String, index=True)
    mail_to = Column(String, index=True)
    subject = Column(String)
    message = Column(String)

class Surgery(Base):
    __tablename__ = 'surgeries'

    id = Column(Integer, primary_key=True, index=True)
    surgery = Column(String(100), nullable=False)
    surgery_description = Column(String(100), nullable=False)

    # Relationship to tier lists
    tier_lists = relationship("TierList", back_populates="surgery", cascade="all, delete")



class TierList(Base):
    __tablename__ = 'tier_lists'

    id = Column(Integer, primary_key=True, index=True)
    tier = Column(String(50), nullable=False)
    surgery_id = Column(Integer, ForeignKey('surgeries.id'), nullable=False)
    visa_sponsorship = Column(String(100), nullable=False)
    flight_type = Column(String(100), nullable=False)
    number_family_members = Column(String(100), nullable=False)
    hospital_accomodations = Column(String(100), nullable=False)
    hotel = Column(String(100), nullable=False)
    duration_stay = Column(String(100), nullable=False)
    tourism_package = Column(String(100), nullable=False)
    post_surgery_monitoring = Column(String(100), nullable=False)
    price = Column(String(40), nullable=False)

    # Relationship to surgery
    surgery = relationship("Surgery", back_populates="tier_lists", cascade="all, delete")

class Partner(Base):
    __tablename__ = 'partners'

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    website = Column(String(100), nullable=False)
    help_type = Column(String(100), nullable=False)
    logo = Column(LargeBinary, nullable=True)  # BLOB for the logo image