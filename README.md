# Accounting Integration API

A **Python/FastAPI** service that provides a **modular API architecture** for routing requests to multiple accounting systems (e.g., Tally ERP, Miracle), complete with:
- Central entry points for `GET` and `POST` requests
- Database-driven configuration
- Transaction logging (success/fail)
- Built-in rate limiting
- An Admin Panel (REST) for managing configurations & logs

---

## Table of Contents
1. [Features](#features)  
2. [Architecture Diagram](#architecture-diagram)  
3. [Tech Stack](#tech-stack)  
4. [Prerequisites](#prerequisites)  
5. [Installation](#installation)  
6. [Running the Project](#running-the-project)  
7. [API Usage](#api-usage)  
   - [Public Routes (Dynamic Routing)](#public-routes-dynamic-routing)  
   - [Admin Routes](#admin-routes)  
8. [Configuration Details](#configuration-details)  
   - [ConfigTable](#configtable)  
   - [TransactionLog](#transactionlog)  
   - [Rate Limiting](#rate-limiting)  
9. [Extending the Project](#extending-the-project)  
10. [Troubleshooting](#troubleshooting)

---

## Features

- **Dynamic Routing**: A single entry point (`/api/...`) that routes `GET` and `POST` calls to different accounting software based on database configs.  
- **Admin Panel**: Manage all external system configs, view/update logs, and control rate limits via RESTful endpoints.  
- **Transaction Logging**: Automatically logs both successful and failed calls for easy troubleshooting and analytics.  
- **Rate Limiting**: Restricts excessive calls per route within a 24-hour window, returning a `429 (Too Many Requests)` status if exceeded.  
- **Scalable Architecture**: Clean, modular folder structure, making it easy to add new systems, features, or endpoints.

---

## Architecture Diagram

A **simplified** conceptual diagram of the system:

           ┌───────────────────────┐
           │   External Clients    │
           └─────────┬─────────────┘
                     │
                     ▼
             (Public API Routes)
┌──────────────────────────────────────────┐
│       FastAPI Application (main.py)     │
│  - Dynamic Routing Endpoints (routes.py)│
│  - Admin Panel Endpoints (admin.py)     │
│  - Rate Limiter (rate_limiter.py)       │
│  - Utils & Models (utils.py, models.py) │
│  - Database Session (database.py)       │
└──────────────────────────────────────────┘
                     │
                     ▼
           ┌───────────────────────┐
           │  SQLite / PostgreSQL  │
           │   (ConfigTable,       │
           │    TransactionLog)    │
           └───────────────────────┘
                     │
                     ▼
        ┌───────────────────────────┐
        │     External Systems      │
        │ (e.g. Tally, Miracle, etc.)  
        └───────────────────────────┘



- A single FastAPI app with two main sets of routes (public and admin).  
- Public routes dynamically read from the `ConfigTable` to determine the base URL for external systems.  
- Each request is logged in `TransactionLog` with success/failure status.  
- Rate limiting is enforced at the route level (based on route configs in the DB).

---

## Tech Stack

- **Language**: Python 3.9+  
- **Framework**: FastAPI  
- **Database**: SQLite by default (easily switchable to PostgreSQL or MySQL)  
- **HTTP Library**: `requests` for making outbound calls  
- **ORM**: SQLAlchemy (via `sqlalchemy.orm`)

---

## Prerequisites

1. **Python 3.9+** (earlier versions may work, but 3.9 or above is recommended).  
2. (Optional) **Virtual environment** tool such as `venv` or `conda` for local isolation.  
3. **Git** installed (if you’ll be cloning from a repository).  
4. **SQLite** (default) or any SQL database you prefer.

---

## Installation

1. **Clone** or download this repository:

   ```bash
   git clone https://github.com/your-repo/accounting-integration.git
   cd accounting-integration

Create and activate a virtual environment (recommended):


python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
Install required dependencies:

pip install -r requirements.txt

(Optional) Update database URL:
By default, the project uses sqlite:///./accounting_integration.db. To use something else (e.g., PostgreSQL), edit DATABASE_URL in app/database.py:

# For PostgreSQL:
DATABASE_URL = "postgresql://username:password@localhost:5432/your_db"

Running the Project
Database creation (if you're using SQLite):

The project automatically creates the necessary tables on the first run using SQLAlchemy’s Base.metadata.create_all().\

Start the application:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Open http://localhost:8000/docs to view the interactive Swagger documentation.
Open http://localhost:8000/redoc for ReDoc documentation.


API Usage
Public Routes (Dynamic Routing)
All public routes (i.e., the ones that external clients or other systems will use) reside under the /api prefix in app/routers/routes.py.

POST /api/{route_name}/{method_name}

Purpose: Dynamically route a POST request to an external system.
Body: JSON payload (arbitrary structure).
Behavior:
Checks if route_name exists in ConfigTable.
Enforces rate limit (if any).
Sends a POST to the system’s base_url/{method_name} with the given JSON.
Logs the call in TransactionLog (success/failure).
GET /api/{route_name}/{method_name}

Purpose: Dynamically route a GET request to an external system.
Behavior: Similar to the POST route, except no JSON body is sent.
Example:


Example:

POST /api/tally-route/create-voucher
{
  "voucherData": { "id": 123, "amount": 999.99 }
}
If tally-route is configured with base_url="http://localhost:5000/tally",
the service will call http://localhost:5000/tally/create-voucher with your JSON payload.



Admin Routes
All admin panel routes are under the /admin prefix in app/routers/admin.py. These are for internal management of the integration layer.

GET /admin/config

Lists all existing config entries in ConfigTable.
POST /admin/config

Creates a new config entry (system name, base URL, rate limit, etc.).
Body example:
json
Copy
{
  "system_name": "tally",
  "base_url": "http://localhost:5000/tally",
  "username": "myUser",
  "password": "mySecret",
  "route_name": "tally-route",
  "rate_limit": 100
}
PUT /admin/config/{config_id}

Updates an existing config entry by ID.
DELETE /admin/config/{config_id}

Deletes an existing config entry by ID.
GET /admin/transactions

Lists recent transaction logs (up to a limit, default 50).
GET /admin/transactions/summary

Summarizes total calls per route, with success/failed counts.



Configuration Details
ConfigTable
Fields:
system_name: e.g., "tally", "miracle", etc.
base_url: e.g., "http://localhost:5000/tally"
username, password: optional credentials for basic HTTP auth.
route_name: unique route key (e.g., "tally-route").
rate_limit: max requests allowed in a 24-hour window (per route).
TransactionLog
Fields:
system_name: e.g., "tally".
route_name: e.g., "tally-route".
request_method: "GET" or "POST".
was_successful: True or False.
timestamp: auto-set on creation.
detail: optional string for error messages or extra info.
Rate Limiting
Each route has an integer rate_limit.
The code counts how many calls have been made for that route_name in the past 24 hours.
If count >= rate_limit, it returns 429 (Too Many Requests).