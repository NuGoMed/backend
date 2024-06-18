from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sql_app.database import SessionLocal

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "https://nugomed.com:3000",
    "http://nugomed.com"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/helloworld2")
async def main():
    return {"message":"Hello World"}