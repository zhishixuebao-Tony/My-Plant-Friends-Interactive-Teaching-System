from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    student_id: str
    student_name: str
    is_logged_in: bool = False
    current_stage: str = "0"

    pre_record_card: Optional[str] = None
    pre_plant_1: Optional[str] = None
    pre_plant_2: Optional[str] = None
    pre_plant_3: Optional[str] = None

    sensory_evaluations: List[str] = Field(default_factory=list)
    dimension_evaluations: List[str] = Field(default_factory=list)
    resource_click_stats: dict = Field(default_factory=dict)
    stage5_checks: List[str] = Field(default_factory=list)

    stage1_stars: int = 0
    stage3_stars: int = 0
    stage5_stars: int = 0
    total_stars: int = 0

    has_viewed_resources: bool = False
    has_claimed_certificate: bool = False

    last_active_time: Optional[datetime] = None
