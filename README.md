# FastAPI Project

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Running the Application](#running-the-application)
5. [API Endpoints](#api-endpoints)
6. [Testing](#testing)
7. [Contributing](#contributing)
8. [License](#license)

## Introduction

This project is a web API built with [FastAPI](https://fastapi.tiangolo.com/), a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Features

- User authentication with JWT
- Email sending functionality
- CRUD operations for users, surgeries, tier lists, partners, and PDF files
- File upload and download functionality
- CORS support for specified origins

## Installation

1. **Clone the repository**:
    ```bash
    git clone [https://github.com/yourusername/yourproject.git](https://github.com/NuGoMed/backend.git)
    cd backend
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the environment variables**:
    Create a `.env` file in the project root and add the necessary environment variables:
    ```
    DATABASE_URL=sqlite+aiosqlite:///./test.db
    SMTP_HOST=smtp.example.com
    SMTP_PORT=587
    SMTP_USER=your-email@example.com
    SMTP_PASSWORD=your-email-password
    ```

## Running the Application

1. **Initialize the database**:
    ```bash
    python -m sql_app.models
    ```

2. **Start the FastAPI server**:
    ```bash
    uvicorn main:app --reload
    ```

3. Open your browser and go to `http://127.0.0.1:8000/docs` to see the interactive API documentation (provided by Swagger UI).

4. Go to `http://127.0.0.1:8000/redoc` for an alternative API documentation (provided by ReDoc).

## API Endpoints

### Authentication
- **POST** `/token`: Authenticate a user and get a JWT token.

### Users
- **POST** `/users/`: Create a new user.
- **GET** `/users/me/`: Get the current authenticated user.

### Surgeries
- **GET** `/surgeries`: Retrieve a list of surgeries.
- **GET** `/surgeries/{surgery_id}`: Retrieve a specific surgery by its ID.
- **POST** `/surgeries`: Create a new surgery.
- **PUT** `/surgeries/{surgery_id}`: Update an existing surgery.
- **PATCH** `/surgeries/{surgery_id}`: Partially update an existing surgery.
- **DELETE** `/surgeries/{surgery_id}`: Delete a surgery by its ID.

### Tier Lists
- **GET** `/tier-lists`: Retrieve a list of tier lists.
- **GET** `/tier-lists/{tier_list_id}`: Retrieve a specific tier list by its ID.
- **PUT** `/tier-lists/{tier_list_id}`: Update an existing tier list.

### Partners
- **GET** `/partners`: Retrieve a list of partners.
- **GET** `/partners/{partner_id}`: Retrieve a specific partner by its ID.
- **POST** `/partners`: Create a new partner.
- **PUT** `/partners/{partner_id}`: Update an existing partner.
- **DELETE** `/partners/{partner_id}`: Delete a partner by its ID.

### Files
- **POST** `/upload/`: Upload a PDF file.
- **GET** `/files/{file_id}`: Retrieve a specific file by its ID.

### Email
- **POST** `/send-email/`: Send an email.

## Testing

To run the tests, you can use `pytest`:

```bash
pytest
