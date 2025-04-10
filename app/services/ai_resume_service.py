import json

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.resume_service import handle_resume_upload
from app.utils.ai_assistant import analyze_resume_with_ai
from app.utils.aws_utils import generate_presigned_url
from app.utils.utils import parse_ai_response


def tailor_resume(
    db: Session,
    user_id: str,
    job_title: str,
    job_description: str,
    skills: str,
    user_resume: UploadFile,
):
    """Sends the uploaded resume file as an attachment to AI for analysis and improvement recommendations."""

    if settings.MOCK_DATA:
        ai_response = """
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
        review_suggestions = json.loads(ai_response)
        s3_url = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/resume_02118e79-aa1e-4792-b5ca-6f6363ab0dd0.pdf"
    else:
        # ✅ Call AI assistant to analyze resume
        ai_response = analyze_resume_with_ai(
            job_title, job_description, skills, user_resume
        )
        try:
            review_suggestions = parse_ai_response(
                ai_response
            )  # Convert AI response to a dictionary
        except json.JSONDecodeError as e:
            print(f"json load error: {str(e)}")
            review_suggestions = {}  # Default empty dict if parsing fails
        except Exception as e:
            print(f"Exception in tailoring: {str(e)}")
            review_suggestions = {}

        # ✅ Upload the AI-analyzed resume to S3 (optional, for user downloads)
        resume = handle_resume_upload(db, user_id, user_resume, job_title)
        s3_url = generate_presigned_url(resume.s3_url)

    return {
        "resume_url": s3_url,
        "review_suggestions": review_suggestions
    }