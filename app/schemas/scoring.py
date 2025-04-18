from pydantic import BaseModel
from typing import List, Literal


class EvaluationItem(BaseModel):
    criterion: str
    description: str
    score: float
    status: Literal["green", "yellow", "red"]
    assessment: str


class ResumeScoringResponse(BaseModel):
    overall_summary: str
    detailed_evaluation: List[EvaluationItem]
