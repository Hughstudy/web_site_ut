"""
OpenAI Python API Connector Module

This module handles connections to the OpenAI API with proper error handling,
retry logic, and support for both sync/async operations.
"""

import os
import asyncio
import httpx
from typing import Optional, Dict, Any, List, Union, AsyncGenerator, Generator
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from dotenv import load_dotenv
from pydantic import BaseModel


# Load environment variables
load_dotenv()


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI API connection"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 60.0
    max_retries: int = 3
    model: str = "moonshotai/kimi-k2-0905"


class OpenAIConnector:
    """
    Handles synchronous connections to OpenAI API
    """

    def __init__(self, config: Optional[OpenAIConfig] = None):
        """
        Initialize the OpenAI connector

        Args:
            config: OpenAI configuration object
        """
        self.config = config or OpenAIConfig()

        # Get API key from config or environment
        api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass in config.")

        # Get base URL from config or environment
        base_url = self.config.base_url or os.environ.get("OPENAI_BASE_URL")

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=httpx.Timeout(self.config.timeout),
            max_retries=self.config.max_retries
        )

    def generate_text(self,
                     prompt: str,
                     model: Optional[str] = None,
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None,
                     **kwargs) -> str:
        """
        Generate text using OpenAI API

        Args:
            prompt: User prompt
            model: Model to use (defaults to config model)
            system_prompt: System prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            str: Generated text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=model or self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

    def generate_text_stream(self,
                            prompt: str,
                            model: Optional[str] = None,
                            system_prompt: Optional[str] = None,
                            temperature: float = 0.7,
                            max_tokens: Optional[int] = None,
                            **kwargs) -> Generator[str, None, None]:
        """
        Generate text using OpenAI API with streaming

        Args:
            prompt: User prompt
            model: Model to use
            system_prompt: System prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            str: Text chunks as they are generated
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.completions.create(
                model=model or self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"OpenAI API streaming error: {e}")

    def generate_code(self,
                     description: str,
                     language: str = "html",
                     system_prompt: Optional[str] = None,
                     **kwargs) -> str:
        """
        Generate code using OpenAI API

        Args:
            description: Description of what to generate
            language: Programming language
            system_prompt: Custom system prompt
            **kwargs: Additional parameters

        Returns:
            str: Generated code
        """
        if not system_prompt:
            system_prompt = f"""You are an expert {language} developer. Generate clean, well-structured {language} code based on the user's requirements.
            Return only the code without explanations or markdown formatting unless specifically requested."""

        prompt = f"Generate {language} code for: {description}"

        return self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )


class AsyncOpenAIConnector:
    """
    Handles asynchronous connections to OpenAI API
    """

    def __init__(self, config: Optional[OpenAIConfig] = None):
        """
        Initialize the async OpenAI connector

        Args:
            config: OpenAI configuration object
        """
        self.config = config or OpenAIConfig()

        # Get API key from config or environment
        api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass in config.")

        # Get base URL from config or environment
        base_url = self.config.base_url or os.environ.get("OPENAI_BASE_URL")

        # Initialize AsyncOpenAI client
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=httpx.Timeout(self.config.timeout),
            max_retries=self.config.max_retries
        )

    async def generate_text(self,
                           prompt: str,
                           model: Optional[str] = None,
                           system_prompt: Optional[str] = None,
                           temperature: float = 0.7,
                           max_tokens: Optional[int] = None,
                           **kwargs) -> str:
        """
        Generate text using OpenAI API asynchronously

        Args:
            prompt: User prompt
            model: Model to use (defaults to config model)
            system_prompt: System prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            str: Generated text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=model or self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

    async def generate_text_stream(self,
                                  prompt: str,
                                  model: Optional[str] = None,
                                  system_prompt: Optional[str] = None,
                                  temperature: float = 0.7,
                                  max_tokens: Optional[int] = None,
                                  **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate text using OpenAI API with async streaming

        Args:
            prompt: User prompt
            model: Model to use
            system_prompt: System prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            str: Text chunks as they are generated
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self.client.chat.completions.create(
                model=model or self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"OpenAI API streaming error: {e}")

    async def generate_code(self,
                           description: str,
                           language: str = "html",
                           system_prompt: Optional[str] = None,
                           **kwargs) -> str:
        """
        Generate code using OpenAI API asynchronously

        Args:
            description: Description of what to generate
            language: Programming language
            system_prompt: Custom system prompt
            **kwargs: Additional parameters

        Returns:
            str: Generated code
        """
        if not system_prompt:
            system_prompt = f"""You are an expert {language} developer. Generate clean, well-structured {language} code based on the user's requirements.
            Return only the code without explanations or markdown formatting unless specifically requested."""

        prompt = f"Generate {language} code for: {description}"

        return await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )

    async def close(self):
        """Close the async client connection"""
        await self.client.close()