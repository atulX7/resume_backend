import json

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.scoring import ResumeScoringResponse
from app.utils.prompts import RESUME_SCORING_PROMPT
from app.utils.resume_parser import extract_resume_text
from app.utils.utils import parse_ai_response
from app.utils.openai_client import call_openai

def score_resume(resume_file: UploadFile):
    """Analyzes and scores a resume."""
    if settings.MOCK_DATA:
        ai_response = '''```json
        {
            "layout": 75,
            "ats_readability": 80,
            "impact": 70,
            "keyword_optimization": 65,
            "quantifiable_achievements": 85,
            "action_verbs": 80,
            "readability": 70,
            "personal_branding": 60,
            "customization": 55,
            "grammar_spelling": 95,
            "contact_info": 80,
            "section_completeness": 90,
            "visual_appeal": 75,
            "cultural_fit": 70,
            "social_proof": 85,
            "career_progression": 75,
            "emotional_appeal": 65,
            "conciseness": 80,
            "bullet_point_clarity": 75,
            "industry_keywords": 75,
            "call_to_action": 60
        }
        ```
        '''
    else:
        resume_text = extract_resume_text(resume_file)
        prompt = RESUME_SCORING_PROMPT.format(resume_text=resume_text)
        ai_response = call_openai(prompt)

    try:
        scores = parse_ai_response(ai_response)  # Convert AI response to a dictionary
    except json.JSONDecodeError as e:
        print(f"json load error: {str(e)}")
        scores = {}  # Default empty dict if parsing fails
    except Exception as e:
        print(f"Exception in scoring: {str(e)}")
        scores = {}

    return ResumeScoringResponse(scores=scores)
