import time
import logging
import json
from typing import AsyncGenerator
from app.schemas.lesson_plan import (
    LessonPlanRequest,
    LessonPlanContentEvent,
    LessonPlanEndEvent,
    LessonPlanMetadata,
    LessonPlanErrorEvent,
    LessonPlanLog
)
from app.services.llm_service import LLMService
from app.utils.prompt_loader import load_prompt
from app.core.config import settings

logger = logging.getLogger(__name__)

class LessonPlanService:

    @staticmethod
    async def generate(
        req: LessonPlanRequest
    ) -> AsyncGenerator[object, None]:

        prompt = load_prompt(
            "lesson_plan/outline.yaml",
            subject=req.subject,
            grade=req.grade_level,
            topic=req.topic,
            duration=req.duration,
            style=req.teaching_style,
        )

        start_time = time.time()
        
        separator = "---METADATA---"
        buffer = ""
        metadata_mode = False
        metadata_buffer = ""
        
        async for chunk in LLMService.stream_generate(prompt):
            if chunk["type"] == "content":
                text = chunk["text"]
                
                if metadata_mode:
                    metadata_buffer += text
                    continue
                
                buffer += text
                
                # Check if separator is in buffer
                if separator in buffer:
                    parts = buffer.split(separator, 1)
                    content_part = parts[0]
                    metadata_part = parts[1]
                    
                    if content_part:
                        yield LessonPlanContentEvent(text=content_part)
                    
                    metadata_mode = True
                    metadata_buffer = metadata_part
                    buffer = ""
                else:
                    # Defensive streaming: only yield part of buffer that is safe
                    # (i.e. not potentially part of the separator)
                    # Separator length is 14. 
                    # If buffer ends with partial match of separator, don't yield that part yet.
                    # Simplest heuristic: Keep last N chars where N = len(separator)
                    
                    if len(buffer) > len(separator):
                        safe_len = len(buffer) - len(separator)
                        to_yield = buffer[:safe_len]
                        buffer = buffer[safe_len:]
                        yield LessonPlanContentEvent(text=to_yield)
            
            elif chunk["type"] == "usage":
                latency = (time.time() - start_time) * 1000
                log_entry = LessonPlanLog(
                    request_id=str(req.request_id),
                    model_name=chunk.get("model", settings.model_name),
                    input_tokens=chunk["input_tokens"],
                    output_tokens=chunk["output_tokens"],
                    total_tokens=chunk["total_tokens"],
                    latency_ms=latency
                )
                logger.info(f"Request Log: {log_entry.json()}")
                
            elif chunk["type"] == "error":
                yield LessonPlanErrorEvent(message=chunk["message"])
                return

        # End of stream
        # If we still have content in buffer (and no metadata found), yield it
        if buffer and not metadata_mode:
             yield LessonPlanContentEvent(text=buffer)

        # Parse Metadata
        metadata = LessonPlanMetadata(key_concepts=[])
        if metadata_buffer:
            try:
                # Clean up json string
                json_str = metadata_buffer.strip()
                # Remove markdown code blocks if present
                if json_str.startswith("```"):
                    # Find first newline
                    first_newline = json_str.find("\n")
                    if first_newline != -1:
                        json_str = json_str[first_newline+1:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                
                json_str = json_str.strip()
                data = json.loads(json_str)
                metadata = LessonPlanMetadata(**data)
            except Exception as e:
                logger.error(f"Failed to parse metadata: {e}. Raw buffer: {metadata_buffer}")
                # We return empty metadata on failure rather than crashing the stream end

        yield LessonPlanEndEvent(metadata=metadata)
