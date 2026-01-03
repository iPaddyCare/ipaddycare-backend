from email import message
from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="iPaddyCare - AI Powered Paddy Field Monitoring System",
    description="iPaddyCare is an AI-powered paddy field monitoring system that uses machine learning to monitor and analyze paddy fields .",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "iPaddyCare",
        "url": "https://ipaddycare.com",
        "email": "contact@ipaddycare.com",
    },
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message" : "Welcome to iPaddyCare - AI Powered Paddy Field Monitoring System"}