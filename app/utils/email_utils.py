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


async def send_email(to_email: str, subject: str, message: str):
    """Sends an email notification to the user."""
    try:
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        if USE_SSL:
            # ✅ Use Implicit TLS (Port 465)
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            # ✅ Use STARTTLS (Port 587)
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()

        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        print(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
