# CodeSense AI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deployed on Railway](https://img.shields.io/badge/Deployed-Railway-blueviolet)](https://railway.app)

**Automated Code Review Platform** — Detect security vulnerabilities, bugs, and code quality issues using AI before they reach production.

[Live Demo](https://your-app.streamlit.app) · [API Docs](https://codesense-ai-production-78ab.up.railway.app/docs) · [Report Bug](https://github.com/amrgaberM/codesense-ai/issues)

---

## Overview

CodeSense AI is an intelligent code analysis tool that integrates directly into your development workflow. It provides automated code reviews through multiple interfaces:

- **GitHub Integration** — Automatically reviews every Pull Request
- **REST API** — Integrate into CI/CD pipelines
- **Command Line** — Review code locally before committing
- **Web Interface** — Quick analysis through browser

### Why CodeSense AI?

| Problem | Solution |
|---------|----------|
| Manual code reviews are slow | Instant AI-powered analysis |
| Security issues slip through | Automated vulnerability detection |
| Inconsistent review quality | Standardized analysis across all code |
| Delayed feedback loops | Real-time PR comments |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CodeSense AI                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐     ┌──────────────┐     ┌─────────────┐     │
│   │ GitHub  │────>│              │────>│   Groq AI   │     │
│   │ Webhook │     │   FastAPI    │     │  (Llama 3)  │     │
│   └─────────┘     │   Backend    │     └─────────────┘     │
│                   │              │            │             │
│   ┌─────────┐     │              │            v             │
│   │   CLI   │────>│              │     ┌─────────────┐     │
│   └─────────┘     │              │     │   Review    │     │
│                   │              │<────│   Results   │     │
│   ┌─────────┐     │              │     └─────────────┘     │
│   │   API   │────>│              │                         │
│   └─────────┘     └──────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### Security Analysis
- SQL Injection detection
- Cross-Site Scripting (XSS) vulnerabilities
- Hardcoded secrets and credentials
- Command injection risks
- Authentication weaknesses

### Bug Detection
- Division by zero
- Null pointer dereferences
- Race conditions
- Logic errors
- Type mismatches

### Code Quality
- Best practice violations
- Code smell detection
- Performance anti-patterns
- Documentation gaps

---

## Installation

### Prerequisites
- Python 3.10+
- Groq API key ([Get free key](https://console.groq.com/keys))

### Setup

```bash
git clone https://github.com/amrgaberM/codesense-ai.git
cd codesense-ai

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -e .

cp .env.example .env
# Add your GROQ_API_KEY to .env
```

---

## Usage

### Command Line Interface

```bash
# Review a file
codesense review app.py

# Security-focused review
codesense review src/ --type security

# Quick check
codesense check "def divide(a,b): return a/b" -l python
```

### REST API

```bash
# Start server
uvicorn codesense.api.app:app --reload

# Send review request
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"code": "eval(user_input)", "language": "python"}'
```

### Python SDK

```python
from codesense import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.review_code(
    code="password = 'admin123'",
    language="python"
)

for issue in result.issues:
    print(f"[{issue.severity}] {issue.title}")
    print(f"  Fix: {issue.suggestion}")
```

---

## GitHub Integration

CodeSense AI automatically reviews Pull Requests when configured as a webhook.

### How It Works

1. Developer opens a Pull Request
2. GitHub sends webhook to CodeSense API
3. CodeSense analyzes the changed files
4. Bot posts review comment on the PR

### Setup

1. Deploy API to Railway/Render
2. Add webhook in repository settings:
   - URL: `https://your-api.up.railway.app/webhook/github`
   - Events: Pull requests
3. Add `GITHUB_TOKEN` and `GROQ_API_KEY` to environment

### Example Output

```
## CodeSense AI Review

Issues Found:

1. [CRITICAL] SQL Injection Vulnerability
   Line 23: User input directly concatenated into query
   Fix: Use parameterized queries

2. [HIGH] Hardcoded Credentials  
   Line 45: Password stored in plain text
   Fix: Use environment variables or secrets manager

3. [MEDIUM] Missing Input Validation
   Line 12: No validation on user input
   Fix: Add type checking and sanitization
```

---

## Project Structure

```
codesense-ai/
├── src/codesense/
│   ├── api/           # FastAPI REST endpoints
│   ├── cli/           # Command line interface
│   ├── core/          # Analysis engine
│   ├── github/        # Webhook handlers
│   ├── llm/           # AI integration
│   └── models/        # Data structures
├── streamlit_app.py   # Web demo
├── requirements.txt
└── pyproject.toml
```

---

## Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for AI analysis |
| `GITHUB_TOKEN` | GitHub token for PR comments |
| `GITHUB_WEBHOOK_SECRET` | Webhook signature verification |

---

## Supported Languages

| Language | Extensions |
|----------|------------|
| Python | .py |
| JavaScript | .js, .jsx |
| TypeScript | .ts, .tsx |
| Java | .java |
| Go | .go |
| Rust | .rs |
| C/C++ | .c, .cpp, .h |

---

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** Groq (Llama 3.3 70B)
- **Frontend:** Streamlit
- **Deployment:** Railway
- **CI/CD:** GitHub Webhooks

---

## Roadmap

- [x] CLI tool
- [x] REST API
- [x] GitHub PR integration
- [x] Web demo (Streamlit)
- [ ] VS Code extension
- [ ] GitLab integration
- [ ] Custom rule configuration

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Author

**Amr Hassan** — AI Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-amrhassangaber-blue)](https://linkedin.com/in/amrhassangaber)
[![GitHub](https://img.shields.io/badge/GitHub-amrgaberM-black)](https://github.com/amrgaberM)

---

<p align="center">
Built for developers who ship quality code.
</p>