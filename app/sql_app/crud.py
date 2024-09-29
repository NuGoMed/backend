from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import Email, Surgery, TierList, Partner, PDFFile, User
from .schemas import EmailSchema, SurgeryCreate, SurgeryUpdate, SurgeryPartialUpdate, UserCreate, TierListUpdate, PartnerUpdate, PartnerCreate
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate):
    db_user = User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_email(db: Session, email: EmailSchema) -> Email:
    db_email = Email(
        mail_from=email.mail_from,
        mail_to=email.mail_to,
        subject=email.subject,
        message=email.message
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

async def get_email_by_id(db: Session, email_id: int) -> Email:
    return db.query(Email).filter(Email.id == email_id).first()

def get_surgeries_by_id(db: Session, surgery_id: int):
    return db.query(Surgery).filter(Surgery.id == surgery_id).first()

def get_surgeries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Surgery).order_by(Surgery.id).offset(skip).limit(limit).all()

def delete_surgery(db: Session, surgery_id: int):
    surgery = db.query(Surgery).filter(Surgery.id == surgery_id).first()
    if surgery:
        db.delete(surgery)
        db.commit()
        return surgery
    return None

def update_surgery(db: Session, surgery_id: int, surgery_data: SurgeryUpdate):
    surgery = db.query(Surgery).filter(Surgery.id == surgery_id).first()
    if not surgery:
        return None

    update_data = surgery_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(surgery, key):
            setattr(surgery, key, value)
        else:
            raise ValueError(f"Invalid field: {key}")

    db.commit()
    db.refresh(surgery)
    return surgery


def partial_update_surgery(db: Session, surgery_id: int, surgery_data: SurgeryPartialUpdate):
    surgery = db.query(Surgery).filter(Surgery.id == surgery_id).first()
    if surgery:
        for key, value in surgery_data.dict(exclude_unset=True).items():
            setattr(surgery, key, value)
        db.commit()
        db.refresh(surgery)
        return surgery
    return None

def create_surgery(db: Session, surgery: SurgeryCreate):
    db_surgery = Surgery(
        surgery=surgery.surgery,
        surgery_description=surgery.surgery_description
    )
    db.add(db_surgery)
    db.commit()
    db.refresh(db_surgery)
    return db_surgery

def get_tier_list_by_id(db: Session, tier_list_id: int):
    return db.query(TierList).filter(TierList.id == tier_list_id).first()

def get_tier_lists(db: Session, skip: int = 0, limit: int = 100):
    try:
        tier_lists = db.query(TierList).offset(skip).limit(limit).all()
        return tier_lists
    except Exception as e:
        raise e
    
def update_tier_lists(db: Session, tier_list_id: int, tier_list_data: TierListUpdate):
    tier_list = db.query(TierList).filter(TierList.id == tier_list_id).first()
    if not tier_list:
        return None

    update_data = tier_list_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(tier_list, key):
            setattr(tier_list, key, value)
        else:
            raise ValueError(f"Invalid field: {key}")

    db.commit()
    db.refresh(tier_list)
    return tier_list
    
def get_partner_lists(db: Session, skip: int = 0, limit: int = 100):
    try:
        partners = db.query(Partner).offset(skip).limit(limit).all()
        partners_list = []
        for partner in partners:
            logo_base64 = base64.b64encode(partner.logo).decode('utf-8') if partner.logo else None
            partners_list.append({
                "id": partner.id,
                "company_name": partner.company_name,
                "website": partner.website,
                "help_type": partner.help_type,
                "logo": logo_base64
            })

        return partners_list
    
    except Exception as e:
        raise e
    
def get_partner_by_id(db: Session, partner_id: int):
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            return None
        
        logo_base64 = base64.b64encode(partner.logo).decode('utf-8') if partner.logo else None
        return {
            "id": partner.id,
            "company_name": partner.company_name,
            "website": partner.website,
            "help_type": partner.help_type,
            "logo": logo_base64
        }
    except Exception as e:
        raise e

def delete_partner(db: Session, partner_id: int):
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            return None
        db.delete(partner)
        db.commit()
        return partner
    except Exception as e:
        raise e


def update_partner(db: Session, partner_id: int, partner_data: PartnerUpdate):
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            return None
        for key, value in partner_data.dict(exclude_unset=True).items():
            setattr(partner, key, value)
        db.commit()
        db.refresh(partner)
        
        logo_base64 = base64.b64encode(partner.logo).decode('utf-8') if partner.logo else None
        return {
            "id": partner.id,
            "company_name": partner.company_name,
            "website": partner.website,
            "help_type": partner.help_type,
            "logo": logo_base64
        }
    except Exception as e:
        raise e

def create_partner(db: Session, partner: PartnerCreate):
    try:
        db_partner = Partner(
            company_name=partner.company_name,
            website=partner.website,
            help_type=partner.help_type,
            logo=base64.b64decode(partner.logo) if partner.logo else None
        )
        db.add(db_partner)
        db.commit()
        db.refresh(db_partner)
        return db_partner
    except Exception as e:
        raise e

def create_pdf_file(db: Session, file_name: str, file_data: bytes, description: str):
    db_pdf_file = PDFFile(file_name=file_name, file_data=file_data, description=description)
    db.add(db_pdf_file)
    db.commit()
    db.refresh(db_pdf_file)
    return db_pdf_file

def get_pdf_file(db: Session, file_id: int):
    return db.query(PDFFile).filter(PDFFile.id == file_id).first()

def get_pdf_files(db: Session, skip: int = 0, limit: int = 10):
    return db.query(PDFFile).offset(skip).limit(limit).all()

def delete_pdf_file(db: Session, file_id: int):
    db_pdf_file = db.query(PDFFile).filter(PDFFile.id == file_id).first()
    if db_pdf_file:
        db.delete(db_pdf_file)
        db.commit()
    return db_pdf_file
    