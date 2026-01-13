import os
from groq import Groq

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

code = '''
def hello():
    print("world")
'''

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a code reviewer. Respond ONLY with valid JSON."},
        {"role": "user", "content": f'''Review this code and respond with JSON only:
{code}

Format:
{{"summary": "brief summary", "issues": [{{"title": "issue name", "severity": "low", "description": "details"}}]}}
'''}
    ],
    temperature=0.1
)

print(response.choices[0].message.content)
