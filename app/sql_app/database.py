from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

host = "localhost"
port = 5433
userDB = os.getenv('POSTGRES_USER')
passDB = os.getenv('POSTGRES_PASSWORD')
dbname = os.getenv('POSTGRES_DB')

SQLALCHEMY_DATABASE_URL = f'postgresql://{userDB}:{passDB}@{host}:{port}/{dbname}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
