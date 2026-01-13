SYSTEM_PROMPT = '''You are CodeSense AI, an expert code reviewer. Analyze code for bugs, security issues, and best practices. Always respond with valid JSON only, no markdown.'''

CODE_REVIEW_PROMPT = '''Review this {language} code:
`
{code}
`

Respond ONLY with this JSON format:
{{"summary": "brief assessment", "quality_score": 85, "issues": [{{"title": "Issue name", "description": "Details", "severity": "critical|high|medium|low|info", "category": "security|bug|performance|style|best_practice", "line_start": 1, "suggestion": "How to fix"}}]}}
'''

def get_review_prompt(code, language="python", filename="code", review_type="full"):
    user_prompt = CODE_REVIEW_PROMPT.format(code=code, language=language, filename=filename)
    return SYSTEM_PROMPT, user_prompt
