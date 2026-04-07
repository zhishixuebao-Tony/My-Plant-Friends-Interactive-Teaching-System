from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    student_id: str
    student_name: str
    is_logged_in: bool = False
    current_stage: str = "0_login"

    pre_photo_url: Optional[str] = None

    sensory_evaluations: List[str] = Field(default_factory=list)
    dimension_evaluations: List[str] = Field(default_factory=list)
    record_card_img: Optional[str] = None

    draft_img: Optional[str] = None
    ai_feedback_text: Optional[str] = None
    has_completed_ai: bool = False

    has_viewed_resources: bool = False

    final_img: Optional[str] = None
    last_active_time: Optional[datetime] = None
