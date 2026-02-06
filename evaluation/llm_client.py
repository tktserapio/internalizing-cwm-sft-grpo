"""
LLM Client for benchmark evaluation.

Provides a unified interface for calling various LLM APIs:
- OpenAI (GPT-4o, GPT-4, etc.)
- Local vLLM endpoints
- Anthropic (Claude)
- OpenRouter (access to many models including Kimi, DeepSeek, etc.)
"""

import os
import time
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMResponse:
    """Structured response from an LLM call."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    latency_ms: float
    raw_response: Optional[Dict[str, Any]] = None


class LLMClient:
    """
    Unified client for LLM API calls.

    Supports OpenAI, vLLM, and Anthropic APIs with consistent interface.
    """

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ):
        """
        Initialize the LLM client.

        Args:
            provider: "openai", "vllm", "anthropic", or "openrouter"
            model: Model identifier
            api_key: API key (defaults to env var)
            base_url: Custom API endpoint (for vLLM)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        if self.provider in ["openai", "vllm", "openrouter"]:
            self._init_openai_client(api_key, base_url)
        elif self.provider == "anthropic":
            self._init_anthropic_client(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _init_openai_client(self, api_key: Optional[str], base_url: Optional[str]):
        """Initialize OpenAI-compatible client."""
        import openai

        if self.provider == "openrouter":
            if api_key is None:
                api_key = os.getenv("OPENROUTER_API_KEY")
            if base_url is None:
                base_url = "https://openrouter.ai/api/v1"
        elif self.provider == "vllm":
            if api_key is None:
                api_key = os.getenv("OPENAI_API_KEY")
            if base_url is None:
                base_url = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
        else:
            if api_key is None:
                api_key = os.getenv("OPENAI_API_KEY")

        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def _init_anthropic_client(self, api_key: Optional[str]):
        """Initialize Anthropic client."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            LLMResponse with generated content and metadata
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        start_time = time.time()

        if self.provider in ["openai", "vllm", "openrouter"]:
            response = self._generate_openai(prompt, system_prompt, temp, tokens)
        else:
            response = self._generate_anthropic(prompt, system_prompt, temp, tokens)

        latency_ms = (time.time() - start_time) * 1000
        response.latency_ms = latency_ms

        return response

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using OpenAI API."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                # max_tokens=max_tokens, # uncomment if u want to set max tokens
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                finish_reason=response.choices[0].finish_reason,
                latency_ms=0,  # Set by caller
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using Anthropic API."""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
                latency_ms=0,
                raw_response=None
            )

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[LLMResponse]:
        """
        Generate responses for multiple prompts.

        Args:
            prompts: List of prompts
            system_prompt: Shared system prompt
            **kwargs: Additional arguments passed to generate()

        Returns:
            List of LLMResponse objects
        """
        responses = []
        for prompt in prompts:
            response = self.generate(prompt, system_prompt, **kwargs)
            responses.append(response)
        return responses


# Convenience functions for quick usage
def get_gpt4o_client(**kwargs) -> LLMClient:
    """Get a pre-configured GPT-4o client."""
    return LLMClient(provider="openai", model="gpt-4o", **kwargs)


def get_gpt4_client(**kwargs) -> LLMClient:
    """Get a pre-configured GPT-4 client."""
    return LLMClient(provider="openai", model="gpt-4-turbo", **kwargs)


def get_vllm_client(model: str, base_url: str = None, **kwargs) -> LLMClient:
    """Get a client for local vLLM endpoint."""
    return LLMClient(provider="vllm", model=model, base_url=base_url, **kwargs)


def get_openrouter_client(model: str, **kwargs) -> LLMClient:
    """Get a client for OpenRouter API."""
    return LLMClient(provider="openrouter", model=model, **kwargs)


def get_kimi_client(**kwargs) -> LLMClient:
    """Get a pre-configured Kimi K2 client via OpenRouter."""
    return LLMClient(provider="openrouter", model="moonshotai/kimi-k2", **kwargs)


if __name__ == "__main__":
    # Quick test
    print("Testing LLM Client...")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    try:
        client = get_gpt4o_client(api_key=OPENAI_API_KEY)
        response = client.generate(
            prompt="Say 'Hello, World!' and nothing else.", 
            temperature=0.3
        )
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")
        print(f"Latency: {response.latency_ms:.2f}ms")
    except Exception as e:
        print(f"Test failed (expected if no API key): {e}")
