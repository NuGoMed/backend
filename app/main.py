import os, sys, asyncio, logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from email.message import EmailMessage
import aiosmtplib
from sql_app import models, schemas
from sql_app.database import engine, SessionLocal
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Database configuration
host = "localhost"
port = 5432
userDB = os.getenv('POSTGRES_USER')
passDB = os.getenv('POSTGRES_PASSWORD')
dbname = os.getenv('POSTGRES_DB')
SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{userDB}:{passDB}@{host}:{port}/{dbname}'

# Async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to get the async database session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/")
async def main():
    return {"message": "Hello World"}

@app.get("/surgery")
async def get_surgery_test():
    async with AsyncSessionLocal() as db:
        surgery_id = 1
        result = await db.execute(select(models.Surgeries).filter(models.Surgeries.id == surgery_id))
        surgery = result.scalars().first()

        if surgery is None:
            print("No surgery listed")
        else:
            assert surgery.surgery == 'CABG - Coronary artery bypass graft of 3 or more vessels'
            assert surgery.surgery_description == 'Surgical procedure to treat coronary artery disease'
            print(f"Surgery name: {surgery.surgery}, Surgery description: {surgery.surgery_description}")

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str

async def send_email(email: str, subject: str, message: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))  # Default to 587 if not provided
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
            # Use STARTTLS for port 587
            await aiosmtplib.send(
                msg,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                use_tls=True  # STARTTLS
            )
        elif smtp_port == 465:
            # Use SSL for port 465
            await aiosmtplib.send(
                msg,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                use_tls=True  # Implicit SSL/TLS
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
async def send_email_endpoint(email: EmailSchema):
    await send_email(email.email, email.subject, email.message)
    return {"message": "Email has been sent"}
