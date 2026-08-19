from __future__ import annotations

from typing import TypedDict, Annotated
from operator import add

class StudentState(TypedDict):
    student_id: str    
    grade: str
    log: Annotated[list[str], add]