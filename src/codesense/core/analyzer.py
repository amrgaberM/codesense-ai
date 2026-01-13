"""Main code analyzer that orchestrates the review process."""

import time
import uuid
from pathlib import Path
from typing import Optional, Any

from codesense.models import (
    ReviewResult,
    FileReview,
    Issue,
    Severity,
    IssueCategory
)
from codesense.llm import get_llm_client, BaseLLMClient
from codesense.core.detector import detect_language


class CodeAnalyzer:
    """
    Main code analysis orchestrator.
    
    Coordinates LLM-based code review, handling file processing,
    language detection, and result formatting.
    """
    
    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        provider: Optional[str] = None
    ):
        """
        Initialize the code analyzer.
        
        Args:
            llm_client: Pre-configured LLM client (optional)
            provider: LLM provider name if no client provided
        """
        self.llm_client = llm_client or get_llm_client(provider)
    
    def _parse_issue(self, issue_data: dict[str, Any]) -> Issue:
        """Parse an issue from LLM response to Issue model."""
        # Map severity string to enum
        severity_str = issue_data.get("severity", "medium").lower()
        try:
            severity = Severity(severity_str)
        except ValueError:
            severity = Severity.MEDIUM
        
        # Map category string to enum
        category_str = issue_data.get("category", "best_practice").lower()
        try:
            category = IssueCategory(category_str)
        except ValueError:
            category = IssueCategory.BEST_PRACTICE
        
        return Issue(
            title=issue_data.get("title", "Unknown Issue"),
            description=issue_data.get("description", "No description provided"),
            severity=severity,
            category=category,
            line_start=issue_data.get("line_start"),
            line_end=issue_data.get("line_end"),
            code_snippet=issue_data.get("code_snippet"),
            suggestion=issue_data.get("suggestion"),
            suggested_code=issue_data.get("suggested_code")
        )
    
    def review_code(
        self,
        code: str,
        filename: Optional[str] = None,
        language: Optional[str] = None,
        review_type: str = "full"
    ) -> FileReview:
        """
        Review a single piece of code.
        
        Args:
            code: Source code to review
            filename: Name of the file (for language detection)
            language: Programming language (auto-detected if not provided)
            review_type: Type of review ('full', 'security', 'quick')
        
        Returns:
            FileReview containing analysis results
        """
        # Detect language if not provided
        if not language:
            language = detect_language(code=code, filename=filename)
        
        # Count lines
        lines_of_code = len(code.splitlines())
        
        # Get LLM analysis
        result = self.llm_client.analyze_sync(
            code=code,
            language=language,
            filename=filename or "code",
            review_type=review_type
        )
        
        # Handle error in LLM response
        if "error" in result:
            return FileReview(
                filename=filename or "code",
                language=language,
                lines_of_code=lines_of_code,
                issues=[
                    Issue(
                        title="Analysis Error",
                        description=f"Failed to analyze code: {result.get('error')}",
                        severity=Severity.INFO,
                        category=IssueCategory.DOCUMENTATION,
                        suggestion="Please try again or check your code format"
                    )
                ],
                summary="Analysis encountered an error"
            )
        
        # Parse issues from response
        issues = []
        for issue_data in result.get("issues", []):
            try:
                issue = self._parse_issue(issue_data)
                issues.append(issue)
            except Exception as e:
                # Skip malformed issues
                continue
        
        return FileReview(
            filename=filename or "code",
            language=language,
            lines_of_code=lines_of_code,
            issues=issues,
            summary=result.get("summary")
        )
    
    def review_file(
        self,
        file_path: str,
        review_type: str = "full"
    ) -> FileReview:
        """
        Review a file from the filesystem.
        
        Args:
            file_path: Path to the file to review
            review_type: Type of review
        
        Returns:
            FileReview containing analysis results
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        # Read file content
        try:
            code = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            code = path.read_text(encoding="latin-1")
        
        return self.review_code(
            code=code,
            filename=path.name,
            review_type=review_type
        )
    
    def review_multiple(
        self,
        files: list[str],
        review_type: str = "full"
    ) -> ReviewResult:
        """
        Review multiple files.
        
        Args:
            files: List of file paths to review
            review_type: Type of review
        
        Returns:
            ReviewResult containing all file reviews
        """
        start_time = time.time()
        review_id = str(uuid.uuid4())[:8]
        
        result = ReviewResult(
            id=review_id,
            total_issues=0
        )
        
        for file_path in files:
            try:
                file_review = self.review_file(file_path, review_type)
                result.add_file_review(file_review)
            except Exception as e:
                # Add error review for failed files
                result.add_file_review(FileReview(
                    filename=file_path,
                    language="unknown",
                    lines_of_code=0,
                    issues=[
                        Issue(
                            title="File Processing Error",
                            description=str(e),
                            severity=Severity.INFO,
                            category=IssueCategory.DOCUMENTATION
                        )
                    ]
                ))
        
        # Calculate review time
        result.review_time_ms = int((time.time() - start_time) * 1000)
        
        # Generate overall summary
        result.overall_summary = self._generate_overall_summary(result)
        
        # Calculate overall score
        result.overall_score = self._calculate_score(result)
        
        return result
    
    def _generate_overall_summary(self, result: ReviewResult) -> str:
        """Generate an overall summary of the review."""
        total = result.total_issues
        breakdown = result.severity_breakdown
        
        if total == 0:
            return "✅ No issues found! The code looks good."
        
        parts = []
        if breakdown.get("critical", 0) > 0:
            parts.append(f"{breakdown['critical']} critical")
        if breakdown.get("high", 0) > 0:
            parts.append(f"{breakdown['high']} high")
        if breakdown.get("medium", 0) > 0:
            parts.append(f"{breakdown['medium']} medium")
        if breakdown.get("low", 0) > 0:
            parts.append(f"{breakdown['low']} low")
        
        summary = f"Found {total} issues: {', '.join(parts)}."
        
        if breakdown.get("critical", 0) > 0:
            summary += " ⚠️ Critical issues require immediate attention!"
        
        return summary
    
    def _calculate_score(self, result: ReviewResult) -> int:
        """Calculate an overall quality score (0-100)."""
        if result.total_issues == 0:
            return 100
        
        breakdown = result.severity_breakdown
        
        # Weighted penalty system
        penalty = (
            breakdown.get("critical", 0) * 25 +
            breakdown.get("high", 0) * 15 +
            breakdown.get("medium", 0) * 8 +
            breakdown.get("low", 0) * 3 +
            breakdown.get("info", 0) * 1
        )
        
        # Score starts at 100, reduce by penalty, minimum 0
        score = max(0, 100 - penalty)
        
        return score


# Convenience function for quick reviews
def analyze_code(
    code: str,
    filename: Optional[str] = None,
    language: Optional[str] = None,
    review_type: str = "full"
) -> FileReview:
    """
    Quick function to analyze code.
    
    Args:
        code: Source code to analyze
        filename: Optional filename
        language: Optional language override
        review_type: Type of review
    
    Returns:
        FileReview with analysis results
    """
    analyzer = CodeAnalyzer()
    return analyzer.review_code(
        code=code,
        filename=filename,
        language=language,
        review_type=review_type
    )


def analyze_file(file_path: str, review_type: str = "full") -> FileReview:
    """
    Quick function to analyze a file.
    
    Args:
        file_path: Path to file
        review_type: Type of review
    
    Returns:
        FileReview with analysis results
    """
    analyzer = CodeAnalyzer()
    return analyzer.review_file(file_path, review_type)
