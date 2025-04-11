import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Resume Builder API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    ALLOW_ORIGINS: list = os.getenv("ALLOW_ORIGINS", "http://localhost:3000").split(",")
    MOCK_DATA: bool = os.getenv("MOCK_DATA", "True").lower() in ("true", "1", "yes")
    SEED_DB: bool = os.getenv("SEED_DB", "True").lower() in ("true", "1", "yes")

    # AWS Credentials (Ensure these are set in .env)
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_KEY")
    AWS_REGION_NAME: str = os.getenv("AWS_REGION_NAME")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # SMTP details
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: str = os.getenv("SMTP_PORT")
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", SMTP_USERNAME)

    SQS_MOCK_INTERVIEW_QUEUE_URL: str = os.getenv("SQS_MOCK_INTERVIEW_QUEUE_URL")


settings = Settings()
