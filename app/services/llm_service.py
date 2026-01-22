import time
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from openai import AsyncOpenAI, APIError
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    _client: Optional[AsyncOpenAI] = None
    _semaphore: Optional[asyncio.Semaphore] = None

    @classmethod
    def get_semaphore(cls) -> asyncio.Semaphore:
        if cls._semaphore is None:
            cls._semaphore = asyncio.Semaphore(settings.llm_concurrency_limit)
        return cls._semaphore

    @classmethod
    def get_client(cls) -> AsyncOpenAI:
        if not cls._client:
            api_key = settings.dashscope_api_key
            if not api_key:
                logger.warning(
                    "DASHSCOPE_API_KEY is not set in settings. AsyncOpenAI will attempt to read from environment variables.")

            cls._client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
        return cls._client

    @classmethod
    async def stream_generate(
        cls,
        prompt: str,
        model: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generates streaming response from LLM.
        Yields dicts with keys:
        - type: "content" | "usage" | "error"
        - text: str (if type="content")
        - input_tokens, output_tokens, total_tokens, model: (if type="usage")
        - message: str (if type="error")
        """
        client = cls.get_client()
        model = model or settings.model_name

        semaphore = cls.get_semaphore()

        try:
            async with semaphore:
                logger.info(f"Starting LLM generation with model: {model}")
                stream = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    stream_options={"include_usage": True}
                )

                async for chunk in stream:
                    # Handle usage information (typically in the last chunk)
                    if chunk.usage:
                        yield {
                            "type": "usage",
                            "input_tokens": chunk.usage.prompt_tokens,
                            "output_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                            "model": chunk.model,
                        }

                    # Handle content
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            yield {
                                "type": "content",
                                "text": delta.content
                            }

        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            yield {"type": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected Error in LLMService: {e}")
            yield {"type": "error", "message": f"Internal Error: {str(e)}"}
