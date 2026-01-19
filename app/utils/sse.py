import json
from typing import AsyncContextManager
from pydantic import BaseModel


async def see_event_generator(
    events: AsyncGenerator[BaseModel]
):
    async for event in events:
        yield f"data: {event.json()}\n\n"
