# PYDANTIC MODEL FILE

from pydantic import BaseModel
from typing import List

# OUTPUT STRUCTURE
class Blog(BaseModel):

    # Blog title
    blog_title: str

    # Outline sections
    outline_sections: List[str]

    # Target audience
    target_audience: str

    # Writing goal
    writing_goal: str