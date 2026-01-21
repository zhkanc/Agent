from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class LessonPlanRequest(BaseModel):
    subject: str = Field(
        ...,
        description="学科名称，如：IGCSE Economics"
    )

    grade_level: str = Field(
        ...,
        description="年级，如：Grade 10"
    )

    topic: str = Field(
        ...,
        description="课程主题，如：supply and demand"
    )

    duration: int = Field(
        ...,
        gt=0,
        description="持续时长（单位：分钟），如：45"
    )

    teaching_style: str = Field(
        ...,
        description="教学风格，如：PBL项目制"
    )

    context_file: Optional[str] = Field(
        None,
        description="上下文背景文件名（需位于 app/data/context 目录下），如：standard.md"
    )


class SSEEventBase(BaseModel):
    event: Literal["content", "error", "end"]


class LessonPlanContentEvent(SSEEventBase):
    event: Literal["content"] = "content"
    text: str


class LessonPlanErrorEvent(SSEEventBase):
    event: Literal["error"] = "error"
    message: str
    error_code: Optional[str] = None


class LessonPlanMetadata(BaseModel):
    key_concepts: List[str]
    difficulty_level: Optional[str] = None
    estimated_prep_time: Optional[str] = None

    class Config:
        extra = "ignore"


class LessonPlanLog(BaseModel):
    request_id: str
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float


class LessonPlanEndEvent(SSEEventBase):
    event: Literal["end"] = "end"
    metadata: LessonPlanMetadata
    usage: Optional[LessonPlanLog] = None
