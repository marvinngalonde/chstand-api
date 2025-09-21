"""
Main application module for FastAPI backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .v1.auth.router import router as auth_router
from .v1.applications.router import router as apps_router
from .v1.companies.router import router as companies_router
from .v1.reports.router import router as reports_router
from .v1.settings.router import router as settings_router
from .v2.auth.router import router as v2_auth_router
from .v2.applications.router import router as v2_apps_router
from .config import CORS_ORIGINS
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Stands Registration API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(apps_router, prefix="/api/v1")
app.include_router(companies_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(v2_auth_router, prefix="/api/v2")
app.include_router(v2_apps_router, prefix="/api/v2")

# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {"status": "ok"}
