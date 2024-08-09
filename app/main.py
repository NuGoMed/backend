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
    """
    ## Login for Access Token

    Authenticate a user using their username and password, and return an access token.

    ### Parameters:
    - **db**: Database session dependency.
    - **form_data**: OAuth2PasswordRequestForm containing the username and password.

    ### Returns:
    - **200 OK**: JSON containing the access token and token type.
        - Example: `{"access_token": "token_value", "token_type": "bearer"}`

    ### Errors:
    - **401 Unauthorized**: Incorrect username or password.
        - Error detail: `{"detail": "Incorrect username or password"}`
    """
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
    """
    ## Create New User

    Register a new user with a unique username.

    ### Parameters:
    - **user**: A `UserCreate` schema containing the details of the user to be created.
    - **db**: Database session dependency.
    - **current_user**: The current logged-in user (used for authentication purposes).

    ### Returns:
    - **200 OK**: A JSON response with the created user details.
        - Example: `{"id": 1, "username": "new_user", ...}`

    ### Errors:
    - **400 Bad Request**: Username already registered.
        - Error detail: `{"detail": "Username already registered"}`
    """
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@app.get("/users/me/", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    ## Get Current User

    Retrieve the details of the currently authenticated user.

    ### Parameters:
    - **current_user**: The current logged-in user (automatically retrieved by `Depends(get_current_user)`).

    ### Returns:
    - **200 OK**: A JSON response with the current user's details.
        - Example: `{"id": 1, "username": "current_user", ...}`
    """
    return current_user

@app.get("/")
async def main():
    """
    ## Root Endpoint

    A simple endpoint to verify the API is running.

    ### Returns:
    - **200 OK**: A JSON message confirming the API is active.
        - Example: `{"message": "Hello World"}`
    """
    return {"message": "Hello World"}

async def send_email(email: str, subject: str, message: str):
    """
    ## Send Email

    Sends an email using the configured SMTP server.

    ### Parameters:
    - **email**: The recipient's email address.
        - Type: `str`
        - Example: `"recipient@example.com"`
    - **subject**: The subject of the email.
        - Type: `str`
        - Example: `"Your Surgery Details"`
    - **message**: The body of the email.
        - Type: `str`
        - Example: `"Here are the details of your upcoming surgery..."`

    ### Raises:
    - **500 Internal Server Error**: If SMTP configuration is incomplete or if there is an issue connecting to the SMTP server.
        - Error detail: `{"detail": "SMTP configuration is incomplete"}`
        - Error detail: `{"detail": "Failed to connect to SMTP server"}`
        - Error detail: `{"detail": "SMTP server returned an error response"}`
        - Error detail: `{"detail": "An unexpected error occurred"}`
    
    ### Notes:
    - Supports both TLS (port 587) and SSL (port 465) based on the SMTP configuration.
    """
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
    """
    ## Send Email Endpoint

    This endpoint sends an email using the provided details and logs the email in the database.

    ### Request Body:
    - **email**: A `schemas.EmailSchema` object containing the following fields:
        - **mail_to**: The recipient's email address.
            - Type: `str`
            - Example: `"recipient@example.com"`
        - **subject**: The subject of the email.
            - Type: `str`
            - Example: `"Your Surgery Details"`
        - **message**: The body of the email.
            - Type: `str`
            - Example: `"Here are the details of your upcoming surgery..."`

    ### Returns:
    - **200 OK**: A JSON response confirming that the email has been sent and stored in the database.
        - Example: `{"message": "Email has been sent", "email_id": 1}`

    ### Errors:
    - **500 Internal Server Error**: If there is an issue with the SMTP configuration or server connection.
        - Error detail: `{"detail": "SMTP configuration is incomplete"}`
        - Error detail: `{"detail": "Failed to connect to SMTP server"}`
        - Error detail: `{"detail": "SMTP server returned an error response"}`
        - Error detail: `{"detail": "An unexpected error occurred"}`
    """
    await send_email(email.mail_to, email.subject, email.message)
    db_email = crud.create_email(db, email)
    return {"message": "Email has been sent", "email_id": db_email.id}

@app.get("/surgeries", response_model=list[schemas.Surgery])
async def read_surgeries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    ## Get Surgeries

    Retrieves a list of surgeries from the database with optional pagination.

    ### Query Parameters:
    - **skip**: The number of records to skip for pagination.
        - Type: `int`
        - Default: `0`
        - Example: `10`
    - **limit**: The maximum number of records to return.
        - Type: `int`
        - Default: `100`
        - Example: `50`

    ### Returns:
    - **200 OK**: A list of surgeries, each represented by a `schemas.Surgery` object.
        - Example: `[{"id": 1, "patient_name": "John Doe", "surgery_date": "2024-08-10", ...}, ...]`

    ### Errors:
    - **500 Internal Server Error**: If there is an issue with the database connection or query.
    """
    return crud.get_surgeries(db, skip=skip, limit=limit)

@app.get("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def read_surgery(surgery_id: int, db: Session = Depends(get_db)):
    """
    ## Get Surgery by ID

    Retrieves a specific surgery by its ID from the database.

    ### Path Parameters:
    - **surgery_id**: The ID of the surgery to retrieve.
        - Type: `int`
        - Example: `1`

    ### Returns:
    - **200 OK**: A `schemas.Surgery` object representing the surgery.
        - Example: `{"id": 1, "patient_name": "John Doe", "surgery_date": "2024-08-10", ...}`

    ### Errors:
    - **404 Not Found**: If the surgery with the specified ID does not exist.
        - Error detail: `{"detail": "Surgery not found"}`
    """
    surgery = crud.get_surgeries_by_id(db, surgery_id=surgery_id)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.delete("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def delete_surgery(surgery_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    ## Delete Surgery by ID

    Deletes a specific surgery by its ID from the database. Only accessible to authenticated users.

    ### Path Parameters:
    - **surgery_id**: The ID of the surgery to delete.
        - Type: `int`
        - Example: `1`

    ### Returns:
    - **200 OK**: A `schemas.Surgery` object representing the deleted surgery.
        - Example: `{"id": 1, "patient_name": "John Doe", "surgery_date": "2024-08-10", ...}`

    ### Errors:
    - **404 Not Found**: If the surgery with the specified ID does not exist.
        - Error detail: `{"detail": "Surgery not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    surgery = crud.delete_surgery(db, surgery_id=surgery_id)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.put("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def update_surgery(surgery_id: int, surgery_data: schemas.SurgeryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    ## Update Surgery

    Updates an existing surgery's details with the provided data.

    ### Path Parameters:
    - **surgery_id**: The ID of the surgery to update.
        - Type: `int`
        - Example: `1`

    ### Request Body:
    - **surgery_data**: The updated surgery data.
        - Type: `schemas.SurgeryUpdate`
        - Example: `{"patient_name": "Jane Doe", "surgery_date": "2024-09-01", ...}`

    ### Returns:
    - **200 OK**: A `schemas.Surgery` object representing the updated surgery.
        - Example: `{"id": 1, "patient_name": "Jane Doe", "surgery_date": "2024-09-01", ...}`

    ### Errors:
    - **404 Not Found**: If the surgery with the specified ID does not exist.
        - Error detail: `{"detail": "Surgery not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    surgery = crud.update_surgery(db, surgery_id=surgery_id, surgery_data=surgery_data)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.patch("/surgeries/{surgery_id}", response_model=schemas.Surgery)
async def partial_update_surgery(surgery_id: int, surgery_data: schemas.SurgeryPartialUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    ## Partially Update Surgery

    Partially updates specific fields of an existing surgery's details.

    ### Path Parameters:
    - **surgery_id**: The ID of the surgery to partially update.
        - Type: `int`
        - Example: `1`

    ### Request Body:
    - **surgery_data**: The fields to update in the surgery.
        - Type: `schemas.SurgeryPartialUpdate`
        - Example: `{"surgery_date": "2024-09-01"}`

    ### Returns:
    - **200 OK**: A `schemas.Surgery` object representing the updated surgery.
        - Example: `{"id": 1, "patient_name": "John Doe", "surgery_date": "2024-09-01", ...}`

    ### Errors:
    - **404 Not Found**: If the surgery with the specified ID does not exist.
        - Error detail: `{"detail": "Surgery not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    surgery = crud.partial_update_surgery(db, surgery_id=surgery_id, surgery_data=surgery_data)
    if surgery is None:
        raise HTTPException(status_code=404, detail="Surgery not found")
    return surgery

@app.post("/surgeries", response_model=schemas.Surgery)
async def create_surgery(surgery: schemas.SurgeryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    ## Create Surgery

    Creates a new surgery record with the provided details.

    ### Request Body:
    - **surgery**: The data for the new surgery.
        - Type: `schemas.SurgeryCreate`
        - Example: `{"patient_name": "John Doe", "surgery_date": "2024-08-10", "surgeon_name": "Dr. Smith", ...}`

    ### Returns:
    - **200 OK**: A `schemas.Surgery` object representing the newly created surgery.
        - Example: `{"id": 1, "patient_name": "John Doe", "surgery_date": "2024-08-10", ...}`

    ### Errors:
    - **400 Bad Request**: If there is an issue creating the surgery.
        - Error detail: `{"detail": "Failed to create surgery"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    db_surgery = crud.create_surgery(db, surgery)
    if db_surgery is None:
        raise HTTPException(status_code=400, detail="Failed to create surgery")
    return db_surgery

@app.get("/tier-lists", response_model=list[schemas.TierList])
async def read_tier_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    ## Get All Tier Lists

    Retrieves a list of tier lists with optional pagination.

    ### Query Parameters:
    - **skip**: The number of records to skip (for pagination).
        - Type: `int`
        - Default: `0`
        - Example: `10`
    - **limit**: The maximum number of records to return.
        - Type: `int`
        - Default: `100`
        - Example: `50`

    ### Returns:
    - **200 OK**: A list of `schemas.TierList` objects.
        - Example: `[{"id": 1, "name": "Best Movies", ...}, {"id": 2, "name": "Top Games", ...}]`

    ### Errors:
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    return crud.get_tier_lists(db, skip=skip, limit=limit)

@app.get("/tier-lists/{tier_list_id}", response_model=schemas.TierList)
async def read_tier_list(tier_list_id: int, db: Session = Depends(get_db)):
    """
    ## Get Tier List by ID

    Retrieves a specific tier list by its ID.

    ### Path Parameters:
    - **tier_list_id**: The ID of the tier list to retrieve.
        - Type: `int`
        - Example: `1`

    ### Returns:
    - **200 OK**: A `schemas.TierList` object representing the tier list.
        - Example: `{"id": 1, "name": "Best Movies", "categories": ["Action", "Drama"], ...}`

    ### Errors:
    - **404 Not Found**: If the tier list with the specified ID does not exist.
        - Error detail: `{"detail": "Tier list not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
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
    """
    ## Update Tier List

    Updates an existing tier list with the provided data.

    ### Path Parameters:
    - **tier_list_id**: The ID of the tier list to update.
        - Type: `int`
        - Example: `1`

    ### Request Body:
    - **tier_list_data**: The updated tier list data.
        - Type: `schemas.TierListUpdate`
        - Example: `{"name": "Top Movies", "categories": ["Action", "Comedy"]}`

    ### Returns:
    - **200 OK**: A `schemas.TierList` object representing the updated tier list.
        - Example: `{"id": 1, "name": "Top Movies", "categories": ["Action", "Comedy"], ...}`

    ### Errors:
    - **404 Not Found**: If the tier list with the specified ID does not exist.
        - Error detail: `{"detail": "Tier list not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    tier_list = crud.update_tier_lists(db, tier_list_id=tier_list_id, tier_list_data=tier_list_data)
    if tier_list is None:
        raise HTTPException(status_code=404, detail="Tier list not found")
    return tier_list

@app.get("/partners", response_model=list[schemas.Partner])
async def read_partner_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    ## Get All Partners

    Retrieves a list of partners with optional pagination.

    ### Query Parameters:
    - **skip**: The number of records to skip (for pagination).
        - Type: `int`
        - Default: `0`
        - Example: `10`
    - **limit**: The maximum number of records to return.
        - Type: `int`
        - Default: `100`
        - Example: `50`

    ### Returns:
    - **200 OK**: A list of `schemas.Partner` objects.
        - Example: `[{"id": 1, "name": "Partner A", ...}, {"id": 2, "name": "Partner B", ...}]`

    ### Errors:
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    return crud.get_partner_lists(db, skip=skip, limit=limit)

@app.get("/partners/{partner_id}", response_model=schemas.Partner)
async def read_partner_lists_Id(partner_id: int, db: Session = Depends(get_db)):
    """
    ## Get Partner by ID

    Retrieves a specific partner by its ID.

    ### Path Parameters:
    - **partner_id**: The ID of the partner to retrieve.
        - Type: `int`
        - Example: `1`

    ### Returns:
    - **200 OK**: A `schemas.Partner` object representing the partner.
        - Example: `{"id": 1, "name": "Partner A", "details": {...}}`

    ### Errors:
    - **404 Not Found**: If the partner with the specified ID does not exist.
        - Error detail: `{"detail": "Partner not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    partner = crud.get_partner_by_id(db, partner_id=partner_id)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@app.delete("/partners/{partner_id}", response_model=schemas.Partner)
async def delete_partner(partner_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    ## Delete Partner

    Deletes a specific partner by its ID.

    ### Path Parameters:
    - **partner_id**: The ID of the partner to delete.
        - Type: `int`
        - Example: `1`

    ### Returns:
    - **200 OK**: A `schemas.Partner` object representing the deleted partner.
        - Example: `{"id": 1, "name": "Partner A", "details": {...}}`

    ### Errors:
    - **404 Not Found**: If the partner with the specified ID does not exist.
        - Error detail: `{"detail": "Partner not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    partner = crud.delete_partner(db, partner_id=partner_id)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@app.put("/partners/{partner_id}", response_model=schemas.Partner)
async def update_partner(partner_id: int, partner_data: schemas.PartnerUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    ## Update Partner

    Updates the details of an existing partner by its ID.

    ### Path Parameters:
    - **partner_id**: The ID of the partner to update.
        - Type: `int`
        - Example: `1`

    ### Request Body:
    - **partner_data**: The updated data for the partner.
        - Type: `schemas.PartnerUpdate`
        - Example:
        ```json
        {
            "company_name": "New Company Name",
            "website": "https://new-website.com",
            "help_type": "New Help Type",
            "logo": "base64_encoded_logo_string"
        }
        ```

    ### Returns:
    - **200 OK**: The updated `schemas.Partner` object.
        - Example:
        ```json
        {
            "id": 1,
            "company_name": "New Company Name",
            "website": "https://new-website.com",
            "help_type": "New Help Type",
            "logo": "base64_encoded_logo_string"
        }
        ```

    ### Errors:
    - **404 Not Found**: If the partner with the specified ID does not exist.
        - Error detail: `{"detail": "Partner not found"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    partner = crud.update_partner(db, partner_id=partner_id, partner_data=partner_data)
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@app.post("/partners", response_model=schemas.Partner)
async def create_partner(partner: schemas.PartnerCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    ## Create New Partner

    Creates a new partner and returns the created partner's details.

    ### Request Body:
    - **partner**: The data for the new partner.
        - Type: `schemas.PartnerCreate`
        - Example:
        ```json
        {
            "company_name": "Partner Company",
            "website": "https://partner-website.com",
            "help_type": "Financial",
            "logo": "base64_encoded_logo_string"
        }
        ```

    ### Returns:
    - **200 OK**: The created `schemas.Partner` object.
        - Example:
        ```json
        {
            "id": 1,
            "company_name": "Partner Company",
            "website": "https://partner-website.com",
            "help_type": "Financial",
            "logo": "base64_encoded_logo_string"
        }
        ```

    ### Errors:
    - **400 Bad Request**: If the partner creation fails.
        - Error detail: `{"detail": "Failed to create partner"}`
    - **401 Unauthorized**: If the user is not authenticated.
        - Error detail: `{"detail": "Not authenticated"}`
    """
    db_partner = crud.create_partner(db=db, partner=partner)
    return {
        "id": db_partner.id,
        "company_name": db_partner.company_name,
        "website": db_partner.website,
        "help_type": db_partner.help_type,
        "logo": base64.b64encode(db_partner.logo).decode('utf-8') if db_partner.logo else None
    }

"""
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
<<<<<<< Updated upstream
    return StreamingResponse(file_like, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={file_record.file_name}"})
=======
    return StreamingResponse(file_like, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={file_record.file_name}"})
"""

@app.post("/customers/", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    ## Create New Customer

    Creates a new customer and returns the created customer's details.

    ### Request Body:
    - **customer**: The data required to create a new customer.
        - Type: `schemas.CustomerCreate`
        - Example:
        ```json
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "123-456-7890",
            "address": "123 Main St, Anytown, USA"
        }
        ```

    ### Returns:
    - **200 OK**: The created `schemas.CustomerResponse` object, which includes the customer's ID and other details.
        - Example:
        ```json
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "123-456-7890",
            "address": "123 Main St, Anytown, USA"
        }
        ```

    ### Errors:
    - **400 Bad Request**: If the customer creation fails due to validation errors or other issues.
        - Error detail: `{"detail": "Failed to create customer"}`
    """
    return crud.create_customer(db, customer)

@app.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    ## Get Customer by ID

    Retrieves a customer's details by their ID.

    ### Path Parameters:
    - **customer_id**: The ID of the customer to retrieve.
        - Type: `int`
        - Example: `1`

    ### Returns:
    - **200 OK**: The `schemas.CustomerResponse` object containing the customer's details.
        - Example:
        ```json
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "123-456-7890",
            "address": "123 Main St, Anytown, USA"
        }
        ```

    ### Errors:
    - **404 Not Found**: If no customer with the given ID is found.
        - Error detail: `{"detail": "Customer not found"}`
    """
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.get("/customers/", response_model=list[schemas.CustomerResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    ## Get List of Customers

    Retrieves a list of customers with pagination support.

    ### Query Parameters:
    - **skip**: The number of records to skip for pagination.
        - Type: `int`
        - Default: `0`
        - Example: `10`
    - **limit**: The maximum number of records to return.
        - Type: `int`
        - Default: `100`
        - Example: `50`

    ### Returns:
    - **200 OK**: A list of `schemas.CustomerResponse` objects.
        - Example:
        ```json
        [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "123-456-7890",
                "address": "123 Main St, Anytown, USA"
            },
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "phone_number": "987-654-3210",
                "address": "456 Elm St, Othertown, USA"
            }
        ]
        ```

    ### Errors:
    - **400 Bad Request**: If an invalid `skip` or `limit` value is provided.
        - Error detail: `{"detail": "Invalid query parameters"}`
    """
    return crud.get_customers(db, skip=skip, limit=limit)

@app.post("/buys/", response_model=schemas.BuyResponse)
def create_buy(buy: schemas.BuyCreate, db: Session = Depends(get_db)):
    """
    ## Create New Buy

    Creates a new buy record and returns the details of the created buy.

    ### Request Body:
    - **buy**: The data required to create a new buy.
        - Type: `schemas.BuyCreate`
        - Example:
        ```json
        {
            "product_id": 1,
            "customer_id": 2,
            "quantity": 3,
            "price": 299.99
        }
        ```

    ### Returns:
    - **200 OK**: The created `schemas.BuyResponse` object, which includes details of the buy.
        - Example:
        ```json
        {
            "id": 1,
            "product_id": 1,
            "customer_id": 2,
            "quantity": 3,
            "price": 299.99,
            "timestamp": "2024-08-09T12:34:56"
        }
        ```

    ### Errors:
    - **400 Bad Request**: If the buy creation fails due to validation errors or other issues.
        - Error detail: `{"detail": "Failed to create buy"}`
    """
    return crud.create_buy(db, buy)

@app.get("/buys/{buy_id}", response_model=schemas.BuyResponse)
def read_buy(buy_id: int, db: Session = Depends(get_db)):
    """
    ## Get Buy by ID

    Retrieves details of a specific buy record by its ID.

    ### Path Parameters:
    - **buy_id**: The ID of the buy record to retrieve.
        - Type: `int`
        - Example: `1`

    ### Returns:
    - **200 OK**: The `schemas.BuyResponse` object containing details of the buy.
        - Example:
        ```json
        {
            "id": 1,
            "product_id": 1,
            "customer_id": 2,
            "quantity": 3,
            "price": 299.99,
            "timestamp": "2024-08-09T12:34:56"
        }
        ```

    ### Errors:
    - **404 Not Found**: If no buy with the given ID is found.
        - Error detail: `{"detail": "Buy not found"}`
    """
    db_buy = crud.get_buy(db, buy_id)
    if db_buy is None:
        raise HTTPException(status_code=404, detail="Buy not found")
    return db_buy

@app.get("/customers/{customer_id}/buys/", response_model=list[schemas.BuyResponse])
def read_buys_by_customer(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    ## Get Buys by Customer

    Retrieves a list of buy records associated with a specific customer, with pagination support.

    ### Path Parameters:
    - **customer_id**: The ID of the customer whose buys are to be retrieved.
        - Type: `int`
        - Example: `2`

    ### Query Parameters:
    - **skip**: The number of records to skip for pagination.
        - Type: `int`
        - Default: `0`
        - Example: `10`
    - **limit**: The maximum number of records to return.
        - Type: `int`
        - Default: `100`
        - Example: `50`

    ### Returns:
    - **200 OK**: A list of `schemas.BuyResponse` objects for the specified customer.
        - Example:
        ```json
        [
            {
                "id": 1,
                "product_id": 1,
                "customer_id": 2,
                "quantity": 3,
                "price": 299.99,
                "timestamp": "2024-08-09T12:34:56"
            },
            {
                "id": 2,
                "product_id": 3,
                "customer_id": 2,
                "quantity": 1,
                "price": 149.99,
                "timestamp": "2024-08-09T13:45:00"
            }
        ]
        ```

    ### Errors:
    - **400 Bad Request**: If invalid `skip` or `limit` values are provided.
        - Error detail: `{"detail": "Invalid query parameters"}`
    """
    return crud.get_buys_by_customer(db, customer_id, skip=skip, limit=limit)
    
>>>>>>> Stashed changes
