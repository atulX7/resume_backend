MAX_QUESTIONS_PER_SESSION = 9
INTRO_QUESTION = "Hello and welcome! It's great to have you here today. I'm Alex, and I'm looking forward to our conversation. To start things off, could you please introduce yourself and share a bit about your career journey? Feel free to include any experiences or achievements that you believe would be important for us to know as we begin the interview."
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"

FEATURE_MOCK_INTERVIEW = "mock_interview"
FEATURE_RESUME_EVAL = "resume_eval"
FEATURE_RESUME_TAILOR = "resume_tailor"

FREE_PLAN_CODE = "free"

MOCK_INTERVIEW_PREV_Q_FILE = "previous_questions.json"
MOCK_INTERVIEW_PREV_JD_FILE = "job_description.json"
MOCK_INTERVIEW_LOG_FILE = "interview_log.json"
MOCK_INTERVIEW_AI_FEEDBACK_FILE = "ai_feedback.json"

EMAIL_SUB = "📢 Your Mock Interview Results Are Available!"
EMAIL_BODY = """
Hi {user_name},

Your mock interview session for **{job_title}** has been evaluated.

- 🏆 **Overall Score:** {score}/10
- 📊 **Key Strengths:** {strengths}
- 📌 **Areas for Growth:** {growth_areas}
- ⏳ **Duration:** {duration} minutes

You can view your results here: [View Results](https://resuwin.com/dashboard/mock-mate/{session_id})

Regards,  
ResuWin Team
"""
