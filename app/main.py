import logging, os, aiosmtplib
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.future import select
from dotenv import load_dotenv
from sql_app import models, crud, schemas, database
from email.message import EmailMessage
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "https://nugomed.com:3000",
    "http://nugomed.com",
    "https://nugomed.com",
    "http://www.nugomed.com",
    "https://www.nugomed.com"
]

app.add_middleware(
CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def main():
    return {"message": "Hello World"}

async def send_email(email: str, subject: str, message: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_host or not smtp_user or not smtp_password:
        logger.error("SMTP configuration is incomplete.")
        raise HTTPException(status_code=500, detail="SMTP configuration is incomplete")

    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = email
    msg["Subject"] = subject
    msg.set_content(message)

    try:
        if smtp_port == 587:
            await aiosmtplib.send(
                msg,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                use_tls=True
            )
        elif smtp_port == 465:
            await aiosmtplib.send(
                msg,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                use_tls=True
            )
        else:
            logger.error(f"Unsupported SMTP port: {smtp_port}")
            raise HTTPException(status_code=500, detail="Unsupported SMTP port")

        logger.info(f"Email sent to {email} with subject '{subject}'")
    except aiosmtplib.SMTPConnectError as e:
        logger.error(f"SMTPConnectError: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to SMTP server")
    except aiosmtplib.SMTPException as e:
        logger.error(f"SMTPException: {e}")
        raise HTTPException(status_code=500, detail="SMTP server returned an error response")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.post("/send-email/")
async def send_email_endpoint(email: schemas.EmailSchema, db: AsyncSession = Depends(get_db)):
    await send_email(email.mail_to, email.subject, email.message)
    db_email = crud.create_email(db, email)
    return {"message": "Email has been sent", "email_id": db_email.id}

@app.get("/surgeries", response_model=list[schemas.Surgery])
async def read_surgeries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_surgeries(db, skip=skip, limit=limit)

@app.get("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def read_surgery(surgery_id: int, db: Session = Depends(get_db)):
    surgery = crud.get_surgeries_by_id(db, surgery_id=surgery_id)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.delete("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def delete_surgery(surgery_id: int, db: Session = Depends(get_db)):
    surgery = crud.delete_surgery(db, surgery_id=surgery_id)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.put("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def update_surgery(surgery_id: int, surgery_data: schemas.SurgeryUpdate, db: Session = Depends(get_db)):
    surgery = crud.update_surgery(db, surgery_id=surgery_id, surgery_data=surgery_data)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.patch("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def partial_update_surgery(surgery_id: int, surgery_data: schemas.SurgeryPartialUpdate, db: Session = Depends(get_db)):
    surgery = crud.partial_update_surgery(db, surgery_id=surgery_id, surgery_data=surgery_data)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.post("/surgeries", response_model=schemas.Surgery)
async def create_surgery(surgery: schemas.SurgeryCreate, db: Session = Depends(get_db)):
    db_surgery = crud.create_surgery(db, surgery)
    if db_surgery is None:
        raise HTTPException(status_code=400, detail="Failed to create surgery")
    return db_surgery

@app.get("/tier-lists", response_model=list[schemas.TierList])
async def read_tier_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tier_lists(db, skip=skip, limit=limit)

@app.get("/partners", response_model=list[schemas.Partner])
async def read_partner_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    print("Here")
    return crud.get_partner_lists(db, skip=skip, limit=limit)

