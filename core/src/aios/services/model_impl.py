import json
import logging
import os
import time
from typing import Any, Dict, Iterator, Optional, Tuple

import httpx


from aios.config import load_config
from aios.services.model import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelRegistry,
    ModelService,
    ProviderFactory,
)

logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Structured error returned from LLM providers."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class MockProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[MockProvider] Response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"Instruction: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "mock-model",
            provider_name=self.name,
            usage={"prompt_tokens": 10, "completion_tokens": 20},
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "openai"

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self._api_key:
            content = f"[OpenAIProvider] Mock response to prompt: '{request.prompt}'"
            if request.system_instruction:
                content = f"System: {request.system_instruction}\n{content}"
            return LLMResponse(
                content=content,
                model_name=request.model_name or "gpt-4o",
                provider_name=self.name,
                usage={"prompt_tokens": 12, "completion_tokens": 25},
                finish_reason="stop",
                metadata={},
            )

        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": request.model_name or "gpt-4o",
            "messages": messages,
            "temperature": request.temperature,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        try:
            with httpx.Client(timeout=float(self._timeout)) as client:
                res = client.post(endpoint, json=payload, headers=headers)

            if res.status_code == 429:
                raise LLMProviderError("Rate limit exceeded", status_code=429)
            if res.status_code == 401:
                raise LLMProviderError("Authentication failure", status_code=401)
            if res.status_code != 200:
                raise LLMProviderError(f"OpenAI error: {res.text}", status_code=res.status_code)

            data = res.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})
            return LLMResponse(
                content=choice["message"]["content"],
                model_name=data.get("model", request.model_name or "gpt-4o"),
                provider_name=self.name,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                finish_reason=choice.get("finish_reason", "stop"),
                metadata=data
            )
        except httpx.RequestError as e:
            raise LLMProviderError(f"Connection error: {e}", status_code=503)

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self._api_key = api_key or os.environ.get("CLAUDE_CODE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "claude"

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self._api_key:
            content = f"[ClaudeProvider] Mock response to prompt: '{request.prompt}'"
            if request.system_instruction:
                content = f"System: {request.system_instruction}\n{content}"
            return LLMResponse(
                content=content,
                model_name=request.model_name or "claude-3-5-sonnet",
                provider_name=self.name,
                usage={"prompt_tokens": 15, "completion_tokens": 30},
                finish_reason="stop",
                metadata={},
            )

        endpoint = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        messages = [{"role": "user", "content": request.prompt}]

        payload = {
            "model": request.model_name or "claude-3-5-sonnet",
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
        }
        if request.system_instruction:
            payload["system"] = request.system_instruction

        try:
            with httpx.Client(timeout=float(self._timeout)) as client:
                res = client.post(endpoint, json=payload, headers=headers)

            if res.status_code == 429:
                raise LLMProviderError("Rate limit exceeded", status_code=429)
            if res.status_code == 401:
                raise LLMProviderError("Authentication failure", status_code=401)
            if res.status_code != 200:
                raise LLMProviderError(f"Claude error: {res.text}", status_code=res.status_code)

            data = res.json()
            choice = data["content"][0]
            usage = data.get("usage", {})
            return LLMResponse(
                content=choice["text"],
                model_name=data.get("model", request.model_name or "claude-3-5-sonnet"),
                provider_name=self.name,
                usage={
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                },
                finish_reason="stop",
                metadata=data
            )
        except httpx.RequestError as e:
            raise LLMProviderError(f"Connection error: {e}", status_code=503)

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "gemini"

    def generate(self, request: LLMRequest) -> LLMResponse:
        import shutil
        import subprocess
        if not shutil.which("gemini-cli") and self._api_key != "cli_active":
            content = f"[GeminiProvider] Mock response to prompt: '{request.prompt}'"
            if request.system_instruction:
                content = f"System: {request.system_instruction}\n{content}"
            return LLMResponse(
                content=content,
                model_name=request.model_name or "gemini-1.5-pro",
                provider_name=self.name,
                usage={"prompt_tokens": 8, "completion_tokens": 18},
                finish_reason="stop",
                metadata={},
            )

        cmd = ["gemini-cli", "--prompt", request.prompt, "--model", request.model_name or "gemini-1.5-pro"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=self._timeout)
            if res.returncode != 0:
                raise LLMProviderError(f"Gemini CLI failed: {res.stderr}", status_code=500)

            return LLMResponse(
                content=res.stdout.strip(),
                model_name=request.model_name or "gemini-1.5-pro",
                provider_name=self.name,
                usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
                finish_reason="stop",
                metadata={"stdout": res.stdout, "stderr": res.stderr}
            )
        except subprocess.TimeoutExpired as e:
            raise LLMProviderError(f"Gemini CLI timeout: {e}", status_code=408)
        except FileNotFoundError:
            raise LLMProviderError("gemini-cli binary not found in PATH", status_code=503)

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class OllamaProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "ollama"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[OllamaProvider] Mock local response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"System: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "llama3",
            provider_name=self.name,
            usage={"prompt_tokens": 0, "completion_tokens": 0},
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class LMStudioProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "lmstudio"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[LMStudioProvider] Mock local response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"System: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "luna-7b",
            provider_name=self.name,
            usage={"prompt_tokens": 0, "completion_tokens": 0},
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class OpenRouterProvider(LLMProvider):
    """Production-ready OpenRouter LLM Provider implementing unified adapter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

    @property
    def name(self) -> str:
        return "openrouter"

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.validate_request(request):
            raise LLMProviderError("Request validation failed.")

        if not self._api_key:
            raise LLMProviderError(
                "OpenRouter API key is missing. "
                "Please set the OPENROUTER_API_KEY environment variable."
            )

        endpoint = f"{self._base_url}/chat/completions"

        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": request.model_name or "qwen/qwen3-coder",
            "messages": messages,
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Anzar0904/Aios",
            "X-Title": "Personal AI OS",
        }

        last_exception = None
        for attempt in range(self._max_retries):
            try:
                logger.info(f"OpenRouter API call attempt {attempt + 1}/{self._max_retries}")
                with httpx.Client(timeout=float(self._timeout)) as client:
                    response = client.post(endpoint, json=payload, headers=headers)

                if response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"Transient HTTP error {response.status_code} "
                        f"received on attempt {attempt + 1}"
                    )
                    time.sleep(2**attempt)
                    continue

                if response.status_code != 200:
                    raise LLMProviderError(
                        message=f"OpenRouter API returned error status {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                data = response.json()
                choice = data["choices"][0]
                message_content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason")
                usage = data.get("usage", {})

                return LLMResponse(
                    content=message_content,
                    model_name=data.get("model", request.model_name or "qwen/qwen3-coder"),
                    provider_name=self.name,
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    finish_reason=finish_reason,
                    metadata=data,
                )

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                last_exception = e
                time.sleep(2**attempt)

        if last_exception:
            raise LLMProviderError(
                message=(
                    f"Failed to connect to OpenRouter after {self._max_retries} "
                    f"attempts: {last_exception}"
                )
            )
        else:
            raise LLMProviderError("Failed to execute OpenRouter request (retries exhausted).")

    def validate_request(self, request: LLMRequest) -> bool:
        if request.temperature < 0.0 or request.temperature > 2.0:
            return False
        if request.max_tokens is not None and request.max_tokens <= 0:
            return False
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class OmniRouteProvider(LLMProvider):
    """Production-ready OmniRoute LLM Provider implementing unified adapter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:20128/v1",
        routing_policy: str = "FREE_ONLY",
        timeout: int = 30,
        max_retries: int = 3,
        streaming_enabled: bool = True,
        offline_mode: bool = False,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._routing_policy = routing_policy
        self._timeout = timeout
        self._max_retries = max_retries
        self._streaming_enabled = streaming_enabled
        self._offline_mode = offline_mode

    def _safe_header(self, headers, name: str, default: Any) -> Any:
        if not headers or not hasattr(headers, "get"):
            return default
        val = headers.get(name)
        if isinstance(val, (str, int, float, bool)):
            return val
        return default


    @property
    def name(self) -> str:
        return "omniroute"

    def _map_model_name(self, model_name: Optional[str], task_category: Optional[str] = None) -> str:
        if task_category:
            category = task_category
        else:
            category = "chat"
            if model_name:
                model_lower = model_name.lower()
                if (
                    "coding" in model_lower
                    or "code" in model_lower
                    or "claude-3-5-sonnet" in model_lower
                    or "developer" in model_lower
                ):
                    category = "coding"
                elif (
                    "reasoning" in model_lower
                    or "research" in model_lower
                    or "learning" in model_lower
                    or "smart" in model_lower
                    or "gpt-4o" in model_lower
                    or "gemini-1.5-pro" in model_lower
                ):
                    category = "reasoning"
                elif "vision" in model_lower or "multimodal" in model_lower:
                    category = "multimodal"
                elif (
                    "chat" in model_lower
                    or "conversation" in model_lower
                    or "career" in model_lower
                    or "automation" in model_lower
                    or "llama" in model_lower
                    or "mistral" in model_lower
                    or "phi3" in model_lower
                ):
                    category = "chat"
                elif model_lower.startswith("auto"):
                    parts = model_lower.split("/")
                    if len(parts) > 1:
                        subparts = parts[1].split(":")
                        category = subparts[0]
                    else:
                        category = "chat"

        # Map task categories to OmniRoute-compatible categories
        if category in ("conversation", "learning", "career", "automation", "chat"):
            target_cat = "chat"
        elif category in ("research", "reasoning"):
            target_cat = "reasoning"
        else:
            target_cat = category

        if self._routing_policy == "FREE_ONLY":
            return f"auto/{target_cat}:free"
        else:
            return f"auto/{target_cat}"

    def _get_task_category_and_prefs(self, request: LLMRequest) -> Tuple[str, Dict[str, Any]]:
        # Read explicit category/preferences or infer them from model name
        category = request.task_category
        prefs = dict(request.preferences) if request.preferences else {}

        if not category:
            model_name = request.model_name
            if model_name:
                model_lower = model_name.lower()
                if (
                    "coding" in model_lower
                    or "code" in model_lower
                    or "claude-3-5-sonnet" in model_lower
                    or "developer" in model_lower
                ):
                    category = "coding"
                    prefs.setdefault("latency_preference", "low")
                    prefs.setdefault("tool_calling", True)
                elif (
                    "research" in model_lower
                    or "gemini-1.5-pro" in model_lower
                    or "long-context" in model_lower
                ):
                    category = "research"
                    prefs.setdefault("long_context", True)
                elif (
                    "reasoning" in model_lower
                    or "gpt-4o" in model_lower
                    or "smart" in model_lower
                ):
                    category = "reasoning"
                    prefs.setdefault("reasoning_depth", "high")
                elif "automation" in model_lower or "n8n" in model_lower:
                    category = "automation"
                    prefs.setdefault("tool_calling", True)
                elif "learning" in model_lower:
                    category = "learning"
                    prefs.setdefault("reasoning_depth", "medium")
                elif "career" in model_lower:
                    category = "career"
                    prefs.setdefault("JSON_output", True)
                else:
                    category = "conversation"
                    prefs.setdefault("latency_preference", "low")
            else:
                category = "conversation"

        return category, prefs

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.validate_request(request):
            raise LLMProviderError("Request validation failed.")

        category, prefs = self._get_task_category_and_prefs(request)
        enriched_text = ""
        try:
            from aios.registry import ServiceRegistry
            from aios.services.context import ContextService
            registry = ServiceRegistry._global_registry
            if registry:
                ctx_svc = registry.get(ContextService)
                if ctx_svc:
                    context_data = ctx_svc.build_enriched_context(request.prompt, token_budget=1000)
                    enriched_text = context_data.get("assembled_text", "")
        except Exception as e:
            logger.warning(f"OmniRouteProvider: Context enrichment failed: {e}")

        if enriched_text:
            prefs["semantic_context"] = enriched_text[:1000]
            request.prompt = f"Enriched Context:\n{enriched_text}\n\nTask Prompt:\n{request.prompt}"

        endpoint = f"{self._base_url}/chat/completions"

        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        model_to_use = self._map_model_name(request.model_name, category)

        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": request.temperature,
            "metadata": {
                "task_category": category,
                "preferences": prefs,
            },
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Content-Type": "application/json",
            "X-OmniRoute-Task-Category": category,
            "X-OmniRoute-Preferences": json.dumps(prefs),
        }
        # Add per-preference headers for redundancy
        for k, v in prefs.items():
            headers[f"X-OmniRoute-Preference-{k.replace('_', '-').title()}"] = str(v)


        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        last_exception = None
        for attempt in range(self._max_retries):
            if self._offline_mode:
                raise LLMProviderError("Offline mode enabled. OmniRoute requests are blocked.")

            start_time = time.time()
            try:
                logger.info(f"OmniRoute API call attempt {attempt + 1}/{self._max_retries}")
                with httpx.Client(timeout=float(self._timeout)) as client:
                    response = client.post(endpoint, json=payload, headers=headers)

                if response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"Transient HTTP error {response.status_code} "
                        f"received on attempt {attempt + 1}"
                    )
                    time.sleep(2**attempt)
                    continue

                if response.status_code != 200:
                    raise LLMProviderError(
                        message=f"OmniRoute API returned error status {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                latency = time.time() - start_time
                data = response.json()
                choice = data["choices"][0]
                message_content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason")
                usage = data.get("usage", {})

                # Parse OmniRoute Response Telemetry safely
                selected_prov = self._safe_header(response.headers, "X-OmniRoute-Provider", "omniroute_upstream")
                selected_mod = self._safe_header(response.headers, "X-OmniRoute-Model", data.get("model", model_to_use))
                fallback_used = self._safe_header(response.headers, "X-OmniRoute-Fallback", "No")
                fallback_reason = self._safe_header(response.headers, "X-OmniRoute-Fallback-Reason", "N/A")
                resp_latency = self._safe_header(response.headers, "X-OmniRoute-Latency", latency)

                diag = {
                    "task_category": category,
                    "routing_policy": self._routing_policy,
                    "selected_provider": selected_prov,
                    "selected_model": selected_mod,
                    "fallback_used": fallback_used,
                    "fallback_reason": fallback_reason,
                    "latency": float(resp_latency),
                    "streaming_enabled": False,
                    "retry_count": attempt,
                }
                logger.info(f"OmniRoute Response Diagnostics: {json.dumps(diag)}")

                # Embed diagnostics into response metadata
                meta_res = dict(data)
                meta_res["diagnostics"] = diag

                return LLMResponse(
                    content=message_content,
                    model_name=data.get("model", model_to_use),
                    provider_name=self.name,
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    finish_reason=finish_reason,
                    metadata=meta_res,
                )

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                last_exception = e
                time.sleep(2**attempt)

        if last_exception:
            raise LLMProviderError(
                message=(
                    f"Failed to connect to OmniRoute after {self._max_retries} "
                    f"attempts: {last_exception}"
                )
            )
        else:
            raise LLMProviderError("Failed to execute OmniRoute request (retries exhausted).")

    def validate_request(self, request: LLMRequest) -> bool:
        if request.temperature < 0.0 or request.temperature > 2.0:
            return False
        if request.max_tokens is not None and request.max_tokens <= 0:
            return False
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        if not self._streaming_enabled:
            yield self.generate(request)
            return

        if not self.validate_request(request):
            raise LLMProviderError("Request validation failed.")

        endpoint = f"{self._base_url}/chat/completions"

        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        category, prefs = self._get_task_category_and_prefs(request)
        model_to_use = self._map_model_name(request.model_name, category)

        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
            "metadata": {
                "task_category": category,
                "preferences": prefs,
            },
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Content-Type": "application/json",
            "X-OmniRoute-Task-Category": category,
            "X-OmniRoute-Preferences": json.dumps(prefs),
        }
        for k, v in prefs.items():
            headers[f"X-OmniRoute-Preference-{k.replace('_', '-').title()}"] = str(v)


        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        last_exception = None
        for attempt in range(self._max_retries):
            if self._offline_mode:
                raise LLMProviderError("Offline mode enabled. OmniRoute stream is blocked.")

            start_time = time.time()
            try:
                with httpx.Client(timeout=float(self._timeout)) as client:
                    with client.stream("POST", endpoint, json=payload, headers=headers) as r:
                        if r.status_code in (429, 500, 502, 503, 504):
                            logger.warning(
                                f"Transient HTTP error {r.status_code} in stream attempt {attempt + 1}"
                            )
                            time.sleep(2**attempt)
                            continue

                        if r.status_code != 200:
                            raise LLMProviderError(
                                message=f"OmniRoute API returned error status {r.status_code} in stream",
                                status_code=r.status_code,
                                response_body=r.read().decode("utf-8", errors="ignore"),
                            )

                        latency = time.time() - start_time
                        selected_prov = self._safe_header(r.headers, "X-OmniRoute-Provider", "omniroute_upstream")
                        selected_mod = self._safe_header(r.headers, "X-OmniRoute-Model", model_to_use)
                        fallback_used = self._safe_header(r.headers, "X-OmniRoute-Fallback", "No")
                        fallback_reason = self._safe_header(r.headers, "X-OmniRoute-Fallback-Reason", "N/A")
                        resp_latency = self._safe_header(r.headers, "X-OmniRoute-Latency", latency)

                        diag = {
                            "task_category": category,
                            "routing_policy": self._routing_policy,
                            "selected_provider": selected_prov,
                            "selected_model": selected_mod,
                            "fallback_used": fallback_used,
                            "fallback_reason": fallback_reason,
                            "latency": float(resp_latency),
                            "streaming_enabled": True,
                            "retry_count": attempt,
                        }
                        logger.info(f"OmniRoute Stream Diagnostics: {json.dumps(diag)}")

                        for line in r.iter_lines():
                            if not line:
                                continue
                            if isinstance(line, bytes):
                                line = line.decode("utf-8", errors="ignore")
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data_str)
                                    choice = chunk["choices"][0]
                                    delta = choice.get("delta", {})
                                    content = delta.get("content", "")
                                    finish_reason = choice.get("finish_reason")
                                    if content or finish_reason:
                                        chunk["diagnostics"] = diag
                                        yield LLMResponse(
                                            content=content,
                                            model_name=chunk.get("model", model_to_use),
                                            provider_name=self.name,
                                            usage={},
                                            finish_reason=finish_reason,
                                            metadata=chunk,
                                        )
                                except Exception as e:
                                    logger.warning(f"Error parsing stream chunk: {e}")
                        return
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                logger.warning(f"Network error on stream attempt {attempt + 1}: {e}")
                last_exception = e
                time.sleep(2**attempt)

        if last_exception:
            logger.error(f"Stream error, falling back to generate: {last_exception}")
        yield self.generate(request)

    def check_health(self) -> bool:
        base_url_parent = self._base_url
        if base_url_parent.endswith("/v1"):
            base_url_parent = base_url_parent[:-3]
        elif base_url_parent.endswith("/v1/"):
            base_url_parent = base_url_parent[:-4]

        endpoint = f"{base_url_parent}/api/health/ping"
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        try:
            with httpx.Client(timeout=float(self._timeout)) as client:
                res = client.get(endpoint, headers=headers)
                if res.status_code == 200:
                    return True
        except Exception:
            pass

        try:
            with httpx.Client(timeout=float(self._timeout)) as client:
                res = client.get(f"{self._base_url}/models", headers=headers)
                if res.status_code == 200:
                    return True
        except Exception:
            pass

        return False



class LocalModelService(ModelService):
    """Concrete implementation of ModelService coordinating model routing

    across multiple registered providers via registries and factories.
    """

    def __init__(self, default_model: str = None, config_path: str = "config/config.toml", registry: Optional[Any] = None) -> None:
        self.registry = ModelRegistry()
        self.factory = ProviderFactory()
        self._default_model = default_model
        self._config_path = config_path

        from aios.providers import (
            ProviderConfig,
            ProviderHealthMonitor,
            ProviderMetricsCollector,
            ProviderRegistry,
            ProviderRouter,
        )

        self.provider_config = ProviderConfig()
        self.provider_registry = ProviderRegistry(registry)
        self.provider_health = ProviderHealthMonitor(registry)
        self.provider_metrics = ProviderMetricsCollector()
        self.provider_router = ProviderRouter(
            self.provider_config,
            self.provider_registry,
            self.provider_health,
            self.provider_metrics,
            self.factory,
            di_registry=registry,
        )

    def initialize(self) -> None:
        logger.info("Initializing LocalModelService")
        from pathlib import Path

        config = load_config(Path(self._config_path))

        if not self._default_model:
            self._default_model = config.llm.default_model or "mock-model"

        self.factory.register_provider(MockProvider())
        self.factory.register_provider(OpenAIProvider())
        self.factory.register_provider(ClaudeProvider())
        self.factory.register_provider(GeminiProvider())
        self.factory.register_provider(OllamaProvider())
        self.factory.register_provider(LMStudioProvider())

        api_key = os.environ.get("OPENROUTER_API_KEY")
        self.factory.register_provider(
            OpenRouterProvider(
                api_key=api_key,
                base_url=config.llm.openrouter.base_url,
                timeout=config.llm.openrouter.timeout,
            )
        )

        omniroute_cfg = getattr(config.llm, "omniroute", None)
        if omniroute_cfg:
            self.factory.register_provider(
                OmniRouteProvider(
                    api_key=omniroute_cfg.api_key,
                    base_url=omniroute_cfg.base_url,
                    routing_policy=omniroute_cfg.routing_policy,
                    timeout=omniroute_cfg.timeout,
                    max_retries=omniroute_cfg.retry_count,
                    streaming_enabled=omniroute_cfg.streaming_enabled,
                    offline_mode=omniroute_cfg.offline_mode,
                )
            )
        else:
            self.factory.register_provider(OmniRouteProvider())

        # Configure provider properties loaded from file config
        self.provider_config.preferred_provider = config.llm.provider
        self.provider_config.offline_mode = omniroute_cfg.offline_mode if omniroute_cfg else False
        self.provider_config.omniroute_base_url = omniroute_cfg.base_url if omniroute_cfg else "http://localhost:20128/v1"
        self.provider_config.omniroute_api_key = omniroute_cfg.api_key if omniroute_cfg else None
        self.provider_config.omniroute_routing_policy = omniroute_cfg.routing_policy if omniroute_cfg else "FREE_ONLY"
        self.provider_config.omniroute_timeout = omniroute_cfg.timeout if omniroute_cfg else 30
        self.provider_config.omniroute_retry_count = omniroute_cfg.retry_count if omniroute_cfg else 3
        self.provider_config.omniroute_streaming_enabled = omniroute_cfg.streaming_enabled if omniroute_cfg else True


        # Register default model dynamically
        if self._default_model != "mock-model":
            self.registry.register_model(self._default_model, config.llm.provider)

        # Handle slash-based OpenRouter fallback in ModelRegistry lookup if needed
        # We can dynamically overwrite ModelRegistry.get_provider_for_model in self
        orig_get = self.registry.get_provider_for_model

        def dynamic_get_provider(model_name: str) -> str:
            try:
                return orig_get(model_name)
            except ValueError:
                if "/" in model_name:
                    return "openrouter"
                raise

        self.registry.get_provider_for_model = dynamic_get_provider

    def execute_prompt(self, prompt: str, system_instruction: str | None = None) -> str:
        req = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            model_name=self._default_model,
        )
        res = self.execute_request(req)
        return res.content

    def execute_request(self, request: LLMRequest) -> LLMResponse:
        if not request.model_name:
            request.model_name = self._default_model
        return self.provider_router.route_request(request)

    def execute_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        if not request.model_name:
            request.model_name = self._default_model
        return self.provider_router.route_stream(request)
