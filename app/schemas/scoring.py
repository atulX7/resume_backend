from pydantic import BaseModel
from typing import Dict


class ResumeScoringResponse(BaseModel):
    scores: Dict[str, float]
