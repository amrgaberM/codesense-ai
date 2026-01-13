# 🔍 CodeSense AI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)

**AI-Powered Code Review Assistant** - Catch bugs, security vulnerabilities, and code quality issues before they reach production.

<p align="center">
  <img src="docs/demo.gif" alt="CodeSense AI Demo" width="700">
</p>

## ✨ Features

- 🐛 **Bug Detection** - Find logic errors, null pointer issues, race conditions
- 🔒 **Security Analysis** - OWASP Top 10, injection vulnerabilities, authentication issues
- ⚡ **Performance Issues** - Inefficient algorithms, memory leaks, N+1 queries
- 📝 **Code Quality** - Best practices, code smells, maintainability
- 🔌 **GitHub Integration** - Automatic PR reviews with inline comments
- 🌐 **REST API** - Integrate into your CI/CD pipeline

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/amrgaberM/codesense-ai.git
cd codesense-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# Get free Groq API key at: https://console.groq.com/keys
GROQ_API_KEY=your_api_key_here
```

### Usage

#### CLI

```bash
# Review a single file
codesense review app.py

# Review with security focus
codesense review src/ --type security

# Quick check a code snippet
codesense check "def add(a,b): return a+b" -l python

# Save results to markdown
codesense review main.py -o report.md
```

#### API

```bash
# Start the API server
uvicorn codesense.api.app:app --reload

# Review code via API
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a,b): return a+b", "language": "python"}'
```

#### Python

```python
from codesense import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.review_code(
    code="def divide(a, b): return a / b",
    language="python"
)

for issue in result.issues:
    print(f"{issue.severity}: {issue.title}")
    print(f"  {issue.suggestion}")
```

## 📊 Example Output

```
╔══════════════════════════════════════════════════════════════╗
║                     📊 Review Summary                        ║
╠══════════════════════════════════════════════════════════════╣
║  Review ID: a1b2c3d4                                         ║
║  Files Reviewed: 1                                           ║
║  Total Issues: 3                                             ║
║  Quality Score: 72/100                                       ║
╚══════════════════════════════════════════════════════════════╝

🟠 Issue #1: Division by Zero Risk
   Severity: HIGH | Category: bug
   Location: Line 2
   
   The function does not handle the case when b is zero,
   which will cause a ZeroDivisionError.
   
   💡 Suggestion: Add a check for zero before dividing
   
   Fixed code:
   def divide(a, b):
       if b == 0:
           raise ValueError("Cannot divide by zero")
       return a / b
```

## 🔌 GitHub Integration

CodeSense AI can automatically review your Pull Requests:

1. Set up a webhook in your repository
2. Point it to your deployed CodeSense API
3. Get AI-powered review comments on every PR!

See [GitHub Setup Guide](docs/github-setup.md) for detailed instructions.

## 🛠️ Supported Languages

| Language | Extensions |
|----------|-----------|
| Python | .py, .pyw, .pyi |
| JavaScript | .js, .jsx, .mjs |
| TypeScript | .ts, .tsx |
| Java | .java |
| Go | .go |
| Rust | .rs |
| Ruby | .rb |
| PHP | .php |
| C/C++ | .c, .cpp, .h |
| C# | .cs |

## 📁 Project Structure

```
codesense-ai/
├── src/codesense/
│   ├── cli/          # Command line interface
│   ├── api/          # FastAPI REST API
│   ├── core/         # Analysis engine
│   ├── llm/          # LLM integration
│   ├── github/       # GitHub integration
│   └── models/       # Data models
├── tests/            # Test suite
├── docs/             # Documentation
└── examples/         # Usage examples
```

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/

# Format code
black src/ tests/
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Amr Hassan** - AI Engineer

- LinkedIn: [amrhassangaber](https://linkedin.com/in/amrhassangaber)
- GitHub: [@amrgaberM](https://github.com/amrgaberM)
- Medium: [@amrgabeerr20](https://medium.com/@amrgabeerr20)

---

<p align="center">
  Made with ❤️ and 🤖 AI
</p>
