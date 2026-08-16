"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.database import create_tables
from app.api.v1 import calculate, history

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Quantitative Finance Calculator API",
    description="RESTful API for fundamental quantitative finance calculations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Include routers
app.include_router(calculate.router)
app.include_router(history.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Quantitative Finance Calculator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
