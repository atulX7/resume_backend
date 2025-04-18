import asyncio
import logging

import boto3
import json

from app.core.logging import setup_logging
from app.services.mock_interview_service import process_mock_interview_worker
from app.database.connection import SessionLocal  # or your actual db init
from app.core.config import settings

setup_logging()

# ✅ Initialize SQS client
sqs = boto3.client(
    "sqs",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION_NAME,
)


queue_logger = logging.getLogger("sqs")  # This logger writes to logs/sqs.log


def poll_sqs():
    queue_logger.info("🔁 Worker started. Polling SQS for messages...")

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=settings.SQS_MOCK_INTERVIEW_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10,
            )

            messages = response.get("Messages", [])
            if not messages:
                queue_logger.debug("🕐 No messages received this cycle.")
                continue

            for message in messages:
                try:
                    queue_logger.info(f"✅ Received message: {message['MessageId']}")
                    body = json.loads(message["Body"])
                    queue_logger.info(f"📦 Message body: {body}")

                    db = SessionLocal()

                    queue_logger.info("⚙️ Starting mock interview processing...")
                    asyncio.run(
                        process_mock_interview_worker(
                            db=db,
                            user_id=body["user_id"],
                            session_id=body["session_id"],
                        )
                    )
                    queue_logger.info("✅ Finished processing mock interview.")

                    # Delete message from SQS
                    sqs.delete_message(
                        QueueUrl=settings.SQS_MOCK_INTERVIEW_QUEUE_URL,
                        ReceiptHandle=message["ReceiptHandle"],
                    )
                    queue_logger.info("🗑️ Deleted message from SQS.")

                except Exception as e:
                    queue_logger.exception(f"❌ Error processing message: {e}")

        except Exception as e:
            queue_logger.exception(f"🔥 Worker polling loop failed: {e}")


if __name__ == "__main__":
    poll_sqs()
