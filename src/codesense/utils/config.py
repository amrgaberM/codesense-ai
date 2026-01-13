import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    groq_api_key: str = os.environ.get('GROQ_API_KEY', '')
    groq_model: str = 'llama-3.3-70b-versatile'
    llm_provider: str = 'groq'
    api_host: str = '0.0.0.0'
    api_port: int = 8000

settings = Settings()
