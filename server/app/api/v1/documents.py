"""
Document Endpoints
===================
Handles document upload, retrieval, and AI analysis.

LEARN:
- UploadFile: FastAPI's way to handle file uploads
- BackgroundTasks: Run slow tasks without blocking the response
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.document import DocumentResponse, DocumentAnalyzeResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    project_id: int = Query(..., description="Filter documents by project ID"),
    db: AsyncSession = Depends(get_db),
):
    """List all documents for a project."""
    service = DocumentService(db)
    return await service.list_by_project(project_id)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a document (PDF, DOCX, or Markdown).

    LEARN: UploadFile = File(...)
    - File(...) means this field is REQUIRED
    - UploadFile gives you: file.filename, file.content_type, file.read()
    - FastAPI handles multipart/form-data automatically
    """
    service = DocumentService(db)
    return await service.upload(project_id=project_id, file=file)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get document details by ID."""
    service = DocumentService(db)
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )
    return document


@router.post("/{document_id}/analyze", response_model=DocumentAnalyzeResponse)
async def analyze_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """
    Trigger AI analysis on an uploaded document.
    Extracts requirements, functional flows, and key sections.

    LEARN: This endpoint calls the AI Engine layer
    - Reads the document text
    - Sends it to LLM (Gemini/Groq/Ollama)
    - Returns structured analysis
    """
    service = DocumentService(db)
    return await service.analyze(document_id)
