"""
Document Service
=================
Business logic for document upload and AI analysis.
This is where file handling meets AI processing.

FLOW:
1. User uploads a document (PDF, DOCX, MD, TXT)
2. File is saved to disk + DB record created
3. User triggers analysis → AI extracts text + identifies requirements
4. Parsed content is saved to DB for test case generation
"""

import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.document_analyzer import document_analyzer
from app.config import settings
from app.db.repositories.document_repo import DocumentRepository
from app.models.document import Document
from app.schemas.document import DocumentAnalyzeResponse

logger = logging.getLogger(__name__)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)

    async def upload(self, project_id: int, file: UploadFile) -> Document:
        """
        Upload and save a document file.

        STEPS:
        1. Validate file type
        2. Save file to disk (uploads/ folder)
        3. Create database record
        """
        # 1. Validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{ext}' not allowed. Allowed: {ALLOWED_EXTENSIONS}",
            )

        # 2. Save file to disk
        project_upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
        project_upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = project_upload_dir / file.filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 3. Create database record
        document = Document(
            project_id=project_id,
            filename=file.filename,
            file_path=str(file_path),
            file_type=ext.lstrip("."),
            status="uploaded",
        )
        return await self.repo.create(document)

    async def get_by_id(self, document_id: int) -> Document | None:
        """Get a document by ID."""
        return await self.repo.get_by_id(document_id)

    async def analyze(self, document_id: int) -> DocumentAnalyzeResponse:
        """
        Analyze a document using AI.

        STEPS:
        1. Get document from DB
        2. Extract text from file (PDF/DOCX/MD/TXT)
        3. Send text to AI for analysis
        4. Save parsed content to DB
        5. Return analysis results

        This connects the Document → AI Engine pipeline.
        """
        # 1. Get document from DB
        document = await self.repo.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )

        # Update status to analyzing
        await self.repo.update_status(document_id, "analyzing")

        try:
            # 2. Extract text from the file
            extracted_text = await document_analyzer.extract_text(
                file_path=document.file_path,
                file_type=document.file_type,
            )

            if not extracted_text.strip():
                await self.repo.update_status(document_id, "failed")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not extract text from document. File may be empty or image-only.",
                )

            # 3. Send to AI for structured analysis
            analysis = await document_analyzer.analyze(extracted_text)

            # 4. Save parsed content to DB (used later for test case generation)
            document.parsed_content = extracted_text
            document.status = "analyzed"
            await self.db.flush()
            await self.db.refresh(document)

            # 5. Return analysis results
            return DocumentAnalyzeResponse(
                document_id=document_id,
                status="analyzed",
                extracted_sections=analysis.get("sections", []),
                requirements_count=len(analysis.get("requirements", [])),
                message=f"Successfully analyzed '{document.filename}'. "
                        f"Found {len(analysis.get('sections', []))} sections, "
                        f"{len(analysis.get('requirements', []))} requirements, "
                        f"{len(analysis.get('functional_flows', []))} functional flows.",
            )

        except HTTPException:
            raise
        except Exception as e:
            # Update status to failed on error
            await self.repo.update_status(document_id, "failed")
            logger.error(f"Document analysis failed for {document_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {e}",
            )
