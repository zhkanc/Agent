import asyncio
from typing import AsyncGenerator


class LLMService:
    @staticmethod
    async def stream_generate(prompt: str) -> AsyncGenerator[str, None]:
        # Todo: 接入千问模型 streaming SDK
        for chunk in ["教学目标...\n", "教学流程...\n", "教学互动...\n"]:
            await asyncio.sleep(0.5)
            yield chunk
