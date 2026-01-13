"""
CodeSense AI - REST API

FastAPI application for programmatic code review access.
"""

import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from codesense import __version__
from codesense.core import CodeAnalyzer, detect_language
from codesense.models import FileReview, ReviewResult, Severity, IssueCategory
from codesense.utils.config import settings


# ============================================
# Request/Response Models
# ============================================

class CodeReviewRequest(BaseModel):
    """Request body for code review."""
    code: str = Field(..., description="Source code to review", min_length=1)
    filename: Optional[str] = Field(None, description="Filename for language detection")
    language: Optional[str] = Field(None, description="Programming language (auto-detected if not provided)")
    review_type: str = Field("full", description="Review type: full, security, quick")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    return a / b",
                "filename": "calculator.py",
                "language": "python",
                "review_type": "full"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    llm_provider: str


class ReviewResponse(BaseModel):
    """Response for code review."""
    id: str
    filename: str
    language: str
    lines_of_code: int
    total_issues: int
    quality_score: int
    summary: Optional[str]
    issues: list[dict]
    review_time_ms: int


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="CodeSense AI",
    description="AI-Powered Code Review Assistant API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global analyzer instance (initialized lazily)
_analyzer: Optional[CodeAnalyzer] = None


def get_analyzer() -> CodeAnalyzer:
    """Get or create the code analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = CodeAnalyzer()
    return _analyzer


# ============================================
# API Endpoints
# ============================================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "CodeSense AI",
        "version": __version__,
        "description": "AI-Powered Code Review Assistant",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        llm_provider=settings.llm_provider
    )


@app.post("/api/review", response_model=ReviewResponse, tags=["Review"])
async def review_code(request: CodeReviewRequest):
    """
    Review code for issues, bugs, and security vulnerabilities.
    
    This is the main endpoint for code review. Submit your code
    and receive detailed analysis with actionable feedback.
    """
    start_time = time.time()
    review_id = str(uuid.uuid4())[:8]
    
    try:
        analyzer = get_analyzer()
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not configured: {str(e)}. Check API keys."
        )
    
    # Perform review
    try:
        file_review = analyzer.review_code(
            code=request.code,
            filename=request.filename,
            language=request.language,
            review_type=request.review_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Review failed: {str(e)}"
        )
    
    # Calculate score
    quality_score = 100
    if file_review.issues:
        penalty = sum(
            25 if i.severity == Severity.CRITICAL else
            15 if i.severity == Severity.HIGH else
            8 if i.severity == Severity.MEDIUM else
            3 if i.severity == Severity.LOW else 1
            for i in file_review.issues
        )
        quality_score = max(0, 100 - penalty)
    
    review_time_ms = int((time.time() - start_time) * 1000)
    
    return ReviewResponse(
        id=review_id,
        filename=file_review.filename,
        language=file_review.language,
        lines_of_code=file_review.lines_of_code,
        total_issues=len(file_review.issues),
        quality_score=quality_score,
        summary=file_review.summary,
        issues=[issue.model_dump() for issue in file_review.issues],
        review_time_ms=review_time_ms
    )


@app.post("/api/review/quick", tags=["Review"])
async def quick_review(request: CodeReviewRequest):
    """Quick review focusing on top 3-5 issues only."""
    request.review_type = "quick"
    return await review_code(request)


@app.post("/api/review/security", tags=["Review"])
async def security_review(request: CodeReviewRequest):
    """Security-focused review."""
    request.review_type = "security"
    return await review_code(request)


@app.get("/api/languages", tags=["Utilities"])
async def list_languages():
    """List supported programming languages."""
    from codesense.core.detector import EXTENSION_MAP
    
    languages = sorted(set(EXTENSION_MAP.values()))
    
    lang_extensions = {}
    for ext, lang in EXTENSION_MAP.items():
        if lang not in lang_extensions:
            lang_extensions[lang] = []
        lang_extensions[lang].append(ext)
    
    return {
        "languages": [
            {
                "name": lang,
                "extensions": sorted(lang_extensions.get(lang, []))
            }
            for lang in languages
        ]
    }


@app.get("/api/detect-language", tags=["Utilities"])
async def detect_lang(
    filename: Optional[str] = Query(None, description="Filename to detect language from"),
    code: Optional[str] = Query(None, description="Code snippet to detect language from")
):
    """Detect programming language from filename or code."""
    if not filename and not code:
        raise HTTPException(
            status_code=400,
            detail="Provide either filename or code parameter"
        )
    
    language = detect_language(code=code, filename=filename)
    
    return {
        "language": language,
        "filename": filename
    }


# ============================================
# Run with uvicorn
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "codesense.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
