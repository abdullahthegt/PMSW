"""
Automotive Decision Support System (DSS) - FastAPI Backend
RESTful API for sprint planning and resource analysis
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import init_db
from src.controllers import (
    teams_router, sprints_router, tasks_router,
    members_router, resources_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")
    yield
    # Shutdown
    print("Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Automotive DSS API",
    description="API for Sprint Planning and Resource Analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(teams_router)
app.include_router(sprints_router)
app.include_router(tasks_router)
app.include_router(members_router)
app.include_router(resources_router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Automotive DSS API",
        "version": "1.0.0",
        "documentation": "/docs",
        "alternative_docs": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
