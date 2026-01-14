import os
from fastapi import APIRouter, Request, Header
from typing import Optional
from groq import Groq
import httpx

router = APIRouter()

def analyze_code(code: str) -> str:
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are CodeSense AI, a code review bot. Analyze the code and respond in this exact format:

## Code Review Summary

**Quality Score:** X/100

### Critical Issues
- Issue description (Line X)

### High Severity
- Issue description (Line X)

### Medium Severity  
- Issue description (Line X)

### Recommendations
1. Recommendation
2. Recommendation

Be specific with line numbers and provide clear fix suggestions."""},
            {"role": "user", "content": f"Review this code:\n\n{code}"}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

async def post_comment(repo: str, pr_number: int, body: str):
    token = os.environ.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={"body": body}, headers=headers)
        return r.status_code

async def get_pr_files(repo: str, pr_number: int) -> list:
    token = os.environ.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        return r.json()

@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None)
):
    if x_github_event != "pull_request":
        return {"status": "ignored"}
    
    data = await request.json()
    action = data.get("action")
    
    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "action": action}
    
    pr = data.get("pull_request", {})
    pr_number = pr.get("number")
    repo = data.get("repository", {}).get("full_name")
    
    files = await get_pr_files(repo, pr_number)
    
    all_patches = []
    for f in files:
        patch = f.get("patch", "")
        filename = f.get("filename", "")
        if patch:
            all_patches.append(f"File: {filename}\n{patch}")
    
    if all_patches:
        code_to_review = "\n\n".join(all_patches)[:4000]
        review = analyze_code(code_to_review)
        comment = f"# CodeSense AI\n\n{review}\n\n---\n*Automated code review by [CodeSense AI](https://github.com/amrgaberM/codesense-ai)*"
        status = await post_comment(repo, pr_number, comment)
        return {"status": "success", "pr": pr_number, "comment_status": status}
    
    return {"status": "success", "pr": pr_number, "comment_status": "no_files"}
