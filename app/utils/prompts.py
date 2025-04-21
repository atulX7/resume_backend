JD_TAILORING_PROMPT = """
    You are an expert resume coach and recruiter with 10+ years of experience. Your task is to **analyze the entire resume file** resume_content given below and **suggest targeted improvements** to help tailor the resume for the job below.

🧾 Job Title: {job_title}

📋 Full Job Description:
{job_description}

🧠 User-Declared Proficiency / Skills:
{skills}


    🎯 **Resume Content:**
    {resume_content}

🔍 Your Responsibilities:
1. Thoroughly analyze the resume and compare it against the job description and skills provided.
2. Suggest inline improvements to each section (Summary, Experience, Skills, Projects, Education).
3. Rewrite vague statements to include measurable results and relevant keywords from the JD.
4. Identify and highlight missing keywords, tools, or expected content.
5. Suggest where underutilized user skills can be better demonstrated.
6. Provide scores and final improvement tips to enhance alignment with the JD.

🖍️ Highlight Color Codes:
- "green": Already aligned well with the JD
- "yellow": Needs improvement or rewording to improve match
- "blue": Missing but important for this JD


    🎯 **Response Format (JSON)**
    {{
    "summary": {{
      "current_text": "...",
      "suggested_text": "...",
      "highlight_color": "yellow"
    }},
    "experience": [
  {{
    "position": "...",
    "company": "...",
    "matched_points": [
      {{
        "text": "...",
        "justification": "...",
        "highlight_color": "green"
      }}
    ],
    "modified_points": [
      {{
        "current_text": "...",
        "suggested_text": "...",
        "highlight_color": "yellow"
      }}
    ],
    "missing_points": [
      {{
        "expected_topic": "...",
        "suggestion": "...",
        "highlight_color": "blue"
      }}
    ]
  }}
]
,
    "user_skills_mapping": [
  {{
    "skill": "...",
    "currently_in_resume": true,
    "recommended_section": "...",
    "action": "enhance"
  }},
  {{
    "skill": "...",
    "currently_in_resume": false,
    "recommended_section": "...",
    "action": "add"
  }}
],
"skills": {{
  "used_well": ["..."],
  "underutilized": ["..."],
  "missing_keywords": ["..."],
  "suggested_action": "..."
}},
"jd_alignment_summary": {{
    "total_jd_points": <number of skills/points in jd>,
    "matched": <number of matched skills/points>,
    "partially_matched": <number of partially matched skills/points>,
    "missing": <number of missing skills/points>,
    "match_score_percent": <0–100>
  }},
    "new_sections": [
      {{
        "title": "...",
        "content": "...",
        "highlight_color": "blue"
      }}
    ],
    "recommendations": ["..."],
    "final_notes": ["..."],
    "section_scores": {{
    "summary": <0–100>,
    "experience": <0–100>,
    "skills": <0–100>,
    "projects": <0–100>,
    "education": <0–100>
  }}
  }}
    
    Please analyze and return **only the structured JSON response**. Do not include any explanation or extra commentary.
    """


RESUME_SCORING_PROMPT = """
    You are an expert resume evaluator with years of experience in hiring, recruiting, and career coaching.

Your task is to thoroughly analyze the resume provided and return a structured JSON response based on the criteria listed below.

You must:

1. Provide a **brief overall summary** of the resume’s quality (3–5 lines).
2. Score the resume across **18 specific criteria** (0–100) which will be overall_score.
3. For each criterion:
    - Add a **description** of what it measures
    - Provide a **score**
    - Provide a **brief assessment**
    - Add a **color-coded status**:
      - 🟢 `"green"`: Excellent (score 80–100)
      - 🟡 `"yellow"`: Average/Needs Improvement (score 60–79)
      - 🔴 `"red"`: Poor (score 0–59)

---

🎯 **Evaluation Criteria**

1. **Layout & Searchability** – Is the resume well-structured, easy to navigate, and visually appealing?
2. **ATS Readability** – Can an Applicant Tracking System (ATS) effectively parse this resume?
3. **Impact & Effectiveness** – Does the resume emphasize achievements rather than responsibilities?
4. **Quantifiable Achievements** – Are there measurable results (e.g., "Increased revenue by 25%")?
5. **Readability & Clarity** – Is it well-written, free of jargon, and easy to understand?
6. **Personal Branding** – Does it have a strong professional summary showcasing unique skills?
7. **Grammar & Spelling** – Are there any errors in spelling, punctuation, or grammar?
8. **Contact Information** – Is it correctly formatted and complete?
9. **Section Completeness** – Does it include Experience, Education, Skills, etc.?
10. **Visual Appeal** – Are font choice, whitespace, and formatting professional?
11. **Cultural Fit** – Does it align with industry norms and company values?
12. **Career Progression** – Does it show logical career growth and promotions?
13. **Emotional & Persuasive Appeal** – Is it engaging, compelling, and well-crafted?
14. **Conciseness** – Is it to-the-point, avoiding fluff and excessive length?
15. **Bullet Point Clarity** – Are bullet points clear, direct, and meaningful?
16. **Industry-Specific Keywords** – Does it contain relevant terminology for the role?
17. **Call-to-Action** – Does it end with a compelling closing statement?
18. **Overall Cohesion** – Is the resume consistent in tone, style, and flow?

---

✅ **Return Format**

Return **only** a valid JSON object in the following format:

{{
  "overall_summary": "<Brief 3–5 line summary of the resume’s overall strengths and weaknesses>",
  "overall_score": <0–100>,
  "detailed_evaluation": [
    {{
      "criterion": "Layout & Searchability",
      "description": "Checks if the resume is visually clean, well-structured, and easy to navigate.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "ATS Readability",
      "description": "Assesses whether the resume can be effectively parsed by Applicant Tracking Systems (ATS).",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Impact & Effectiveness",
      "description": "Evaluates if the resume focuses on outcomes and achievements rather than just duties.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Quantifiable Achievements",
      "description": "Checks for use of metrics, KPIs, or measurable impact to demonstrate success.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Readability & Clarity",
      "description": "Ensures the resume is clear, simple, and avoids jargon or unnecessary complexity.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Personal Branding",
      "description": "Assesses whether the resume presents a clear, unique value proposition and professional identity.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Grammar & Spelling",
      "description": "Checks for spelling, grammar, punctuation, and other language issues.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Contact Information",
      "description": "Validates that contact info is complete, professional, and properly formatted.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Section Completeness",
      "description": "Checks if the resume contains all essential sections like Experience, Education, Skills, etc.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Visual Appeal",
      "description": "Evaluates fonts, spacing, alignment, and use of white space to ensure professional look.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Cultural Fit",
      "description": "Assesses how well the tone, style, and presentation align with the target industry or company type.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Career Progression",
      "description": "Analyzes if the resume shows logical career growth, promotions, or expanding responsibilities.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Emotional & Persuasive Appeal",
      "description": "Evaluates if the resume feels compelling, confident, and persuasive to the reader.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Conciseness",
      "description": "Checks if the content is focused, avoids unnecessary fluff, and respects space constraints.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Bullet Point Clarity",
      "description": "Assesses whether bullet points are action-driven, results-focused, and easy to read.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Industry-Specific Keywords",
      "description": "Checks for presence of role- and domain-specific keywords for better ATS matching.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Call-to-Action",
      "description": "Evaluates if the resume ends with a closing statement that encourages recruiter action.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }},
    {{
      "criterion": "Overall Cohesion",
      "description": "Assesses consistency in formatting, language, and overall tone across the resume.",
      "score": <number>,
      "status": "green | yellow | red",
      "assessment": "<Short feedback>"
    }}
  ]
}}

    🔹 **Resume to Evaluate**
    {resume_text}

    Please analyze the entire resume and return **only the structured JSON response**.
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
