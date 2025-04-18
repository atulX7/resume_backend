import io
import json
import logging
import uuid
import time
from urllib.parse import urlparse

from fastapi import UploadFile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError, BotoCoreError
from app.core.config import settings

logger = logging.getLogger("app")
queue_logger = logging.getLogger("sqs")  # This logger writes to logs/sqs.log

from boto3.s3.transfer import TransferConfig

transfer_config = TransferConfig(
    multipart_threshold=5 * 1024 * 1024,  # Use multipart if file > 5MB
    max_concurrency=10,
    use_threads=True,
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION_NAME,
)

transcribe_client = boto3.client(
    "transcribe",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION_NAME,
)


sqs_client = boto3.client(
    "sqs",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION_NAME,
)


def upload_resume_to_s3(file: UploadFile, user_id: str, session_id: str = None):
    """Uploads a resume file to the S3 bucket."""
    file_extension = file.filename.split(".")[-1].lower()
    resume_id = str(uuid.uuid4())
    if session_id:
        s3_path = f"{user_id}/mock_interviews/{session_id}/data/resume.{file_extension}"
    else:
        s3_path = f"{user_id}/resume_{resume_id}.{file_extension}"

    try:
        file.file.seek(0)  # ✅ Reset pointer to start
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            s3_path,
            ExtraArgs={"ContentType": file.content_type},
        )
        logger.info(f"[S3_UPLOAD] Uploaded resume to: {s3_path}")
        return s3_path
    except NoCredentialsError:
        logger.error("[S3_UPLOAD] AWS credentials not found")
        raise
    except Exception as e:
        logger.error(f"[S3_UPLOAD] Upload failed: {e}", exc_info=True)
        raise


def generate_presigned_url(file_key: str, expiration: int = 3600) -> str:
    """
    Generates a presigned URL for a given file key in the configured S3 bucket.

    Args:
        file_key (str): The relative file key (e.g., "user123/mock_interviews/session456/audio/answer.wav").
        expiration (int): The expiration time in seconds for this URL. The default is 3600 seconds (1 hour).

    Returns:
        str: A presigned URL to access the file.

    Raises:
        Exception: If there is an error generating the presigned URL.
    """
    bucket_name = settings.S3_BUCKET_NAME
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=expiration
        )
        logger.info(f"[PRESIGNED_URL] Successfully generated presigned URL for key: {file_key}")
        return url
    except ClientError as ce:
        logger.error(f"[PRESIGNED_URL] ClientError generating presigned URL for key {file_key}: {ce}", exc_info=True)
        raise
    except Exception as exc:
        logger.error(f"[PRESIGNED_URL] Unexpected error for key {file_key}: {exc}", exc_info=True)
        raise


def delete_resume_from_s3(s3_url: str):
    """Deletes a resume from S3 given its URL."""
    try:
        # ✅ Extract file key from S3 URL
        s3_file_key = s3_url.split(
            f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/"
        )[-1]

        # ✅ Delete from S3
        s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_file_key)
        logger.info(f"[S3_DELETE] Deleted: {s3_file_key}")
    except NoCredentialsError:
        logger.error("[S3_DELETE] AWS credentials not found")
        raise
    except ClientError as e:
        logger.error(f"[S3_DELETE] Client error: {e}", exc_info=True)
        raise


def download_resume_from_s3(s3_url: str):
    """Downloads the resume file from S3 and returns it as a file-like object."""
    try:
        bucket_name = settings.S3_BUCKET_NAME
        # ✅ Extract the correct file key from S3 URL
        file_key = s3_url.replace(
            f"https://{bucket_name}.s3.amazonaws.com/", ""
        )  # Removes leading slash
        # 🔹 Debugging: Ensure correct S3 key extraction
        logger.info(f"[S3_DOWNLOAD] Fetching: {file_key}")
        # ✅ Check if file exists before downloading
        s3_client.head_object(Bucket=bucket_name, Key=file_key)
        # ✅ Download file as a BytesIO object
        file_obj = io.BytesIO()
        s3_client.download_fileobj(bucket_name, file_key, file_obj)
        file_obj.seek(0)  # Reset pointer to the beginning
        return file_obj
    except NoCredentialsError:
        logger.error("[S3_DOWNLOAD] AWS credentials not found")
        raise
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.warning(f"[S3_DOWNLOAD] File not found: {file_key}")
            raise Exception("File not found in S3")
        logger.error(f"[S3_DOWNLOAD] Client error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"[S3_DOWNLOAD] Unexpected error: {e}", exc_info=True)
        raise


def get_file_extension_from_s3_url(s3_url):
    try:
        bucket_name = settings.S3_BUCKET_NAME
        key = s3_url.split(f"https://{bucket_name}.s3.amazonaws.com/")[-1]
        file_extension = key.split(".")[-1]
        logger.info(
            f"[S3_FILE_EXT] Extracted file extension '{file_extension}' from key: {key}"
        )
        return file_extension
    except Exception as e:
        logger.error(
            f"[S3_FILE_EXT] Failed to extract file extension from URL: {s3_url} | Error: {e}",
            exc_info=True,
        )
        raise


def transcribe_audio(file_key: str) -> str:
    """
    Transcribes an audio file stored in S3 using AWS Transcribe.

    Args:
        s3_url (str): The public S3 URL of the audio file.

    Returns:
        str: Transcription text from AWS Transcribe.
    """
    try:
        job_name = f"transcription-{int(time.time())}"  # Unique job name
        media_format = file_key.split(".")[-1].lower()  # Extract file format (mp3, wav, etc.)
        bucket_name = settings.S3_BUCKET_NAME
        queue_logger.info(
            f"[TRANSCRIBE] Starting job: {job_name}, format: {media_format}"
        )
        s3_uri = f"s3://{bucket_name}/{file_key}"
        queue_logger.info(f"Media format: {media_format} from s3 url: {s3_uri}")

        # Start transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            MediaFormat=media_format,
            LanguageCode="en-US",
            OutputBucketName=bucket_name,  # Store result in S3
        )

        # Wait for the transcription job to complete
        while True:
            response = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            status = response["TranscriptionJob"]["TranscriptionJobStatus"]

            if status in ["COMPLETED", "FAILED"]:
                break
            time.sleep(5)  # Poll every 5 seconds

        if status == "COMPLETED":
            # ✅ Get transcription file from S3
            transcript_data = s3_client.get_object(
                Bucket=bucket_name, Key=f"{job_name}.json"
            )
            transcript_text = json.loads(
                transcript_data["Body"].read().decode("utf-8")
            )["results"]["transcripts"][0]["transcript"]

            # delete the original file if you don't need it anymore:
            s3_client.delete_object(Bucket=bucket_name, Key=f"{job_name}.json")
            # ✅ Delete the transcription job from AWS Transcribe
            transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            queue_logger.info(f"[TRANSCRIBE] Transcription complete: {transcript_text}")
            return transcript_text

        queue_logger.warning("[TRANSCRIBE] Transcription failed or incomplete")
        return "Transcription failed or incomplete."

    except (BotoCoreError, NoCredentialsError) as e:
        queue_logger.error(f"[TRANSCRIBE] AWS error: {e}", exc_info=True)
        raise


def send_to_mock_interview_queue(payload: dict):
    try:
        response = sqs_client.send_message(
            QueueUrl=settings.SQS_MOCK_INTERVIEW_QUEUE_URL,
            MessageBody=json.dumps(payload),
        )
        queue_logger.info(f"[SQS] Task queued successfully: {response}")
        return response
    except Exception as e:
        queue_logger.error(f"[SQS] Failed to send message: {e}", exc_info=True)
        raise


def upload_audio_to_s3_sync(
    content: bytes,
    user_id: str,
    session_id: str,
    filename: str,
    content_type: str = "audio/mpeg",
) -> str:
    bucket_name = settings.S3_BUCKET_NAME
    file_key = f"{user_id}/mock_interviews/{session_id}/audio/audio_{filename}"

    try:
        s3_client.upload_fileobj(
            io.BytesIO(content),
            bucket_name,
            file_key,
            ExtraArgs={"ContentType": content_type},
            Config=transfer_config,
        )
        logger.info(f"[AUDIO_UPLOAD] Uploaded audio to: {file_key}")
        return file_key
    except NoCredentialsError:
        logger.error("[AUDIO_UPLOAD] AWS credentials not found")
        raise
    except Exception as e:
        logger.error(f"[AUDIO_UPLOAD] Upload failed: {e}", exc_info=True)
        raise


def upload_mock_interview_data(
    user_id: str, session_id: str, filename: str, data: dict | list
) -> str:
    bucket_name = settings.S3_BUCKET_NAME
    file_key = f"{user_id}/mock_interviews/{session_id}/data/{filename}"
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json.dumps(data),
            ContentType="application/json",
        )
        logger.info(f"[MOCK_DATA_UPLOAD] Uploaded mock data: {file_key}")
        return file_key
    except NoCredentialsError:
        logger.error("[MOCK_DATA_UPLOAD] AWS credentials not found")
        raise
    except Exception as e:
        logger.error(f"[MOCK_DATA_UPLOAD] Failed to upload: {e}", exc_info=True)
        raise


def load_json_from_s3(file_key: str) -> dict | list:
    """
    Downloads and parses a JSON object from an S3 URL.

    Args:
        s3_url (str): Full S3 URL (e.g., https://bucket-name.s3.amazonaws.com/path/to/file.json)

    Returns:
        dict | list: Parsed JSON content.
    """
    bucket_name = settings.S3_BUCKET_NAME
    if not file_key:
        logger.warning("[LOAD_JSON_S3] Empty file key provided")
        return {}

    try:
        # ✅ Check if object exists using the file key
        try:
            s3_client.head_object(Bucket=bucket_name, Key=file_key)
        except ClientError:
            logger.warning(f"[LOAD_JSON_S3] File not found for key: {file_key}")
            return {}

        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        content = obj["Body"].read().decode("utf-8")
        logger.info(f"[LOAD_JSON_S3] Successfully fetched: {file_key}")
        return json.loads(content)
    except Exception as e:
        logger.error(f"[LOAD_JSON_S3] Failed to fetch or parse: {e}", exc_info=True)
        raise
