# app/tasks/mock_interview.py
import json
import asyncio

from app.celery_app import celery_app
from app.database.connection import SessionLocal  # Adjust the import based on your project
from app.api.routes.mock_interview import process_mock_interview

@celery_app.task(bind=True, max_retries=3)
def process_mock_interview_task(self, user_id: str, session_id: str, question_audio_map_json: str, audio_file_map: dict):
    """
    Celery task wrapper for process_mock_interview.
    - `question_audio_map_json` is passed as a JSON string.
    - `audio_files` is expected to be a list of dicts containing file data.
    """
    db = SessionLocal()  # Create a new DB session for the task
    try:
        # Convert the JSON string back into a dict
        question_audio_map = json.loads(question_audio_map_json)
        # Run the async function in a new event loop
        asyncio.run(process_mock_interview(db, user_id, session_id, question_audio_map, audio_file_map))
    except Exception as exc:
        print(f"❌ Error in celery task for session {session_id}: {exc}")
        raise self.retry(exc=exc, countdown=30)  # 🔁 Retry after 30 seconds
    finally:
        db.close()
