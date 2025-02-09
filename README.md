# Accounting Integration Service

A **modular FastAPI-based** service that dynamically routes GET/POST requests to various accounting systems (e.g., Tally, Miracle), tracks transaction logs, and provides a minimal Admin panel to manage configurations.

---

## Overview

This project satisfies the following requirements:

1. **Central Entry Point:** Routes are dynamically mapped based on a `ConfigTable`, enabling quick addition of new accounting systems.
2. **Database-Backed Config:** A `config_table` stores credentials, base URLs, route names, and optional rate limits.
3. **Transaction Logging:** A `transaction_log` table records every request, noting both success and failure outcomes.
4. **Rate Limiting:** If a route exceeds its set limit within a 24-hour window, the API returns a 429 error.
5. **Admin Panel:** An `/admin` endpoint allows listing/creating config entries and viewing logs, plus a summary endpoint to see success/failure counts.
6. **Documentation & Diagram:** This README includes architecture details, a high-level diagram, notes on future extensibility, and local setup instructions.

---

## Architecture Diagram

```text
                        +-------------------+
       External Client   |   /api/          |
            +-----------+-> {route}/{method}+----------+
            |           |    (GET, POST)    |          |
            |           +--------+----------+          |
            |                    |                     |
            |                    v                     v
            |         +-------------------+   +------------------+
            |         | RateLimiter       |   |Requests to        |
            |         | (Checks DB logs)  |   |Tally/Miracle etc. |
            |         +--------+----------+   +------------------+
            |                  |                              
            |                  v                              
            |         +-------------------+                    
            |         |TransactionLog     |                    
            |         |(Success/Fail)     |                    
            |         +-------------------+                    
            |                                                     
            |                  +--------------------------------------------+      
            |                  | /admin/ (Admin Panel)                      |      
            +----------------->| - /config (GET/POST for config_table)      |      
                               | - /transactions (GET logs)                 |      
                               | - /transactions/summary (GET aggregated)   |      
                               +--------------------------------------------+      

                                 [ SQLite DB / SQLAlchemy ORM ]

High-Level Technical Documentation
FastAPI as the Web Framework
We use FastAPI for its lightweight, high-performance HTTP handling. This makes extending endpoints and adding middlewares straightforward.

SQLAlchemy ORM
The database.py file defines a Base and a SessionLocal for database access.

ConfigTable: stores the credentials, base URL, route name, and an integer rate_limit.
TransactionLog: records each request with fields for success/failure, timestamp, route, etc.
Dynamic Routing Logic
routes.py handles the dynamic GET/POST by extracting {route_name}/{method_name} from the URL. We look up the correct config in ConfigTable, then forward the request (using the Python requests library) to the base_url/method_name. If username/password are set, we use HTTP Basic Auth.

Rate Limiting
Implemented in rate_limiter.py. For each incoming request, we query how many times that route has been called in the last 24 hours. If it exceeds rate_limit, we return 429: Rate limit exceeded.

Admin Panel
admin.py provides:

GET /admin/config: Lists all configuration rows.
POST /admin/config: Creates a new row in ConfigTable.
GET /admin/transactions: Lists recent logs.
GET /admin/transactions/summary: Returns aggregated success/failure counts per route.#   M a y a n k - P a t e l -  
 