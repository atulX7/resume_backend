JD_TAILORING_PROMPT = """
    You are an expert resume reviewer over a decade of experience. Your task is to analyze the attached resume file
    and suggest inline improvements based on the following job details:

    - **Job Title:** {job_title}
    - **Job Description:** {job_description}
    - **Candidate Skills:** {skills}

    🎯 **Resume Content:**
    {resume_content}

    🔹 **Instructions:**
    1. Identify **weak areas** in the resume and **suggest improvements**.
    2. Highlight **missing sections** (e.g., "Add a Certifications section").
    3. Return the analysis in a structured **JSON format**.

    🎯 **Response Format (JSON)**
    {{
      "sections": {{
        "summary": {{
          "current_text": "Existing summary...",
          "suggested_text": "Improved summary with impact...",
          "highlight_color": "yellow"
        }},
        "experience": [
          {{
            "position": "Software Engineer",
            "company": "TechCorp",
            "improvements": [
              {{
                "current_text": "Worked on APIs.",
                "suggested_text": "Developed scalable RESTful APIs using FastAPI, improving response times by 30%.",
                "highlight_color": "green"
              }}
            ]
          }}
        ],
        "new_sections": [
          {{
            "title": "Certifications",
            "content": "AWS Certified Solutions Architect",
            "highlight_color": "blue"
          }}
        ]
      }}
    }}
    """


RESUME_SCORING_PROMPT = """
    You are an expert resume evaluator with years of experience in hiring and career coaching. 
    Your task is to analyze the following resume and **provide a detailed score breakdown** 
    based on various criteria.

    🎯 **Evaluation Criteria** (Score range: 0-100)
    1. **Layout & Searchability** – Is the resume well-structured, easy to navigate, and visually appealing?
    2. **ATS Readability** – Can an Applicant Tracking System (ATS) effectively parse this resume?
    3. **Impact & Effectiveness** – Does the resume emphasize achievements rather than responsibilities?
    4. **Quantifiable Achievements** – Are there measurable results (e.g., "Increased revenue by 25%")?
    6. **Readability & Clarity** – Is it well-written, free of jargon, and easy to understand?
    7. **Personal Branding** – Does it have a strong professional summary showcasing unique skills?
    8. **Grammar & Spelling** – Are there any errors in spelling, punctuation, or grammar?
    9. **Contact Information** – Is it correctly formatted and complete?
    10. **Section Completeness** – Does it include Experience, Education, Skills, etc.?
    11. **Visual Appeal** – Are font choice, whitespace, and formatting professional?
    12. **Cultural Fit** – Does it align with industry norms and company values?
    13. **Career Progression** – Does it show logical career growth and promotions?
    14. **Emotional & Persuasive Appeal** – Is it engaging, compelling, and well-crafted?
    15. **Conciseness** – Is it to-the-point, avoiding fluff and excessive length?
    16. **Bullet Point Clarity** – Are bullet points clear, direct, and meaningful?
    17. **Industry-Specific Keywords** – Does it contain relevant terminology for the role?
    18. **Call-to-Action** – Does it end with a compelling closing statement?

    ✅ **Scoring Format**
    Return the response in the following JSON format:
    {{
        "Layout": <score>,
        "ATS_Readability": <score>,
        "Impact": <score>,
        "Quantifiable_Achievements": <score>,
        "Readability": <score>,
        "Personal_Branding": <score>,
        "Grammar_Spelling": <score>,
        "Contact_Info": <score>,
        "Section_Completeness": <score>,
        "Visual_Appeal": <score>,
        "Cultural_Fit": <score>,
        "Career_Progression": <score>,
        "Emotional_Appeal": <score>,
        "Conciseness": <score>,
        "Bullet_Point_Clarity": <score>,
        "Industry_Keywords": <score>,
        "Call_To_Action": <score>
    }}

    🔹 **Resume to Evaluate**
    {resume_text}

    Please analyze and return **only the structured JSON response**.
    """


INTERVIEW_QUESTION_PROMPT = """
You are conducting an interview for the role of **{job_title}**.

### **Candidate's Resume:**
{resume_text}

### **Job Description:**
{job_description}

### **Instructions:**
Generate exactly **{max_questions} unique questions** for the candidate based on:
1. **Technical expertise** (resume skills + job description).
2. **Scenario-based** problem-solving.
3. **Behavioral and leadership qualities**.
4. **Adaptability & Learning capabilities**.

📌 **Important Guidelines:**
- Make **each question unique** (NO repetitions).
- Keep it **conversational & natural**.
- Return the **{max_questions} questions in a structured JSON format**.

### **Response Format (JSON)**
Return the questions in **valid JSON format** only as follows:
{{
  "questions": [
    "Question 1...",
    "Question 2...",
    "Question 3...",
    "Question 4...",
    "Question 5...",
    "Question 6...",
    "Question 7...",
    "Question 8...",
    "Question 9...",
    "Question 10...",
    "Question 11...",
    "Question 12...",
    "Question 13...",
    "Question 14...",
    "Question 15...",
    "Question 16...",
    "Question 17...",
    "Question 18...",
    "Question 19..."
  ]
}}
"""

INTERVIEW_EVALUATION_PROMPT = """
You are an expert interview evaluator. Analyze a candidate’s responses for the role of {job_title}.

### **Candidate Responses**
{interview_log}

### **Evaluation Criteria**
1️⃣ **Per-Question Analysis**:
- Assign a **score (out of 10)** for each response.
- Provide **detailed feedback** on improvements.
- Suggest a **follow-up question** if needed.

2️⃣ **Overall Interview Analysis**:
- Provide an **overall score (out of 10)** for the candidate.
- List **key strengths** and **areas for improvement**.
- Rate their **technical, problem-solving, communication, leadership, adaptability, cultural fit, and confidence** skills.

### **Response Format (JSON)**
{{
    "question_evaluations": {{
        "<question_id>": {{
            "score": <numeric_score>,
            "feedback": "<detailed_feedback>",
            "follow_up_question": "<next_question>"
        }}
    }},
    "final_assessment": {{
        "overall_score": <numeric_score>,
        "key_strengths": ["Highlight of strong points..."],
        "areas_for_growth": ["Areas that need improvement..."],
        "skill_assessment": {{
            "technical": <numeric_score>,
            "problem_solving": <numeric_score>,
            "communication": <numeric_score>,
            "leadership": <numeric_score>,
            "adaptability": <numeric_score>,
            "behavioral_fit": <numeric_score>,
            "confidence": <numeric_score>
        }}
    }}
}}
"""

COVER_LETTER_PROMPT = """
You are a professional career consultant. Generate a formal, well-structured cover letter for the following job:

Job Title: {job_title}
Company: {company_name}

Job Description:
{job_description}

Candidate Resume:
{user_resume}

Ensure the cover letter is personalized, engaging, and aligned with the job description.
"""