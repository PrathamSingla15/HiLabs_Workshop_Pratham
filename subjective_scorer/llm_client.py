"""Async OpenRouter API client with retry and connection pooling."""
import httpx
import asyncio
import logging
from config import (
    OPENROUTER_BASE_URL, OPENROUTER_MODEL, OPENROUTER_API_KEY,
    LLM_TEMPERATURE, LLM_SEED, LLM_MAX_TOKENS, LLM_TOP_LOGPROBS,
    LLM_RETRY_ATTEMPTS, LLM_RETRY_BACKOFF, MAX_CONCURRENT_LLM_CALLS,
)

logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(self):
        self.base_url = OPENROUTER_BASE_URL
        self.model = OPENROUTER_MODEL
        self.api_key = OPENROUTER_API_KEY
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)
        self._client = None

    async def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    async def call(self, messages: list, seed: int = LLM_SEED) -> dict | None:
        """Make a single API call with logprobs."""
        client = await self._get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hilabs-workshop",
            "X-Title": "Clinical NLP Evaluation",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": LLM_TEMPERATURE,
            "seed": seed,
            "max_tokens": LLM_MAX_TOKENS,
            "logprobs": True,
            "top_logprobs": LLM_TOP_LOGPROBS,
        }

        response = await client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    async def call_with_retry(self, messages: list, seed: int = LLM_SEED) -> dict | None:
        """Call with exponential backoff retry on failures."""
        for attempt in range(LLM_RETRY_ATTEMPTS):
            try:
                async with self.semaphore:
                    return await self.call(messages, seed)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = LLM_RETRY_BACKOFF * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {wait}s (attempt {attempt+1})")
                    await asyncio.sleep(wait)
                elif e.response.status_code >= 500:
                    wait = LLM_RETRY_BACKOFF * (2 ** attempt)
                    logger.warning(f"Server error {e.response.status_code}, retrying in {wait}s")
                    await asyncio.sleep(wait)
                else:
                    logger.error(f"HTTP error: {e.response.status_code}")
                    return None
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt == LLM_RETRY_ATTEMPTS - 1:
                    logger.error(f"Connection failed after {LLM_RETRY_ATTEMPTS} attempts: {e}")
                    return None
                wait = LLM_RETRY_BACKOFF * (2 ** attempt)
                await asyncio.sleep(wait)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        return None

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
