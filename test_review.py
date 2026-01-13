import os
import json
import re
from groq import Groq

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

code = '''
def divide(a, b):
    return a / b

password = "admin123"
'''

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a code reviewer. Find bugs and security issues."},
        {"role": "user", "content": f"Review this Python code:\n{code}"}
    ]
)

print(response.choices[0].message.content)
