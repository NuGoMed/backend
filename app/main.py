import logging, os, aiosmtplib, base64
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Path, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.future import select
from dotenv import load_dotenv
from sql_app import models, crud, schemas, database, auth
from email.message import EmailMessage
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO
from fastapi.security import OAuth2PasswordRequestForm
from sql_app.auth import authenticate_user, create_access_token, get_current_user


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

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Received form_data: {form_data}")
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserResponse)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@app.get("/users/me/", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

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
async def delete_surgery(surgery_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    surgery = crud.delete_surgery(db, surgery_id=surgery_id)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.put("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def update_surgery(surgery_id: int, surgery_data: schemas.SurgeryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    surgery = crud.update_surgery(db, surgery_id=surgery_id, surgery_data=surgery_data)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.patch("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def partial_update_surgery(surgery_id: int, surgery_data: schemas.SurgeryPartialUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    surgery = crud.partial_update_surgery(db, surgery_id=surgery_id, surgery_data=surgery_data)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.post("/surgeries", response_model=schemas.Surgery)
async def create_surgery(surgery: schemas.SurgeryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_surgery = crud.create_surgery(db, surgery)
    if db_surgery is None:
        raise HTTPException(status_code=400, detail="Failed to create surgery")
    return db_surgery

@app.get("/tier-lists", response_model=list[schemas.TierList])
async def read_tier_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tier_lists(db, skip=skip, limit=limit)

@app.get("/tier-lists/{tier_list_id}", response_model=schemas.TierList)
async def read_tier_list(tier_list_id: int, db: Session = Depends(get_db)):
    tier_list = crud.get_tier_list_by_id(db, tier_list_id=tier_list_id)
    if tier_list is None:
        raise HTTPException(status_code=404, detail="Tier list not found")
    return tier_list

@app.put("/tier-lists/{tier_list_id}", response_model=schemas.TierList)
async def update_tier_lists(
    tier_list_id: int,
    tier_list_data: schemas.TierListUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tier_list = crud.update_tier_lists(db, tier_list_id=tier_list_id, tier_list_data=tier_list_data)
    if tier_list is None:
        raise HTTPException(status_code=404, detail="Tier list not found")
    return tier_list

@app.get("/partners", response_model=list[schemas.Partner])
async def read_partner_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    print("Here")
    return crud.get_partner_lists(db, skip=skip, limit=limit)

@app.get("/partners/{partner_id}", response_model=schemas.Partner)
async def read_partner_lists_Id(partner_id: int, db: Session = Depends(get_db)):
    partner = crud.get_partner_by_id(db, partner_id=partner_id)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@app.delete("/partners/{partner_id}", response_model=schemas.Partner)
async def delete_partner(partner_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    partner = crud.delete_partner(db, partner_id=partner_id)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@app.put("/partners/{partner_id}", response_model=schemas.Partner)
async def update_partner(partner_id: int, partner_data: schemas.PartnerUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    partner = crud.update_partner(db, partner_id=partner_id, partner_data=partner_data)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@app.post("/partners", response_model=schemas.Partner)
async def create_partner(partner: schemas.PartnerCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_partner = crud.create_partner(db=db, partner=partner)
    return {
        "id": db_partner.id,
        "company_name": db_partner.company_name,
        "website": db_partner.website,
        "help_type": db_partner.help_type,
        "logo": base64.b64encode(db_partner.logo).decode('utf-8') if db_partner.logo else None
    }

@app.post("/upload/")
async def upload_pdf_file(file: UploadFile = File(...), description: str = "", db: Session = Depends(get_db)):
    file_data = await file.read()
    pdf_file = crud.create_pdf_file(db=db, file_name=file.filename, file_data=file_data, description=description)
    return {"file_id": pdf_file.id, "file_name": pdf_file.file_name}

@app.get("/files/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    file_record = db.query(models.PDFFile).filter(models.PDFFile.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_like = BytesIO(file_record.file_data)
    return StreamingResponse(file_like, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={file_record.file_name}"})

@app.post("/customers/", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, customer)

@app.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.get("/customers/", response_model=list[schemas.CustomerResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db, skip=skip, limit=limit)

@app.post("/buys/", response_model=schemas.BuyResponse)
def create_buy(buy: schemas.BuyCreate, db: Session = Depends(get_db)):
    return crud.create_buy(db, buy)

@app.get("/buys/{buy_id}", response_model=schemas.BuyResponse)
def read_buy(buy_id: int, db: Session = Depends(get_db)):
    db_buy = crud.get_buy(db, buy_id)
    if db_buy is None:
        raise HTTPException(status_code=404, detail="Buy not found")
    return db_buy

@app.get("/customers/{customer_id}/buys/", response_model=list[schemas.BuyResponse])
def read_buys_by_customer(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_buys_by_customer(db, customer_id, skip=skip, limit=limit)
    