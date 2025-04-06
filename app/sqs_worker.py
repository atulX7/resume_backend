import asyncio
import boto3
import json
import time
from app.services.mock_interview_service import process_mock_interview
from app.database.connection import SessionLocal  # or your actual db init
from app.core.config import settings

sqs = boto3.client(
    'sqs',
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION_NAME
)

def poll_sqs():
    while True:
        messages = sqs.receive_message(
            QueueUrl=settings.SQS_MOCK_INTERVIEW_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        if 'Messages' not in messages:
            continue

        for msg in messages['Messages']:
            try:
                body = json.loads(msg['Body'])
                print(f"🔄 Processing: {body['session_id']}")
                db = SessionLocal()

                asyncio.run(process_mock_interview(
                    db=db,
                    user_id=body['user_id'],
                    session_id=body['session_id'],
                    question_audio_map=body['question_audio_map'],
                    audio_file_map=body['audio_file_map']
                ))

                sqs.delete_message(
                    QueueUrl=settings.MOCK_INTERVIEW_SQS_URL,
                    ReceiptHandle=msg['ReceiptHandle']
                )
                print("✅ Done")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    poll_sqs()
