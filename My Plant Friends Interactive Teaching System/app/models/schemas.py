from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StudentProfile(BaseModel):
    student_id: str
    student_name: str
    is_logged_in: bool = False
    current_stage: str = "0_login" 
    
    # 预置照片
    pre_photo_url: Optional[str] = None
    
    # 环节1
    sensory_evaluations: List[str] = [] # e.g. ["看了看", "摸了摸"]
    # 环节2
    dimension_evaluations: List[str] = [] # e.g. ["记录特点"]
    record_card_img: Optional[str] = None
    # 环节3
    draft_img: Optional[str] = None
    ai_feedback_text: Optional[str] = None
    has_completed_ai: bool = False
    # 环节4
    has_viewed_resources: bool = False
    # 环节5
    final_img: Optional[str] = None

    is_logged_in: bool = False