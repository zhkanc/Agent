from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.lesson_plan import LessonPlanRequest
from app.services.lesson_plan_service import LessonPlanService
from app.utils.sse import sse_event_generator

router = APIRouter(prefix="/lesson-plan", tags=["Lesson Plan"])


@router.post("/generate")
async def generate_lesson_plan(req: LessonPlanRequest):
    events = LessonPlanService.generate(req)

    return StreamingResponse(
        sse_event_generator(events),
        media_type="text/event-stream",
    )
