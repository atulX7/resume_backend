import logging
import smtplib
from app.core.config import settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = int(settings.SMTP_PORT)
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD
FROM_EMAIL = settings.FROM_EMAIL
USE_SSL = SMTP_PORT == 465

queue_logger = logging.getLogger("sqs")


async def send_email(to_email: str, subject: str, message: str):
    """Sends an email notification to the user."""
    queue_logger.info(
        f"📤 Preparing to send email to: {to_email} with subject: '{subject}'"
    )

    try:
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        if USE_SSL:
            # ✅ Use Implicit TLS (Port 465)
            queue_logger.info(f"Using SMTP_SSL for server: {SMTP_SERVER}:{SMTP_PORT}")
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            # ✅ Use STARTTLS (Port 587)
            queue_logger.info(f"Using STARTTLS for server: {SMTP_SERVER}:{SMTP_PORT}")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()

        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        queue_logger.info(f"✅ Email sent successfully to {to_email}")
    except smtplib.SMTPException as e:
        queue_logger.error(
            f"❌ SMTP error occurred while sending email to {to_email}: {e}",
            exc_info=True,
        )
    except Exception as e:
        queue_logger.error(
            f"❌ Unexpected error while sending email to {to_email}: {e}", exc_info=True
        )
