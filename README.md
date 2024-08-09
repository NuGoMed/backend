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
- CRUD operations for users, surgeries, tier lists, partners, and customers
- File upload and download functionality
- Support for retrieving and managing buys associated with customers
- CORS support for specified origins

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/yourproject.git
    cd yourproject
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. **Initialize the database & Start the FastAPI server**:
    ```bash
    docker-compose up -d
    ```

2. Open your browser and go to `http://127.0.0.1:8000/docs` to see the interactive API documentation (provided by Swagger UI).

3. Go to `http://127.0.0.1:8000/redoc` for an alternative API documentation (provided by ReDoc).

## API Endpoints

### Authentication
- **POST** `/token`
  - **Description**: Authenticate a user and get a JWT token.
  - **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```

### Users
- **POST** `/users/`
  - **Description**: Create a new user.
  - **Request Body**: `schemas.UserCreate`
- **GET** `/users/me/`
  - **Description**: Get the current authenticated user.

### Surgeries
- **GET** `/surgeries`
  - **Description**: Retrieve a list of surgeries.
  - **Query Parameters**:
    - `skip` (int, optional): Number of records to skip (default is 0).
    - `limit` (int, optional): Maximum number of records to return (default is 100).
- **GET** `/surgeries/{surgery_id}`
  - **Description**: Retrieve a specific surgery by its ID.
  - **Path Parameter**:
    - `surgery_id` (int): The ID of the surgery.
- **POST** `/surgeries`
  - **Description**: Create a new surgery.
  - **Request Body**: `schemas.SurgeryCreate`
- **PUT** `/surgeries/{surgery_id}`
  - **Description**: Update an existing surgery.
  - **Path Parameter**:
    - `surgery_id` (int): The ID of the surgery.
  - **Request Body**: `schemas.SurgeryUpdate`
- **PATCH** `/surgeries/{surgery_id}`
  - **Description**: Partially update an existing surgery.
  - **Path Parameter**:
    - `surgery_id` (int): The ID of the surgery.
  - **Request Body**: `schemas.SurgeryPartialUpdate`
- **DELETE** `/surgeries/{surgery_id}`
  - **Description**: Delete a surgery by its ID.
  - **Path Parameter**:
    - `surgery_id` (int): The ID of the surgery.

### Tier Lists
- **GET** `/tier-lists`
  - **Description**: Retrieve a list of tier lists.
  - **Query Parameters**:
    - `skip` (int, optional): Number of records to skip (default is 0).
    - `limit` (int, optional): Maximum number of records to return (default is 100).
- **GET** `/tier-lists/{tier_list_id}`
  - **Description**: Retrieve a specific tier list by its ID.
  - **Path Parameter**:
    - `tier_list_id` (int): The ID of the tier list.
- **PUT** `/tier-lists/{tier_list_id}`
  - **Description**: Update an existing tier list.
  - **Path Parameter**:
    - `tier_list_id` (int): The ID of the tier list.
  - **Request Body**: `schemas.TierListUpdate`

### Partners
- **GET** `/partners`
  - **Description**: Retrieve a list of partners.
  - **Query Parameters**:
    - `skip` (int, optional): Number of records to skip (default is 0).
    - `limit` (int, optional): Maximum number of records to return (default is 100).
- **GET** `/partners/{partner_id}`
  - **Description**: Retrieve a specific partner by its ID.
  - **Path Parameter**:
    - `partner_id` (int): The ID of the partner.
- **POST** `/partners`
  - **Description**: Create a new partner.
  - **Request Body**: `schemas.PartnerCreate`
- **PUT** `/partners/{partner_id}`
  - **Description**: Update an existing partner.
  - **Path Parameter**:
    - `partner_id` (int): The ID of the partner.
  - **Request Body**: `schemas.PartnerUpdate`
- **DELETE** `/partners/{partner_id}`
  - **Description**: Delete a partner by its ID.
  - **Path Parameter**:
    - `partner_id` (int): The ID of the partner.

### Customers
- **POST** `/customers/`
  - **Description**: Create a new customer.
  - **Request Body**: `schemas.CustomerCreate`
- **GET** `/customers/{customer_id}`
  - **Description**: Retrieve a specific customer by its ID.
  - **Path Parameter**:
    - `customer_id` (int): The ID of the customer.
- **GET** `/customers/`
  - **Description**: Retrieve a list of customers.
  - **Query Parameters**:
    - `skip` (int, optional): Number of records to skip (default is 0).
    - `limit` (int, optional): Maximum number of records to return (default is 100).

### Buys
- **POST** `/buys/`
  - **Description**: Create a new buy record.
  - **Request Body**: `schemas.BuyCreate`
- **GET** `/buys/{buy_id}`
  - **Description**: Retrieve a specific buy record by its ID.
  - **Path Parameter**:
    - `buy_id` (int): The ID of the buy.
- **GET** `/customers/{customer_id}/buys/`
  - **Description**: Retrieve a list of buy records associated with a specific customer.
  - **Path Parameter**:
    - `customer_id` (int): The ID of the customer.
  - **Query Parameters**:
    - `skip` (int, optional): Number of records to skip (default is 0).
    - `limit` (int, optional): Maximum number of records to return (default is 100).

### Files
- **POST** `/upload/`
  - **Description**: Upload a PDF file.
  - **Request Body**: Form data with file upload.
- **GET** `/files/{file_id}`
  - **Description**: Retrieve a specific file by its ID.
  - **Path Parameter**:
    - `file_id` (int): The ID of the file.

### Email
- **POST** `/send-email/`
  - **Description**: Send an email.
  - **Request Body**: `schemas.EmailSchema`

## Testing

To run the tests, you can use `pytest`:

```bash
pytest
