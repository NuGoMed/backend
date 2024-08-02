from sqlalchemy.orm import Session
from .models import Book, Email
from .schemas import BookSchema, EmailSchema

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


def get_book(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Book).offset(skip).limit(limit).all()

def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()

def create_book(db: Session, book: BookSchema):
    _book = Book(title=book.title, description=book.description)
    db.add(_book)
    db.commit()
    db.refresh(_book)
    return _book


def remove_book(db: Session, book_id: int):
    _book = get_book_by_id(db=db, book_id=book_id)
    db.delete(_book)
    db.commit()


def update_book(db: Session, book_id: int, title: str, description: str):
    _book = get_book_by_id(db=db, book_id=book_id)

    _book.title = title
    _book.description = description

    db.commit()
    db.refresh(_book)
    return _book
