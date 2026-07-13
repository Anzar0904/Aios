import json
import os
from typing import Any, Iterator, List, Optional

import httpx

from aios.providers.interface import AIProvider
from aios.providers.models import ProviderCapabilities


class MockProvider(AIProvider):
    @property
    def name(self) -> str:
        return "mock"

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        res = f"[MockProvider] Response to prompt: '{prompt}'"
        if system_prompt:
            res = f"System: {system_prompt}\n{res}"
        return res

    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        yield self.generate(model, prompt, system_prompt, **kwargs)

    def embeddings(self, model: str, text: str, **kwargs: Any) -> List[float]:
        return [0.0] * 1536

    def health(self) -> bool:
        return True

    def capabilities(self) -> ProviderCapabilities:
        from aios.providers.models import ProviderCapabilities

        return ProviderCapabilities(chat=True)


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "openai"

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        if not self._api_key:
            return f"[OpenAIProvider] Mock response to prompt: '{prompt}'"

        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": model or "gpt-4o", "messages": messages}
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]

        with httpx.Client(timeout=float(self._timeout)) as client:
            res = client.post(endpoint, json=payload, headers=headers)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]

    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        yield self.generate(model, prompt, system_prompt, **kwargs)

    def embeddings(self, model: str, text: str, **kwargs: Any) -> List[float]:
        return [0.0] * 1536

    def health(self) -> bool:
        return True

    def capabilities(self) -> ProviderCapabilities:
        from aios.providers.models import ProviderCapabilities

        return ProviderCapabilities(chat=True, embeddings=True)


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "claude"

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        if not self._api_key:
            return f"[ClaudeProvider] Mock response to prompt: '{prompt}'"

        endpoint = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": model or "claude-3-5-sonnet",
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        if system_prompt:
            payload["system"] = system_prompt
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]

        with httpx.Client(timeout=float(self._timeout)) as client:
            res = client.post(endpoint, json=payload, headers=headers)
            res.raise_for_status()
            return res.json()["content"][0]["text"]

    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        yield self.generate(model, prompt, system_prompt, **kwargs)

    def embeddings(self, model: str, text: str, **kwargs: Any) -> List[float]:
        return []

    def health(self) -> bool:
        return True

    def capabilities(self) -> ProviderCapabilities:
        from aios.providers.models import ProviderCapabilities

        return ProviderCapabilities(chat=True)


class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "gemini"

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        return "[GeminiProvider] response"

    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        yield self.generate(model, prompt, system_prompt, **kwargs)

    def embeddings(self, model: str, text: str, **kwargs: Any) -> List[float]:
        return []

    def health(self) -> bool:
        return True

    def capabilities(self) -> ProviderCapabilities:
        from aios.providers.models import ProviderCapabilities

        return ProviderCapabilities(chat=True)


class OllamaProvider(AIProvider):
    """Local Ollama instance provider adapter."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30) -> None:
        self.base_url = base_url
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "ollama"

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        endpoint = f"{self.base_url.rstrip('/')}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
        }
        with httpx.Client(timeout=float(self.timeout)) as client:
            res = client.post(endpoint, json=payload, headers=headers)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]

    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        endpoint = f"{self.base_url.rstrip('/')}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "stream": True,
        }
        with httpx.Client(timeout=float(self.timeout)) as client:
            with client.stream("POST", endpoint, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            text = chunk_data["choices"][0]["delta"].get("content", "")
                            if text:
                                yield text
                        except Exception:
                            pass

    def embeddings(self, model: str, text: str, **kwargs: Any) -> List[float]:
        endpoint = f"{self.base_url.rstrip('/')}/api/embeddings"
        payload = {"model": model, "prompt": text}
        with httpx.Client(timeout=float(self.timeout)) as client:
            res = client.post(endpoint, json=payload)
            res.raise_for_status()
            return res.json()["embedding"]

    def health(self) -> bool:
        try:
            endpoint = f"{self.base_url.rstrip('/')}/api/tags"
            with httpx.Client(timeout=2.0) as client:
                res = client.get(endpoint)
                return res.status_code == 200
        except Exception:
            return False

    def capabilities(self) -> ProviderCapabilities:
        from aios.providers.models import ProviderCapabilities

        return ProviderCapabilities(chat=True, embeddings=True, streaming=True)
