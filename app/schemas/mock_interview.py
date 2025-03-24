from pydantic import BaseModel
from typing import Optional, List, Dict


class QuestionItem(BaseModel):
    """Schema for an individual interview question."""
    question_id: str
    question: str

class MockInterviewQuestionResponse(BaseModel):
    """Response schema for mock interview questions."""
    session_id: str
    questions: List[QuestionItem]

class AnswerEvaluation(BaseModel):
    """Schema for individual question evaluation."""
    question: str
    score: float
    feedback: str
    audio_presigned_url: str
    follow_up_question: str

class MockInterviewProcessingResponse(BaseModel):
    """Final AI-driven evaluation after interview completion."""
    overall_score: float
    duration_in_minutes: float
    key_strengths: List[str]
    areas_for_growth: List[str]
    skill_assessment: Dict[str, float]  # ✅ Scores for Leadership, Communication, etc.
    evaluation_results: List[AnswerEvaluation]  # ✅ Stores evaluations for each Q&A

class ProcessingStartedResponse(BaseModel):
    status: str
    message: str

class MockInterviewSessionDetails(BaseModel):
    """Detailed response for a single mock interview session."""
    session_id: str
    job_title: str
    created_at: str
    status: str
    overall_score: Optional[float] = None
    key_strengths: List[str]
    areas_for_growth: List[str]
    skill_assessment: Dict[str, float]
    evaluation_results: List[AnswerEvaluation]

class MockInterviewSessionSummary(BaseModel):
    """Summary of a mock interview session for listing."""
    session_id: str
    job_title: str
    created_at: str
    status: str  # "in_progress" or "completed"
