from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime, func, Boolean, Date, Text
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
    small_description = Column(Text, nullable=False)
    large_description = Column(Text, nullable=False)
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

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    national_id_number = Column(String, nullable=True, unique=True)
    passport_number = Column(String, nullable=True, unique=True)
    tin_number = Column(String, nullable=True, unique=True)
    country_of_origin = Column(String, nullable=False)
    denied_visa = Column(Boolean, nullable=False)

    buys = relationship("Buy", back_populates="customer")

class Buy(Base):
    __tablename__ = 'buys'

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key references to the Customer, Surgery, and TierList tables
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    surgery_id = Column(Integer, ForeignKey('surgeries.id'), nullable=False)
    tier_list_id = Column(Integer, ForeignKey('tier_lists.id'), nullable=False)

    # Adding a price field (assuming it's a float)
    price = Column(String, nullable=False)

    # File fields
    valid_photo = Column(LargeBinary, nullable=True)  # Store file as binary data
    id_scan = Column(LargeBinary, nullable=True)
    medical_dossier = Column(LargeBinary, nullable=True)
    trip_clearance_doc = Column(LargeBinary, nullable=True)
    schengen_area = Column(Boolean, nullable=False)
    oral_care_implant_plan = Column(LargeBinary, nullable=True)
    hair_care_implant_plan = Column(LargeBinary, nullable=True)
    visa_documents = Column(LargeBinary, nullable=True)
    visa_application_form = Column(LargeBinary, nullable=True)
    identical_photos = Column(LargeBinary, nullable=True)
    passport_copy = Column(LargeBinary, nullable=True)
    medical_travel_insurance = Column(LargeBinary, nullable=True)
    proof_of_financial_means = Column(LargeBinary, nullable=True)
    guarantee_letter = Column(LargeBinary, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="buys")
    surgery = relationship("Surgery")  # Relationship to Surgery
    tier_list = relationship("TierList")  # Relationship to TierList

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
