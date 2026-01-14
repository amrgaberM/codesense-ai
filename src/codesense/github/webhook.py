import os
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from groq import Groq
import httpx

router = APIRouter()

GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def verify_signature(payload: bytes, signature: str) -> bool:
    if not GITHUB_WEBHOOK_SECRET:
        return True
    expected = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def analyze_code(code: str) -> dict:
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a code reviewer. Review the code and provide: 1) Score out of 100, 2) List of issues with severity (critical/high/medium/low), 3) Suggestions. Be concise."},
            {"role": "user", "content": f"Review this code:\n\n{code}"}
        ],
        temperature=0.1
    )
    return {"review": response.choices[0].message.content}

async def post_comment(repo: str, pr_number: int, body: str):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"body": body}, headers=headers)

async def get_pr_files(repo: str, pr_number: int) -> list:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    payload = await request.body()
    
    if x_hub_signature_256 and not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    if x_github_event != "pull_request":
        return {"status": "ignored", "event": x_github_event}
    
    data = await request.json()
    action = data.get("action")
    
    if action not in ["opened", "synchronize"]:
        return {"status": "ignored", "action": action}
    
    pr = data.get("pull_request", {})
    pr_number = pr.get("number")
    repo = data.get("repository", {}).get("full_name")
    
    files = await get_pr_files(repo, pr_number)
    
    review_comments = ["## CodeSense AI Review\n"]
    
    for file in files[:5]:
        filename = file.get("filename", "")
        if not filename.endswith(('.py', '.js', '.ts', '.java', '.go')):
            continue
        
        patch = file.get("patch", "")
        if patch:
            result = analyze_code(patch)
            review_comments.append(f"### {filename}\n{result['review']}\n")
    
    if len(review_comments) > 1:
        comment_body = "\n".join(review_comments)
        await post_comment(repo, pr_number, comment_body)
    
    return {"status": "success", "pr": pr_number}
