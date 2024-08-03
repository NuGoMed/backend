from sqlalchemy.orm import Session
from .models import Email, Surgery, TierList, Partner
from .schemas import EmailSchema, SurgeryCreate, SurgeryUpdate, SurgeryPartialUpdate
import base64

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
    return db.query(Surgery).offset(skip).limit(limit).all()

def delete_surgery(db: Session, surgery_id: int):
    surgery = db.query(Surgery).filter(Surgery.id == surgery_id).first()
    if surgery:
        db.delete(surgery)
        db.commit()
        return surgery
    return None

def update_surgery(db: Session, surgery_id: int, surgery_data: SurgeryUpdate):
    surgery = db.query(Surgery).filter(Surgery.id == surgery_id).first()
    if surgery:
        for key, value in surgery_data.dict(exclude_unset=True).items():
            setattr(surgery, key, value)
        db.commit()
        db.refresh(surgery)
        return surgery
    return None

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
    