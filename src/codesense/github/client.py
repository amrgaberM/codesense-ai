"""LLM client for code analysis."""

import json
import re
from typing import Optional, Any
from abc import ABC, abstractmethod

from codesense.utils.config import settings
from codesense.llm.prompts import get_review_prompt, get_pr_review_prompt


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def analyze(self, code: str, **kwargs) -> dict[str, Any]:
        """Analyze code and return structured results."""
        pass
    
    @abstractmethod
    def analyze_sync(self, code: str, **kwargs) -> dict[str, Any]:
        """Synchronous version of analyze."""
        pass


class GroqClient(BaseLLMClient):
    """Groq LLM client using Llama models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Set GROQ_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Lazy import to avoid dependency issues
        from groq import Groq
        self.client = Groq(api_key=self.api_key)
    
    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse LLM response to extract JSON."""
        # Try to extract JSON from the response
        # Sometimes LLMs wrap JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        
        # Clean up the content
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            # Remove trailing commas
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Return error structure if parsing fails
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content[:500],
                    "parse_error": str(e)
                }
    
    def analyze_sync(
        self,
        code: str,
        language: str = "python",
        filename: str = "code",
        review_type: str = "full"
    ) -> dict[str, Any]:
        """
        Synchronously analyze code using Groq.
        
        Args:
            code: Source code to analyze
            language: Programming language
            filename: Name of the file
            review_type: Type of review (full, security, quick)
        
        Returns:
            Parsed analysis results as dictionary
        """
        system_prompt, user_prompt = get_review_prompt(
            code=code,
            language=language,
            filename=filename,
            review_type=review_type
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent output
            max_tokens=4096,
        )
        
        content = response.choices[0].message.content
        return self._parse_response(content)
    
    async def analyze(
        self,
        code: str,
        language: str = "python",
        filename: str = "code",
        review_type: str = "full"
    ) -> dict[str, Any]:
        """Async version - wraps sync for now since Groq SDK is sync."""
        # For true async, you'd use httpx directly
        # For simplicity, we use sync version
        return self.analyze_sync(code, language, filename, review_type)
    
    def analyze_pr_diff(self, diff: str, pr_title: str, files_changed: int) -> dict[str, Any]:
        """Analyze a PR diff."""
        system_prompt, user_prompt = get_pr_review_prompt(
            diff=diff,
            pr_title=pr_title,
            files_changed=files_changed
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        
        content = response.choices[0].message.content
        return self._parse_response(content)


class OpenAIClient(BaseLLMClient):
    """OpenAI LLM client."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse LLM response to extract JSON."""
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content[:500],
                    "parse_error": str(e)
                }
    
    def analyze_sync(
        self,
        code: str,
        language: str = "python",
        filename: str = "code",
        review_type: str = "full"
    ) -> dict[str, Any]:
        """Synchronously analyze code using OpenAI."""
        system_prompt, user_prompt = get_review_prompt(
            code=code,
            language=language,
            filename=filename,
            review_type=review_type
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        
        content = response.choices[0].message.content
        return self._parse_response(content)
    
    async def analyze(
        self,
        code: str,
        language: str = "python",
        filename: str = "code",
        review_type: str = "full"
    ) -> dict[str, Any]:
        """Async version."""
        return self.analyze_sync(code, language, filename, review_type)


def get_llm_client(provider: Optional[str] = None) -> BaseLLMClient:
    """
    Factory function to get the appropriate LLM client.
    
    Args:
        provider: LLM provider ('groq' or 'openai'). 
                 Defaults to settings.llm_provider
    
    Returns:
        Configured LLM client instance
    """
    provider = provider or settings.llm_provider
    
    if provider == "groq":
        return GroqClient()
    elif provider == "openai":
        return OpenAIClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
