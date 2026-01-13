"""
CodeSense AI - Command Line Interface

A beautiful CLI for AI-powered code review.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown

from codesense import __version__
from codesense.core import CodeAnalyzer, detect_language
from codesense.models import Severity, FileReview, ReviewResult

# Initialize Typer app and Rich console
app = typer.Typer(
    name="codesense",
    help="🔍 AI-Powered Code Review Assistant",
    add_completion=False,
)
console = Console()


# Severity colors and emojis
SEVERITY_STYLES = {
    Severity.CRITICAL: ("red bold", "🔴"),
    Severity.HIGH: ("orange1", "🟠"),
    Severity.MEDIUM: ("yellow", "🟡"),
    Severity.LOW: ("blue", "🔵"),
    Severity.INFO: ("dim", "⚪"),
}


def print_banner():
    """Print the CodeSense banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ██████╗ ██████╗ ███████╗███████╗███████╗███╗   ██╗███████╗███████╗ ║
║  ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║██╔════╝██╔════╝ ║
║  ██║     ██║   ██║██║  ██║█████╗  ███████╗█████╗  ██╔██╗ ██║███████╗█████╗   ║
║  ██║     ██║   ██║██║  ██║██╔══╝  ╚════██║██╔══╝  ██║╚██╗██║╚════██║██╔══╝   ║
║  ╚██████╗╚██████╔╝██████╔╝███████╗███████║███████╗██║ ╚████║███████║███████╗ ║
║   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝ ║
║                                                           ║
║               AI-Powered Code Review Assistant            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="cyan")


def print_file_review(review: FileReview):
    """Print a file review with rich formatting."""
    # File header
    console.print()
    console.print(Panel(
        f"[bold]{review.filename}[/bold]\n"
        f"Language: {review.language} | Lines: {review.lines_of_code}",
        title="📄 File Review",
        border_style="cyan"
    ))
    
    # Summary
    if review.summary:
        console.print(f"\n[italic]{review.summary}[/italic]\n")
    
    # No issues case
    if not review.issues:
        console.print("[green]✅ No issues found! Looking good.[/green]\n")
        return
    
    # Issue counts table
    counts = review.issue_count
    table = Table(title="Issue Summary", show_header=True, header_style="bold")
    table.add_column("Severity", style="dim")
    table.add_column("Count", justify="right")
    
    for severity in Severity:
        style, emoji = SEVERITY_STYLES[severity]
        count = counts.get(severity.value, 0)
        if count > 0:
            table.add_row(f"{emoji} {severity.value.upper()}", f"[{style}]{count}[/{style}]")
    
    console.print(table)
    console.print()
    
    # Individual issues
    for i, issue in enumerate(review.issues, 1):
        style, emoji = SEVERITY_STYLES[issue.severity]
        
        # Issue header
        console.print(f"{emoji} [bold {style}]Issue #{i}: {issue.title}[/bold {style}]")
        console.print(f"   [dim]Severity:[/dim] [{style}]{issue.severity.value.upper()}[/{style}] | "
                     f"[dim]Category:[/dim] {issue.category.value}")
        
        if issue.line_start:
            line_info = f"Line {issue.line_start}"
            if issue.line_end and issue.line_end != issue.line_start:
                line_info += f"-{issue.line_end}"
            console.print(f"   [dim]Location:[/dim] {line_info}")
        
        console.print()
        console.print(f"   {issue.description}")
        
        # Code snippet
        if issue.code_snippet:
            console.print()
            console.print("   [dim]Problematic code:[/dim]")
            syntax = Syntax(
                issue.code_snippet,
                review.language,
                theme="monokai",
                line_numbers=True,
                start_line=issue.line_start or 1,
                padding=1
            )
            console.print(syntax)
        
        # Suggestion
        if issue.suggestion:
            console.print()
            console.print(f"   [green]💡 Suggestion:[/green] {issue.suggestion}")
        
        # Suggested fix
        if issue.suggested_code:
            console.print()
            console.print("   [green]Fixed code:[/green]")
            syntax = Syntax(
                issue.suggested_code,
                review.language,
                theme="monokai",
                padding=1
            )
            console.print(syntax)
        
        console.print()
        console.print("─" * 60)
        console.print()


def print_review_result(result: ReviewResult):
    """Print complete review result."""
    # Overall summary panel
    score_color = "green" if result.overall_score >= 80 else "yellow" if result.overall_score >= 60 else "red"
    
    console.print(Panel(
        f"[bold]Review ID:[/bold] {result.id}\n"
        f"[bold]Files Reviewed:[/bold] {len(result.files)}\n"
        f"[bold]Total Issues:[/bold] {result.total_issues}\n"
        f"[bold]Quality Score:[/bold] [{score_color}]{result.overall_score}/100[/{score_color}]\n"
        f"[bold]Time:[/bold] {result.review_time_ms}ms",
        title="📊 Review Summary",
        border_style="green" if result.overall_score >= 80 else "yellow" if result.overall_score >= 60 else "red"
    ))
    
    if result.overall_summary:
        console.print(f"\n{result.overall_summary}\n")
    
    # Print each file review
    for file_review in result.files:
        print_file_review(file_review)


# ============================================
# CLI Commands
# ============================================

@app.command()
def review(
    path: Path = typer.Argument(
        ...,
        help="File or directory to review",
        exists=True,
    ),
    review_type: str = typer.Option(
        "full",
        "--type", "-t",
        help="Review type: full, security, quick"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save results to file (supports .json, .md)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed output"
    ),
):
    """
    🔍 Review code for issues, bugs, and security vulnerabilities.
    
    Examples:
        codesense review app.py
        codesense review src/ --type security
        codesense review main.py -o report.md
    """
    # Show banner if verbose
    if verbose:
        print_banner()
    
    console.print(f"\n[cyan]🔍 Starting code review...[/cyan]\n")
    
    # Initialize analyzer
    try:
        analyzer = CodeAnalyzer()
    except ValueError as e:
        console.print(f"[red]❌ Configuration error: {e}[/red]")
        console.print("[dim]Make sure to set your API key in .env file[/dim]")
        raise typer.Exit(1)
    
    # Collect files to review
    files_to_review = []
    
    if path.is_file():
        files_to_review = [str(path)]
    else:
        # Find all supported files in directory
        supported_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.rb', '.php'}
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in supported_extensions:
                # Skip common non-source directories
                if not any(part.startswith('.') or part in ['node_modules', 'venv', '__pycache__', 'dist', 'build'] 
                          for part in file_path.parts):
                    files_to_review.append(str(file_path))
    
    if not files_to_review:
        console.print("[yellow]⚠️ No supported files found to review.[/yellow]")
        raise typer.Exit(0)
    
    console.print(f"[dim]Found {len(files_to_review)} file(s) to review[/dim]\n")
    
    # Perform review with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing code...", total=None)
        
        if len(files_to_review) == 1:
            # Single file review
            result = analyzer.review_file(files_to_review[0], review_type)
            # Wrap in ReviewResult for consistent output
            review_result = ReviewResult(
                id="single",
                files=[result],
                total_issues=len(result.issues)
            )
            review_result.overall_score = analyzer._calculate_score(review_result)
        else:
            # Multiple files review
            review_result = analyzer.review_multiple(files_to_review, review_type)
        
        progress.update(task, completed=True)
    
    # Print results
    print_review_result(review_result)
    
    # Save to file if requested
    if output:
        if output.suffix == '.json':
            import json
            output.write_text(json.dumps(review_result.model_dump(), indent=2, default=str))
            console.print(f"[green]✅ Results saved to {output}[/green]")
        elif output.suffix == '.md':
            output.write_text(review_result.to_markdown())
            console.print(f"[green]✅ Results saved to {output}[/green]")
        else:
            console.print(f"[yellow]⚠️ Unsupported output format. Use .json or .md[/yellow]")
    
    # Exit with error code if critical issues found
    if review_result.severity_breakdown.get("critical", 0) > 0:
        raise typer.Exit(1)


@app.command()
def check(
    code: str = typer.Argument(
        ...,
        help="Code snippet to review (use quotes)"
    ),
    language: str = typer.Option(
        "python",
        "--language", "-l",
        help="Programming language"
    ),
):
    """
    ⚡ Quick check a code snippet.
    
    Example:
        codesense check "def add(a,b): return a+b" -l python
    """
    console.print(f"\n[cyan]⚡ Quick code check...[/cyan]\n")
    
    try:
        analyzer = CodeAnalyzer()
        result = analyzer.review_code(code=code, language=language, review_type="quick")
        print_file_review(result)
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def languages():
    """📋 List supported programming languages."""
    from codesense.core.detector import EXTENSION_MAP
    
    # Get unique languages
    languages = sorted(set(EXTENSION_MAP.values()))
    
    console.print("\n[bold cyan]Supported Languages:[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("Language", style="green")
    table.add_column("Extensions")
    
    lang_extensions = {}
    for ext, lang in EXTENSION_MAP.items():
        if lang not in lang_extensions:
            lang_extensions[lang] = []
        lang_extensions[lang].append(ext)
    
    for lang in languages:
        exts = ", ".join(sorted(lang_extensions.get(lang, [])))
        table.add_row(lang.capitalize(), exts)
    
    console.print(table)
    console.print()


@app.command()
def version():
    """Show version information."""
    console.print(f"\n[cyan]CodeSense AI[/cyan] version [bold]{__version__}[/bold]\n")


@app.callback()
def main():
    """
    🔍 CodeSense AI - AI-Powered Code Review Assistant
    
    Analyze your code for bugs, security issues, and best practices
    using state-of-the-art language models.
    """
    pass


if __name__ == "__main__":
    app()
