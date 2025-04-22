MOCK_TAILOR_RESPONSE = """
{
  "summary": {
    "current_text": "Dedicated certified professional with more than 15 years of experience in Cloud, DataOps, DevOps, and MLOps versatile and quick learner, possesses strong communications and interpersonal skills.",
    "suggested_text": "Dedicated certified professional with over 15 years of expertise in Cloud, DataOps, DevOps, and MLOps. Skilled in creating and managing ETL workflows using Python, and proficient in ensuring data processing efficiency and accuracy. Strong communication and interpersonal skills.",
    "highlight_color": "yellow"
  },
  "experience": [
    {
      "position": "Principal Architect/AD: - MLOps & DataOps",
      "company": "Eli Lilly India- Bangalore",
      "matched_points": [
        {
          "text": "Leading the Advanced Analytical Data Enterprise team and managing it E2E technically.",
          "justification": "Highlights leadership and data integration management experience.",
          "highlight_color": "green"
        },
        {
          "text": "Maintaining a scalable infrastructure through the use of MLOps tools to automate integrate and monitor operational processes along with our data platform.",
          "justification": "Corresponds with optimizing data workflows to ensure efficiency.",
          "highlight_color": "green"
        }
      ],
      "modified_points": [
        {
          "current_text": "Design and implemented the Enterprise Data Platform for the Data scientist and integrated it with various platforms.",
          "suggested_text": "Designed and implemented comprehensive ETL workflows supporting high-volume data processing, ensuring seamless integration across various platforms.",
          "highlight_color": "yellow"
        }
      ],
      "missing_points": [
        {
          "expected_topic": "Technical Documentation",
          "suggestion": "Include experience with maintaining technical documentation and best-practice guidelines.",
          "highlight_color": "blue"
        }
      ]
    },
    {
      "position": "Principal Engineer: - MLOps & DataOps",
      "company": "Stryker R&D India- Gurgaon",
      "matched_points": [
        {
          "text": "Developed comprehensive machine learning pipelines, considering data source variability and modeling frameworks.",
          "justification": "Aligns with JD requirement of developing end-to-end workflows for data processing.",
          "highlight_color": "green"
        }
      ],
      "modified_points": [
        {
          "current_text": "Managed the deployment of models using the MLOps platform, while also automating inference testing.",
          "suggested_text": "Led the deployment and automation of ML models using Python scripts to perform real-time data validation and inference testing.",
          "highlight_color": "yellow"
        }
      ],
      "missing_points": [
        {
          "expected_topic": "REST API Integrations",
          "suggestion": "Elaborate on experience with developing REST API integrations for data automation.",
          "highlight_color": "blue"
        }
      ]
    }
  ],
  "user_skills_mapping": [
    {
      "skill": "Python",
      "currently_in_resume": true,
      "recommended_section": "experience",
      "action": "enhance"
    },
    {
      "skill": "NumPy",
      "currently_in_resume": false,
      "recommended_section": "skills",
      "action": "add"
    }
  ],
  "skills": {
    "used_well": [
      "MLOps",
      "DataOps",
      "DevOps",
      "AWS"
    ],
    "underutilized": [
      "Python",
      "MLflow",
      "Airflow"
    ],
    "missing_keywords": [
      "ETL Workflows",
      "NumPy",
      "REST API"
    ],
    "suggested_action": "Revise skills to include specific libraries and tools mentioned in the JD."
  },
  "jd_alignment_summary": {
    "total_jd_points": 10,
    "matched": 4,
    "partially_matched": 3,
    "missing": 3,
    "match_score_percent": 70
  },
  "new_sections": [
    {
      "title": "Technical Documentation Experience",
      "content": "Experienced in maintaining comprehensive technical documentation, data flow diagrams, and best-practice guidelines for seamless integration and operations.",
      "highlight_color": "blue"
    }
  ],
  "recommendations": [
    "Enhance Python skill visibility by detailing specific uses related to job duties such as ETL workflows.",
    "Add experience with NumPy and REST API integrations to align with JD specifics.",
    "Include a new section or elaboration on experience with technical documentation and real-time data validation efforts."
  ],
  "final_notes": [
    "Emphasize relevant Python projects, scripts, or frameworks used.",
    "Clarify and expand on projects or responsibilities that correlate with JD requirements.",
    "Consider adding quantifiable achievements where applicable."
  ],
  "section_scores": {
    "summary": 75,
    "experience": 80,
    "skills": 70,
    "projects": 60,
    "education": 60
  }
}
"""

MOCK_RESUME_STORAGE_KEY = "b7465672-73a5-4ce0-bd35-69c2297c363a/resume_02118e79-aa1e-4792-b5ca-6f6363ab0dd0.pdf"
MOCK_JD_STORAGE_KEY = "b7465672-73a5-4ce0-bd35-69c2297c363a/job_description.json"
MOCK_QUES_MAP_STORAGE_KEY = "b7465672-73a5-4ce0-bd35-69c2297c363a/questions_map.json"


MOCK_INTERVIEW_QUESTIONS_RESPONSE = """
{
  "questions": [
    "Can you elaborate on a project where you had to migrate infrastructure to Google Cloud and how you ensured the transition was seamless?"
  ]
}
"""

MOCK_QUES_MAPPING = [
    {
        "question_id": "",
        "question": "Can you elaborate on a project where you had to migrate infrastructure to Google Cloud and how you ensured the transition was seamless?",
        "answer_audio": "b7465672-73a5-4ce0-bd35-69c2297c363a/mock.mp3"
    }
]

MOCK_AUDIO_TRANSCRIPTION_TEXT = (
    "Scenario based questions in any technical interview are asked to assess the depth of your knowledge. "
    "So whenever you get a scenario based question, don't jump to the answer. Try to assess the situation. "
    "They are basically trying to differentiate you from other people. They are also trying to understand, "
    "do you really have production like uh experience in your resume. So they they want to throw a random scenario at "
    "you. Probably that has something happened in their area or that they have experienced themselves. "
    "They want to assess what options you will be performing, what activities you will be performing in such a scenario."
    " So start before you start answering the question. Try to assess, try to understand what was the situation, what "
    "sort of services they use, what was the scenario. Get more details about the question, and "
    "then start framing your answer. That will help you score better in these kind of questions."
)

MOCK_INTERVIEW_EVALUATION_RESPONSE = """
{
    "question_evaluations": {
        "3102c45b-7252d078-1": {
            "score": 2,
            "feedback": "The candidate failed to provide an introduction or share any relevant career experiences, instead offering advice on how to approach scenario-based interview questions. This response did not fulfill the question’s request for personal career insights and achievements.",
            "follow_up_question": "Could you please share more about your career background and some key achievements you've had in your previous roles?"
        },
        "3102c45b-7252d078-2": {
            "score": 1,
            "feedback": "The candidate repeated the same response from the first question, failing to provide any details about a project involving the migration of infrastructure to Google Cloud. This lack of a specific answer did not demonstrate any relevant experience or knowledge of cloud migration, which was crucial for this question.",
            "follow_up_question": "Can you describe a specific project where you successfully migrated an infrastructure to the cloud, detailing the steps you took and the challenges you overcame?"
        }
    },
    "final_assessment": {
        "overall_score": 2,
        "key_strengths": [
         "The candidate attempted to discuss the importance of scenario-based questions, which indicates an understanding of the interview process and possibly a strategic approach to answering questions."
     ],
        "areas_for_growth": [
            "The candidate needs to provide direct answers that are specific to the questions asked.",
            "Improved structure and clarity in responses would be beneficial.",
            "Sharing personal experiences and achievements relevant to the role is crucial."
        ],
        "skill_assessment": {
            "technical": 1,
            "problem_solving": 2,
            "communication": 1,
            "leadership": 1,
            "adaptability": 1,
            "behavioral_fit": 1,
            "confidence": 2
        }
    }
}
"""

MOCK_SCORE = """
 {
  "overall_summary": "The resume showcases an impressive background in AI & Cloud Engineering with a strong emphasis on leadership and technological innovation. It demonstrates a detailed and structured presentation of achievements and skills, using metrics effectively. Improvements could be made in ATS readability and minor formatting aspects to enhance overall presentation.",
  "overall_score": 89.0,
  "detailed_evaluation": [
    {
      "criterion": "Layout & Searchability",
      "description": "Checks if the resume is visually clean, well-structured, and easy to navigate.",
      "score": 40,
      "status": "red",
      "assessment": "The resume is well-organized with clearly defined sections, making it easy to navigate."
    },
    {
      "criterion": "ATS Readability",
      "description": "Assesses whether the resume can be effectively parsed by Applicant Tracking Systems (ATS).",
      "score": 65,
      "status": "yellow",
      "assessment": "Heavy use of formatting symbols might affect ATS parsing; consider simplifying."
    },
    {
      "criterion": "Impact & Effectiveness",
      "description": "Evaluates if the resume focuses on outcomes and achievements rather than just duties.",
      "score": 90,
      "status": "green",
      "assessment": "Strong focus on achievements with clear outcomes and impact highlighted."
    },
    {
      "criterion": "Quantifiable Achievements",
      "description": "Checks for use of metrics, KPIs, or measurable impact to demonstrate success.",
      "score": 88,
      "status": "green",
      "assessment": "Excellent use of quantifiable achievements to showcase impact and results."
    },
    {
      "criterion": "Readability & Clarity",
      "description": "Ensures the resume is clear, simple, and avoids jargon or unnecessary complexity.",
      "score": 80,
      "status": "green",
      "assessment": "The resume is clear and avoids excessive jargon, making complex ideas accessible."
    },
    {
      "criterion": "Personal Branding",
      "description": "Assesses whether the resume presents a clear, unique value proposition and professional identity.",
      "score": 82,
      "status": "green",
      "assessment": "Strong personal branding, particularly in highlighting leadership and innovation in AI."
    },
    {
      "criterion": "Grammar & Spelling",
      "description": "Checks for spelling, grammar, punctuation, and other language issues.",
      "score": 95,
      "status": "green",
      "assessment": "The resume is free from grammar and spelling mistakes."
    },
    {
      "criterion": "Contact Information",
      "description": "Validates that contact info is complete, professional, and properly formatted.",
      "score": 90,
      "status": "green",
      "assessment": "Complete and well-formatted contact information, including links to professional profiles."
    },
    {
      "criterion": "Section Completeness",
      "description": "Checks if the resume contains all essential sections like Experience, Education, Skills, etc.",
      "score": 85,
      "status": "green",
      "assessment": "Contains all essential sections, although explicit education details are not included."
    },
    {
      "criterion": "Visual Appeal",
      "description": "Evaluates fonts, spacing, alignment, and use of white space to ensure professional look.",
      "score": 75,
      "status": "yellow",
      "assessment": "Overall visually appealing but could benefit from improved spacing and alignment."
    },
    {
      "criterion": "Cultural Fit",
      "description": "Assesses how well the tone, style, and presentation align with the target industry or company type.",
      "score": 80,
      "status": "green",
      "assessment": "The tone and style align well with the tech and AI industries."
    },
    {
      "criterion": "Career Progression",
      "description": "Analyzes if the resume shows logical career growth, promotions, or expanding responsibilities.",
      "score": 88,
      "status": "green",
      "assessment": "Demonstrates logical career progression with increasing responsibilities and leadership roles."
    },
    {
      "criterion": "Emotional & Persuasive Appeal",
      "description": "Evaluates if the resume feels compelling, confident, and persuasive to the reader.",
      "score": 85,
      "status": "green",
      "assessment": "Compelling and confident presentation of skills and achievements."
    },
    {
      "criterion": "Conciseness",
      "description": "Checks if the content is focused, avoids unnecessary fluff, and respects space constraints.",
      "score": 80,
      "status": "green",
      "assessment": "Content is concise and stays relevant, avoiding unnecessary details."
    },
    {
      "criterion": "Bullet Point Clarity",
      "description": "Assesses whether bullet points are action-driven, results-focused, and easy to read.",
      "score": 20,
      "status": "red",
      "assessment": "Bullet points are clear, action-oriented, and focus on results."
    },
    {
      "criterion": "Industry-Specific Keywords",
      "description": "Checks for presence of role- and domain-specific keywords for better ATS matching.",
      "score": 90,
      "status": "green",
      "assessment": "Excellent use of industry-specific keywords enhances relevance and ATS matching."
    },
    {
      "criterion": "Call-to-Action",
      "description": "Evaluates if the resume ends with a closing statement that encourages recruiter action.",
      "score": 60,
      "status": "yellow",
      "assessment": "Lacks a strong closing statement or call-to-action to engage recruiters."
    },
    {
      "criterion": "Overall Cohesion",
      "description": "Assesses consistency in formatting, language, and overall tone across the resume.",
      "score": 85,
      "status": "green",
      "assessment": "Maintains consistent formatting and tone throughout the document."
    }
  ]
}
"""


MOCK_UPLOAD_ANSWER = """
{
    "status": "success",
    "answer_audio_key": "fc38451f-2305-4572-a84a-7cf7db0522bd/mock_interviews/6d7c4e49-a114-473f-83d0-0b07523166ab/audio/audio_q2.mp3"
}
"""

MOCK_PROCESS_START = """
{
    "status": "processing",
    "message": "Your interview is being evaluated. You'll be notified once it's done."
}
"""

MOCK_SESSION_DETAILS = """
{
    "session_id": "6d7c4e49-a114-473f-83d0-0b07523166ab",
    "job_title": "diector",
    "created_at": "2025-04-18 08:48:50",
    "status": "completed",
    "overall_score": 1.0,
    "key_strengths": [],
    "areas_for_growth": [
        "Ability to understand and respond to questions appropriately.",
        "Presentation of relevant personal experiences and achievements.",
        "Providing complete responses to technical and leadership inquiries."
    ],
    "skill_assessment": {
        "technical": 2.0,
        "problem_solving": 1.0,
        "communication": 1.0,
        "leadership": 0.0,
        "adaptability": 0.0,
        "behavioral_fit": 0.0,
        "confidence": 1.0
    },
    "evaluation_results": [
        {
            "question": "Hello and welcome! It's great to have you here today. I'm Alex, and I'm looking forward to our conversation. To start things off, could you please introduce yourself and share a bit about your career journey? Feel free to include any experiences or achievements that you believe would be important for us to know as we begin the interview.",
            "score": 2.0,
            "feedback": "The candidate's response was not aligned with the question. Instead of introducing themselves and discussing their career journey, they provided an explanation of MLOps and its significance in relation to DevOps. The lack of personal background or achievements makes it difficult to gauge this aspect of their professional experience.",
            "audio_presigned_url": "",
            "follow_up_question": "Can you please provide an introduction to your career journey, highlighting key experiences and achievements relevant to the director role?"
        },
        {
            "question": "Can you explain your experience with creating ETL workflows using Python? What libraries and techniques did you find most effective?",
            "score": 1.0,
            "feedback": "The candidate repeated the same response as before about MLOps, which was unrelated to the question of creating ETL workflows using Python. There was no mention of libraries or techniques used, indicating a misunderstanding or lack of relevant experience.",
            "audio_presigned_url": "",
            "follow_up_question": "Could you discuss your experience with ETL workflows in Python and the specific libraries you have used?"
        },
        {
            "question": "Describe a challenging scenario where you had to optimize a data workflow to reduce latency. How did you approach the problem and what were the results?",
            "score": 1.0,
            "feedback": "Once again, the candidate provided the same off-topic response about MLOps. They did not address the question regarding optimizing a data workflow to reduce latency, suggesting a significant gap in their ability to communicate relevant experience.",
            "audio_presigned_url": "",
            "follow_up_question": "Could you describe a specific challenge you faced in optimizing a data workflow and how you overcame it?"
        },
        {
            "question": "From your experience with DevOps, how do you ensure data accuracy when integrating data from multiple sources into a unified system?",
            "score": 0.0,
            "feedback": "No response provided.",
            "audio_presigned_url": "",
            "follow_up_question": "How do you approach ensuring data accuracy when integrating multiple data sources into a unified system?"
        },
        {
            "question": "In the context of data monitoring, how do you identify and address anomalies or performance bottlenecks in real-time?",
            "score": 0.0,
            "feedback": "No response provided.",
            "audio_presigned_url": "",
            "follow_up_question": "Can you explain how you handle real-time data monitoring to identify and rectify anomalies or performance issues?"
        },
        {
            "question": "You've worked with REST API integrations before. Can you share a project where automating data exchanges significantly enhanced operational efficiency?",
            "score": 0.0,
            "feedback": "No response provided.",
            "audio_presigned_url": "",
            "follow_up_question": "Could you share an example of a project where REST API integration significantly improved operational efficiency?"
        },
        {
            "question": "How do you approach technical documentation and why do you think it's critical for projects involving data flows and integrations?",
            "score": 0.0,
            "feedback": "No response provided.",
            "audio_presigned_url": "",
            "follow_up_question": "Why do you believe technical documentation is essential, especially for projects involving complex data flows?"
        },
        {
            "question": "Describe a situation where you had to lead a team through a significant change or project. What was your strategy for ensuring successful outcomes?",
            "score": 0.0,
            "feedback": "No response provided.",
            "audio_presigned_url": "",
            "follow_up_question": "Please describe a situation where you led a team through significant changes and how you ensured a successful outcome."
        },
        {
            "question": "Given your experience across AWS and Azure, how do you adapt to new cloud technologies and ensure that your skills remain up to date?",
            "score": 0.0,
            "feedback": "No response provided.",
            "audio_presigned_url": "",
            "follow_up_question": "How do you keep your cloud computing skills up to date, particularly in AWS and Azure?"
        },
        {
            "question": "Can you provide an example where mentoring a junior team member led to a positive impact on a project or team dynamic?",
            "score": 0.0,
            "feedback": "No response provided.",
            "audio_presigned_url": "",
            "follow_up_question": "Can you provide an example of mentoring a junior team member and its positive impact on the team or project?"
        }
    ]
}
"""
