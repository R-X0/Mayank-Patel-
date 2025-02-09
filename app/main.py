from fastapi import FastAPI, status
from .database import Base, engine
from .routers import routes, admin

# Create all tables if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Accounting Integration Service",
    description="A modular API to route requests to various accounting systems (Tally, Miracle, etc.)",
    version="1.0.0",
)

# Include the public API routes (for dynamic routing to external systems)
app.include_router(routes.router, prefix="/api", tags=["API Routes"])
# Include the admin endpoints (for managing configuration and viewing logs)
app.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to the Accounting Integration API"}
