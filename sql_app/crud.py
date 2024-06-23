from sqlalchemy.orm import Session
from . import models,schemas

def get_surgery(db: Session ,surgery_id: int):
    db.query(models.Surgeries).filter(models.Surgeries.id == surgery_id)

def get_tiers_by_surgery(db: Session, surgery_id: int):
    db.query(models.Tiers).filter(models.Tiers.surgery_id == surgery_id)