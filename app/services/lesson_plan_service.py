from typing import AsyncGenerator
from app.schemas.lesson_plan import (
    LessonPlanRequest,
    LessonPlanContentEvent,
    LessonPlanEndEvent,
    LessonPlanMetadata,
)
from app.services.llm_service import LLMService
from app.utils.prompt_loader import load_prompt


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

        async for chunk in LLMService.stream_generate(prompt):
            yield LessonPlanContentEvent(text=chunk)

        yield LessonPlanEndEvent(
            metadata=LessonPlanMetadata(
                key_concepts=["Supply", "Demand", "Equilibrium"]
            )
        )
