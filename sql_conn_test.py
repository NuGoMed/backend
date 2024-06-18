import os
import asyncio

from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.pool import StaticPool

from sql_app.database import Base, SessionLocal
from main import app, get_db
from sql_app import models,schemas

host = "localhost"
port = 5432
userDB = os.getenv('POSTGRES_USER')
passDB = os.getenv('POSTGRES_PASSWORD')
dbname = os.getenv('POSTGRES_DB')

SQLALCHEMY_DATABASE_URL_ = f'postgresql+asyncpg://{userDB}:{passDB}@{host}:{port}/{dbname}'

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL_,
#     poolclass=StaticPool
#     )

engine = create_async_engine(SQLALCHEMY_DATABASE_URL_, echo=True)

# TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()

# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[get_db] = override_get_db

# client = TestClient(app)

async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get the async session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_surgery_test():
    async for db in get_async_db():

        surgery_id = 1
        surgery = await db.execute(select(models.Surgeries).filter(models.Surgeries.id == surgery_id))
        surgery = surgery.scalars().first()

        if surgery is None:
            print("No surgery listed")
        
        assert surgery.surgery == 'CABG - Coronary artery bypass graft of 3 or more vessels'
        assert surgery.surgery_description == 'Surgical procedure to treat coronary artery disease'

        print(f"Surgery name: {surgery.surgery}, Surgery description: {surgery.surgery_description}")

        db.close()

asyncio.run(get_surgery_test())