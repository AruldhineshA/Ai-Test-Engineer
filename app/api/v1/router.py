"""
API V1 Router
==============
Combines all v1 routers into one.
This single router is included in main.py.

LEARN: FastAPI lets you split routes into multiple files,
then combine them here. This keeps code organized.
"""

from fastapi import APIRouter

from app.api.v1 import documents, testcases, scripts, projects

api_v1_router = APIRouter()

# Each include_router adds a group of endpoints
api_v1_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"],  # Groups endpoints in Swagger docs
)

api_v1_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

api_v1_router.include_router(
    testcases.router,
    prefix="/testcases",
    tags=["Test Cases"],
)

api_v1_router.include_router(
    scripts.router,
    prefix="/scripts",
    tags=["Scripts"],
)
