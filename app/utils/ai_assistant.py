from app.utils.openai_client import call_openai
from app.utils.prompts import JD_TAILORING_PROMPT
from app.utils.resume_parser import extract_resume_text

def analyze_resume_with_ai(job_title: str, job_description: str, skills: str, resume_file):
    """Sends resume as an attachment to AI and retrieves structured review suggestions."""
    resume_content = extract_resume_text(resume_file)
    prompt = JD_TAILORING_PROMPT.format(
        job_description=job_description,
        job_title=job_title,
        resume_content=resume_content,
        skills=skills
    )

    # content = call_openai(prompt)
    content = '''json
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
    return content