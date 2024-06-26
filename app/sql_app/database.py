from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


host = "postgresql"
port = 5432
userDB = os.getenv('POSTGRES_USER')
passDB = os.getenv('POSTGRES_PASSWORD')
dbname = os.getenv('POSTGRES_DB')

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{userDB}:{passDB}@{host}/{dbname}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()