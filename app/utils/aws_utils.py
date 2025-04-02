import io
import json
import logging
import uuid
import time

from fastapi import UploadFile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError, BotoCoreError
from app.core.config import settings
queue_logger = logging.getLogger("celery")  # This logger writes to logs/celery.log
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

def upload_resume_to_s3(file: UploadFile, user_id: str):
    """Uploads a resume file to the S3 bucket."""
    file_extension = file.filename.split(".")[-1].lower()
    resume_id = str(uuid.uuid4())
    s3_path = f"{user_id}/resume_{resume_id}.{file_extension}"

    try:
        s3_client.upload_fileobj(file.file, settings.S3_BUCKET_NAME, s3_path, ExtraArgs={"ContentType": file.content_type})
        return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{s3_path}"
    except NoCredentialsError:
        raise Exception("AWS credentials not found")


def generate_presigned_url(s3_url, expiration=3600):
    """Generates a pre-signed URL for secure audio access."""
    bucket_name = settings.S3_BUCKET_NAME
    key = s3_url.split(f"https://{bucket_name}.s3.amazonaws.com/")[-1]

    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration
        )
        return presigned_url
    except Exception as e:
        print(f"Error generating pre-signed URL: {str(e)}")
        return None


def delete_resume_from_s3(s3_url: str):
    """Deletes a resume from S3 given its URL."""
    try:
        # ✅ Extract file key from S3 URL
        s3_file_key = s3_url.split(f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/")[-1]

        # ✅ Delete from S3
        s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_file_key)
        print(f"Deleted from S3: {s3_file_key}")

    except NoCredentialsError:
        raise Exception("AWS credentials not found")
    except ClientError as e:
        print(f"S3 Deletion Failed: {e}")


def download_resume_from_s3(s3_url: str):
    """Downloads the resume file from S3 and returns it as a file-like object."""
    try:
        bucket_name = settings.S3_BUCKET_NAME
        # ✅ Extract the correct file key from S3 URL
        file_key = s3_url.replace(f"https://{bucket_name}.s3.amazonaws.com/", "")  # Removes leading slash
        # 🔹 Debugging: Ensure correct S3 key extraction
        print(f"🔍 Extracted S3 Key: {file_key}")
        # ✅ Check if file exists before downloading
        s3_client.head_object(Bucket=bucket_name, Key=file_key)
        # ✅ Download file as a BytesIO object
        file_obj = io.BytesIO()
        s3_client.download_fileobj(bucket_name, file_key, file_obj)
        file_obj.seek(0)  # Reset pointer to the beginning
        return file_obj
    except NoCredentialsError:
        print("AWS credentials not found")
        raise Exception("AWS credentials not found")

    except ClientError as e:
        print(f"S3 Client Error: {str(e)}")
        if e.response['Error']['Code'] == '404':
            raise Exception("File not found in S3")
        raise Exception(f"S3 Error: {str(e)}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise Exception(f"Error downloading resume from S3: {str(e)}")


def get_file_extension_from_s3_url(s3_url):
    bucket_name = settings.S3_BUCKET_NAME
    key = s3_url.split(f"https://{bucket_name}.s3.amazonaws.com/")[-1]
    file_extension = key.split(".")[-1]
    return file_extension


def transcribe_audio(s3_url: str) -> str:
    """
    Transcribes an audio file stored in S3 using AWS Transcribe.

    Args:
        s3_url (str): The public S3 URL of the audio file.

    Returns:
        str: Transcription text from AWS Transcribe.
    """
    try:
        job_name = f"transcription-{int(time.time())}"  # Unique job name
        media_format = s3_url.split(".")[-1]  # Extract file format (mp3, wav, etc.)
        bucket_name = settings.S3_BUCKET_NAME
        queue_logger.info(f"Fetching audio from bucket: {bucket_name} in region: {settings.AWS_REGION_NAME} to create job: {job_name}")
        queue_logger.info(f"Media format: {media_format} from s3 url: {s3_url}")

        # Start transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_url},
            MediaFormat=media_format,
            LanguageCode="en-US",
            OutputBucketName=bucket_name  # Store result in S3
        )

        # Wait for the transcription job to complete
        while True:
            response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            status = response["TranscriptionJob"]["TranscriptionJobStatus"]

            if status in ["COMPLETED", "FAILED"]:
                break
            time.sleep(5)  # Poll every 5 seconds

        if status == "COMPLETED":
            # ✅ Get transcription file from S3
            transcript_data = s3_client.get_object(Bucket=bucket_name, Key=f"{job_name}.json")
            transcript_text = json.loads(transcript_data["Body"].read().decode("utf-8"))["results"]["transcripts"][0][
                "transcript"]

            # delete the original file if you don't need it anymore:
            s3_client.delete_object(Bucket=bucket_name, Key=f"{job_name}.json")

            queue_logger.info(f"Got transcript: {transcript_text}")
            return transcript_text

        return "Transcription failed or incomplete."

    except (BotoCoreError, NoCredentialsError) as e:
        raise Exception(f"AWS Transcribe error: {str(e)}")


def upload_audio_to_s3(
    content: bytes,
    user_id: str,
    session_id: str,
    filename: str,
    content_type: str = "audio/mpeg"
) -> str:
    """Uploads candidate's response audio to S3 using structured key format."""

    bucket_name = settings.S3_BUCKET_NAME
    file_key = f"{user_id}/mock_interviews/{session_id}/audio_{filename}"

    try:
        s3_client.upload_fileobj(io.BytesIO(content), bucket_name, file_key, ExtraArgs={"ContentType": content_type})
        return f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
    except NoCredentialsError:
        raise Exception("AWS credentials not found")
    except Exception as e:
        raise Exception(f"Error uploading audio to S3: {str(e)}")

