import os
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from groq import Groq
import httpx

router = APIRouter()

def analyze_code(code: str) -> str:
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Review this code. List issues and suggestions. Be concise."},
            {"role": "user", "content": f"Review:\n{code}"}
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

async def get_pr_diff(repo: str, pr_number: int) -> str:
    token = os.environ.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        return r.text

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
    
    diff = await get_pr_diff(repo, pr_number)
    
    if diff:
        review = analyze_code(diff[:3000])
        comment = f"## CodeSense AI Review\n\n{review}"
        status = await post_comment(repo, pr_number, comment)
        return {"status": "success", "pr": pr_number, "comment_status": status}
    
    return {"status": "success", "pr": pr_number, "comment_status": "no_diff"}
