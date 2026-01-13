from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"
    DOCUMENTATION = "documentation"


class Issue(BaseModel):
    title: str
    description: str
    severity: Severity
    category: IssueCategory
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    suggested_code: Optional[str] = None


class FileReview(BaseModel):
    filename: str
    language: str
    lines_of_code: int
    issues: list[Issue] = []
    summary: Optional[str] = None

    @property
    def issue_count(self):
        counts = {s.value: 0 for s in Severity}
        for issue in self.issues:
            counts[issue.severity.value] += 1
        return counts


class ReviewResult(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    files: list[FileReview] = []
    total_issues: int = 0
    review_time_ms: int = 0
    overall_summary: Optional[str] = None
    overall_score: Optional[int] = None

    def add_file_review(self, file_review: FileReview):
        self.files.append(file_review)
        self.total_issues += len(file_review.issues)

    @property
    def severity_breakdown(self):
        counts = {s.value: 0 for s in Severity}
        for f in self.files:
            for issue in f.issues:
                counts[issue.severity.value] += 1
        return counts


class ReviewRequest(BaseModel):
    code: Optional[str] = None
    filename: Optional[str] = None
    language: Optional[str] = None
