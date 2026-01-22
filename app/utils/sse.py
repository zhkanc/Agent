import json
from typing import AsyncContextManager, AsyncGenerator, Any
from pydantic import BaseModel


async def sse_event_generator(
    events: AsyncGenerator[Any, None]
):
    """
    生成SSE事件流，将异步事件转换为SSE格式。
    """
    async for event in events:
        if isinstance(event, BaseModel):
            yield f"data: {event.model_dump_json()}\n\n"
