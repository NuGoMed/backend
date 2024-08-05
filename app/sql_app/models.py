from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    mail_from = Column(String, index=True)
    mail_to = Column(String, index=True)
    subject = Column(String)
    message = Column(String)

class Partner(Base):
    __tablename__ = 'partners'

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    website = Column(String(100), nullable=False)
    help_type = Column(String(100), nullable=False)
    logo = Column(LargeBinary, nullable=True)  # BLOB for the logo image

    # Relationship to surgeries
    surgeries = relationship("Surgery", back_populates="partner")

class Surgery(Base):
    __tablename__ = 'surgeries'

    id = Column(Integer, primary_key=True, index=True)
    surgery = Column(String(100), nullable=False)
    surgery_description = Column(String(100), nullable=False)
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False)  # Foreign key to partners

    # Relationship to tier lists
    tier_lists = relationship("TierList", back_populates="surgery", cascade="all, delete")
    
    # Relationship to partner
    partner = relationship("Partner", back_populates="surgeries")

class TierList(Base):
    __tablename__ = 'tier_lists'

    id = Column(Integer, primary_key=True, index=True)
    tier = Column(String(50), nullable=False)
    surgery_id = Column(Integer, ForeignKey('surgeries.id'), nullable=False)
    visa_sponsorship = Column(String(100), nullable=False)
    flight_type = Column(String(100), nullable=False)
    number_family_members = Column(String(100), nullable=False)
    hospital_accommodations = Column(String(100), nullable=False)
    hotel = Column(String(100), nullable=False)
    duration_stay = Column(String(100), nullable=False)
    tourism_package = Column(String(100), nullable=False)
    post_surgery_monitoring = Column(String(100), nullable=False)
    price = Column(String(40), nullable=False)

    # Relationship to surgery
    surgery = relationship("Surgery", back_populates="tier_lists", cascade="all, delete")


class PDFFile(Base):
    __tablename__ = 'pdf_files'

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    upload_date = Column(DateTime, server_default=func.now())
    file_data = Column(LargeBinary, nullable=False)
    description = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
