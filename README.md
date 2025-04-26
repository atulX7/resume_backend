#  🤖 Resume Evaluator & Mock Interview API

A scalable FastAPI backend application for resume evaluation, mock interviews, scoring, and AI-driven feedback — using OpenAI, AWS S3, SQS, and PostgreSQL.

---

## 🚀 Features

- 🔍 Resume parsing and AI-based scoring
- 🎤 Mock interview with audio recording and transcription
- 🤖 GPT-powered interview feedback and improvement suggestions
- ☁️ AWS integrations: S3 (resume/audio), SQS (job queue), Transcribe (audio-to-text)
- 🧠 JD alignment + keyword analysis + ATS-friendly evaluation

---

## 📦 Tech Stack

- **Backend**: FastAPI + Pydantic
- **Task Queue**: AWS SQS
- **AI Integration**: OpenAI (GPT-4o)
- **Cloud Services**: AWS S3, Transcribe
- **Auth & Roles**: JWT & custom scopes
- **CI/CD**: GitHub Actions

---
## ☁️ AWS Integration

This application interacts with AWS for several services. You must ensure the EC2 instance or user running the backend has the correct **IAM Role** attached.

---

### ✅ Required IAM Policies

Attach the following managed policies to your IAM Role (or IAM User, if using access keys):

- `AmazonS3FullAccess` – For uploading/downloading resumes and interview artifacts
- `AmazonSQSFullAccess` – For sending/receiving interview processing jobs via SQS
- `AmazonTranscribeFullAccess` – For converting audio to text during mock interviews

---
### 🗂️ S3 “tmp/” Folder & Lifecycle Cleanup

We use a **temporary** S3 prefix (`tmp/`) to stage uploaded resumes before a session is confirmed. To avoid orphaned files and unnecessary storage costs, add a lifecycle rule:

1. **Prefix:** `tmp/`
2. **Action:** Expire (Permanently delete) objects
3. **Age:** 24 hours (or your desired TTL)

```yaml
# Example S3 Lifecycle configuration (in JSON)
{
  "Rules": [
    {
      "ID": "TmpFolderAutoExpire",
      "Prefix": "tmp/",
      "Status": "Enabled",
      "Expiration": { "Days": 1 },
      "NoncurrentVersionExpiration": { "NoncurrentDays": 1 }
    }
  ]
}
```

---

### 📬 AWS SQS Queue (Mock Interview Processing)

An SQS queue is used to offload intensive tasks like audio transcription and AI evaluation.

**Steps:**

1. Create an SQS queue (e.g., `mock-interview-queue`)
2. Copy the SQS URL (e.g.,  
   `https://sqs.ap-south-1.amazonaws.com/123456789012/mock-interview-queue`)
3. Add it to your `.env` file:

```env
SQS_MOCK_INTERVIEW_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/123456789012/mock-interview-queue
```

## 🛠️ Local Development Setup

### ✅ Prerequisites

Make sure the following tools are installed on your system:

- Python `3.11`
- [Poetry](https://python-poetry.org/docs/)
- PostgreSQL (locally or cloud-managed)
- AWS credentials (for S3 & SQS access)
- OpenAI API key (for resume evaluations)

---

### 🛠️ Step 1: Clone & Install

```bash
git clone https://github.com/atulX7/resume_backend.git
cd resume_backend

# Install all dependencies
poetry install
```


### ⚙️ Step 2: Environment Variables

Create a .env file in the project root:
```bash
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/yourdb
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION_NAME=ap-south-1
S3_BUCKET_NAME=your_s3_bucket

OPENAI_API_KEY=your_openai_api_key

SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=you@example.com
SMTP_PASSWORD=your_password

ALLOW_ORIGINS=http://localhost:3000
MOCK_DATA=True
SQS_MOCK_INTERVIEW_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/xxx/mock-interview-queue
SEED_DB=True
```

### 🧪 Step 3: Database Migrations
```bash
# Run migrations using Alembic
poetry run alembic upgrade head
```

### 🚀 Step 4: Run the FastAPI App & SQS worker
```bash
# Run migrations using Alembic
poetry run uvicorn app.main:app --reload

# Run worker manually
poetry run python sqs_worker.py
```
Visit the interactive API docs at: http://localhost:8000/docs

---

## 🧰 Project Structure
```bash
resume_backend/
├── .github/                 # GitHub workflows and actions
├── alembic/                 # Alembic migration files
├── app/                     # Main FastAPI application
│   ├── api/                 # Route definitions
│   ├── core/                # Settings, logging, and configuration
│   ├── database/            # Database models, sessions, and queries
│   ├── middleware/          # Custom middlewares
│   ├── models/              # ORM model definitions
│   ├── schemas/             # Pydantic schema models
│   ├── services/            # Core business logic
│   ├── utils/               # Utility functions (OpenAI, AWS, etc.)
│   ├── __init__.py
│   └── main.py              # FastAPI entrypoint
├── logs/                    # Centralized log directory
├── .env                     # Local environment configuration
├── alembic.ini              # Alembic config
├── poetry.lock              # Locked package versions
├── pyproject.toml           # Project & dependency config
├── README.md                # You're reading it!
└── sqs_worker.py            # Background worker for SQS queue
```

---

## 🛡️ Deployment
This project uses GitHub Actions to deploy automatically to an EC2 instance. See .github/workflows/deploy.yml for the full provisioning & deployment flow:

✅ Git-based EC2 pull & reset

✅ Python & Poetry install via pyenv

✅ .env injection from GitHub secrets

✅ Alembic DB migrations

✅ FastAPI server start + systemd SQS worker setup


---

## 🧠 Features

🧾 Resume Parsing & Scoring via OpenAI

🧠 Mock Interview Q&A + Feedback System

📤 Upload/Download Resumes via S3

⚙️ SQS Worker Integration for Async Processing

✉️ Email Feedback Delivery


---

## 🧹 Code Quality
```bash
# Auto-format imports & lint
ruff check . --fix
```
---

## 📫 Contact

For queries, reach out to [@atulx7](https://github.com/atulx7) on GitHub.


---

🧠 Built with ❤️ using FastAPI, AWS, OpenAI, and a touch of MLOps magic.
