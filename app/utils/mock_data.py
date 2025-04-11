MOCK_TAILOR_RESPONSE = """
    {
  "review_suggestions": {
    "sections": {
      "experience": [
        {
          "company": "Eli Lilly India",
          "improvements": [
            {
              "current_text": "Led the transformation of the Advanced Analytical Data Enterprise team, aligning technical initiatives with strategic business goals...",
              "highlight_color": "green",
              "suggested_text": "Transformed the Advanced Analytical Data Enterprise team by aligning technology initiatives with strategic business goals, resulting in a 20% increase in project delivery efficiency and a strengthened alignment between tech and business functions."
            },
            {
              "current_text": "Managed a team of 12 engineers and data scientists...",
              "highlight_color": "green",
              "suggested_text": "Managed and mentored a high-performing team of 12 engineers and data scientists, fostering a culture of innovation and excellence, and achieving a 25% improvement in project turnaround times."
            }
          ],
          "position": "Director: LLMOps & MLOps"
        },
        {
          "company": "Stryker R&D India",
          "improvements": [
            {
              "current_text": "Led the design, implementation, and optimization of enterprise data platforms...",
              "highlight_color": "green",
              "suggested_text": "Designed and optimized enterprise data platforms integrating AWS cloud services, which led to a 30% improvement in operational efficiency and enabled seamless machine learning integrations."
            }
          ],
          "position": "Principal Architect: MLOps & DataOps"
        },
        {
          "company": "Sapient Razorfish",
          "improvements": [
            {
              "current_text": "Designed and implemented cloud architectures...",
              "highlight_color": "green",
              "suggested_text": "Successfully designed and implemented agile cloud architectures that improved system reliability by 40% and enhanced deployment speeds by incorporating efficient DevOps practices."
            }
          ],
          "position": "Solution Architect: COE DevOps & Cloud"
        },
        {
          "company": "Lowes India Pvt Ltd",
          "improvements": [
            {
              "current_text": "Led the design of AWS-based cloud infrastructure...",
              "highlight_color": "green",
              "suggested_text": "Pioneered the design and implementation of robust AWS-based cloud infrastructure, ensuring system scalability and reducing operational costs by 20% through effective resource management."
            }
          ],
          "position": "Technical Lead: Cloud & DevOps"
        }
      ],
      "new_sections": [
        {
          "content": "AWS Certified Solution Architect (Professional & Associate), AWS Certified DevOps Engineer",
          "highlight_color": "blue",
          "title": "Certifications"
        },
        {
          "content": "Summarize technical skills in a bullet-point format for a quick overview including key languages, tools, and platforms such as Python, Java, Docker, Kubernetes, Terraform, and others.",
          "highlight_color": "blue",
          "title": "Technical Skills Summary"
        }
      ],
      "summary": {
        "current_text": "A visionary technology leader with over 16 years of experience in MLOps, LLMOps, DataOps, DevOps, and cloud infrastructure...",
        "highlight_color": "yellow",
        "suggested_text": "Seasoned technology executive with 16+ years of experience in MLOps, LLMOps, and DevOps. Proven success in aligning technology strategies with business goals, establishing global Centers of Excellence, and building high-performing teams that drive innovation and business success. Expert in AI, machine learning, cloud transformation, and process optimization, ensuring seamless integration and continuous improvement of scalable solutions."
      }
    }
  }
}
"""

MOCK_RESUME_S3_URL = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/resume_02118e79-aa1e-4792-b5ca-6f6363ab0dd0.pdf"

MOCK_JD_S3_URL = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/job_description.json"

MOCK_PREV_QUESTIONS_S3_URL = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/previous_questions.json"

MOCK_AUDIO_S3_URL = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/mock_interviews/cd156fa5-e52f-4f02-83df-f2e4456735c5/audio_b7465672-cd156fa5-1.mp3"

MOCK_INTERVIEW_QUESTIONS_RESPONSE = """
{
  "questions": [
    "Can you elaborate on a project where you had to migrate infrastructure to Google Cloud and how you ensured the transition was seamless?"
  ]
}
"""

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

MOCK_SCORE = """```json
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
"""