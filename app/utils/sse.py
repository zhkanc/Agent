import json
from typing import AsyncContextManager, AsyncGenerator
from pydantic import BaseModel


async def sse_event_generator(
    events: AsyncGenerator[BaseModel, None]
):
    async for event in events:
        yield f"data: {event.json()}\n\n"
