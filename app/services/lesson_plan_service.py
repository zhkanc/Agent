import time
import logging
import json
from pathlib import Path
from uuid import uuid4
from typing import AsyncGenerator, Optional
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

        request_id = str(uuid4())

        # Load context file if provided
        context_content = ""
        if req.context_file:
            # Security check: prevent directory traversal
            safe_filename = Path(req.context_file).name
            
            # Use absolute path resolution
            BASE_DIR = Path(__file__).resolve().parent.parent.parent # E:\TraePrograms\Agent
            context_path = BASE_DIR / "app" / "data" / "context" / safe_filename

            if context_path.exists() and context_path.is_file():
                try:
                    content = context_path.read_text(encoding="utf-8")
                    context_content = f"\n\n## Context (Reference Standard)\n{content}"
                except Exception as e:
                    logger.error(
                        f"Failed to read context file {context_path}: {e}")
            else:
                logger.warning(f"Context file not found: {context_path}")

        prompt = load_prompt(
            "lesson_plan/outline.yaml",
            subject=req.subject,
            grade=req.grade_level,
            topic=req.topic,
            duration=req.duration,
            style=req.teaching_style,
            context=context_content,
        )

        start_time = time.time()

        separator = "---METADATA---"
        buffer = ""
        metadata_mode = False
        metadata_buffer = ""
        usage_log: Optional[LessonPlanLog] = None

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
                    request_id=request_id,
                    model_name=chunk.get("model", settings.model_name),
                    input_tokens=chunk["input_tokens"],
                    output_tokens=chunk["output_tokens"],
                    total_tokens=chunk["total_tokens"],
                    latency_ms=latency
                )
                logger.info(f"Request Log: {log_entry.json()}")
                usage_log = log_entry

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
                logger.error(
                    f"Failed to parse metadata: {e}. Raw buffer: {metadata_buffer}")
                # We return empty metadata on failure rather than crashing the stream end
        
        # Inject context file usage info into metadata
        if req.context_file and context_content:
             metadata.context_file_used = req.context_file

        yield LessonPlanEndEvent(metadata=metadata, usage=usage_log)
