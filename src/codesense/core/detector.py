EXTENSION_MAP = {
    '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
    '.java': 'java', '.go': 'go', '.rs': 'rust', '.rb': 'ruby',
    '.php': 'php', '.c': 'c', '.cpp': 'cpp', '.cs': 'csharp'
}

def detect_language(code=None, filename=None):
    if filename:
        for ext, lang in EXTENSION_MAP.items():
            if filename.endswith(ext):
                return lang
    if code:
        if 'def ' in code or 'import ' in code:
            return 'python'
        if 'const ' in code or 'function ' in code:
            return 'javascript'
    return 'text'
