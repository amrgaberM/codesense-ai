import json
import re
from abc import ABC, abstractmethod
from groq import Groq
from codesense.utils import settings
from codesense.llm.prompts import get_review_prompt


class BaseLLMClient(ABC):
    @abstractmethod
    def analyze_sync(self, code, **kwargs):
        pass


class GroqClient(BaseLLMClient):
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def _parse_response(self, content):
        try:
            json_match = re.search(r'`(?:json)?\s*([\s\S]*?)\s*`', content)
            if json_match:
                content = json_match.group(1)
            content = content.strip()
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            return json.loads(content)
        except Exception as e:
            return {
                "summary": "Analysis completed",
                "issues": [],
                "error": str(e)
            }

    def analyze_sync(self, code, language="python", filename="code", review_type="full"):
        system_prompt, user_prompt = get_review_prompt(code, language, filename, review_type)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        return self._parse_response(response.choices[0].message.content)


def get_llm_client(provider=None):
    return GroqClient()
