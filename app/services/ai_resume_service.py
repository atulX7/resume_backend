from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.resume_service import handle_resume_upload
from app.utils.ai_assistant import analyze_resume_with_ai
from app.utils.aws_utils import generate_presigned_url


def tailor_resume(db: Session, user_id: str, job_title: str, job_description: str, skills: str, user_resume: UploadFile):
    """Sends the uploaded resume file as an attachment to AI for analysis and improvement recommendations."""

    if settings.MOCK_DATA:
        ai_response = '''json
    {
      "sections": {
        "summary": {
          "current_text": "",
          "suggested_text": "Director-Level Data Scientist with extensive experience in developing data products and machine learning models, specializing in Risk, Fraud, and portfolio management. Proven track record of delivering business value through innovative solutions and stakeholder management.",
          "highlight_color": "yellow"
        },
        "experience": [
          {
            "position": "Cloud Engineer",
            "company": "Company XX",
            "improvements": [
              {
                "current_text": "Replaced the existing infrastructure with IaC using Cloud Deployment Manager and Terraform.",
                "suggested_text": "Led the architecture transformation by implementing Infrastructure-as-Code (IaC) with Cloud Deployment Manager and Terraform, enhancing deployment efficiency by 40%.",
                "highlight_color": "green"
              },
              {
                "current_text": "Build and maintain software documentation sites using various programming languages involving Python, Java and Go",
                "suggested_text": "Developed and maintained comprehensive software documentation utilizing Python, Java, and Go, streamlining knowledge sharing and collaboration across teams.",
                "highlight_color": "green"
              }
            ]
          },
          {
            "position": "Support Engineer",
            "company": "Company XY",
            "improvements": [
              {
                "current_text": "Built and maintained cloud deployments for over 75 clients.",
                "suggested_text": "Spearheaded the deployment and management of cloud infrastructures for over 75 clients, leveraging Google Cloud services to boost operational efficiency.",
                "highlight_color": "green"
              },
              {
                "current_text": "Developed an in-house monitoring and alerting agent for the entire infrastructure deployed on Cloud. Leading to $100k reduction in the infrastructure spend.",
                "suggested_text": "Architected an in-house monitoring and alerting solution that reduced infrastructure costs by $100k through enhanced resource utilization and proactive issue resolution.",
                "highlight_color": "green"
              }
            ]
          }
        ],
        "new_sections": [
          {
            "title": "Professional Summary",
            "content": "Experienced Cloud and Data Professional with expertise in building scalable data solutions and cloud architectures. Strong leadership skills in managing cross-functional teams to deliver high-impact projects.",
            "highlight_color": "blue"
          },
          {
            "title": "Certifications",
            "content": "AWS Certified Solutions Architect - Associate (2022-2025)",
            "highlight_color": "blue"
          }
        ]
      }
    }
    '''
        s3_url = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/resume_02118e79-aa1e-4792-b5ca-6f6363ab0dd0.pdf"
    else:
        # ✅ Call AI assistant to analyze resume
        ai_response = analyze_resume_with_ai(job_title, job_description, skills, user_resume)

        # ✅ Upload the AI-analyzed resume to S3 (optional, for user downloads)
        resume = handle_resume_upload(db, user_id, user_resume, job_title)
        s3_url = resume.s3_url

    return {
        "resume_url": generate_presigned_url(s3_url),
        "review_suggestions": ai_response
    }