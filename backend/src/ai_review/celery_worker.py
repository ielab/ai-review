import random
import string
import redis
import os
import base64

from celery import Celery

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google.oauth2 import service_account

import logging

logger = logging.getLogger(__name__)

celery = Celery(
    "ai_review",
    broker="redis://ai_review_redis:6379/0",
    result_backend="redis://ai_review_redis:6379/0",
)

# Load configuration from a configuration module
# celery.config_from_object("celeryconfig")

# Connect to Redis
redis_client = redis.StrictRedis(host="redis", port=6379, db=0)


@celery.task(bind=True)
def send_otp_email(self, recipient_email, key):
    otp = generate_otp()

    # Store OTP in Redis with a 5-minute expiration time (600 seconds)
    redis_client.setex(f"{key}:{recipient_email}", 600, otp)

    # Send OTP via Gmail SMTP
    try:
        send_email(recipient_email, otp, key)
        return f"OTP sent to {recipient_email}"
    except Exception as e:
        raise self.retry(exc=e)


def generate_otp(length=6):
    """Generate a random OTP of given length."""
    characters = string.digits
    otp = "".join(random.choice(characters) for i in range(length))
    return otp


# Scopes for Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(__file__), "optimal-analogy-459807-i0-c547a69955cd.json"
)
DELEGATED_USER = "admin@ielab.io"


def create_message(sender, to, subject, message_text):
    logger.info(f"create_message")

    message = MIMEMultipart()
    message["To"] = to
    message["From"] = sender
    message["Reply-To"] = sender
    message["Subject"] = subject

    body = MIMEText(message_text, "plain")
    message.attach(body)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_email(recipient_email, otp, key):
    """Send an email via Gmail API OAuth2"""

    try:
        # Authenticate using the service account
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        # Delegate to the actual user you want to send as
        delegated_credentials = credentials.with_subject(DELEGATED_USER)

        # Build the Gmail API service
        service = build("gmail", "v1", credentials=delegated_credentials)

        # Create the email message
        if key == "sign_up_otp":
            email = create_message(
                sender=DELEGATED_USER,
                to=recipient_email,
                subject=f"{otp} - Your AiReview Registration Code",
                message_text=f"OTP Code: {otp}\n\nPlease enter this code on the AiReview verification page to confirm your account. This OTP expires in 10 minutes.\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nAiReview Team",
            )
        elif key == "reset_password_otp":
            email = create_message(
                sender=DELEGATED_USER,
                to=recipient_email,
                subject=f"{otp} - Your AiReview Password Reset Code",
                message_text=f"OTP Code: {otp}\n\nPlease enter this code on the AiReview password reset page to reset your password. This OTP expires in 10 minutes.\n\nIf you did not request a password reset, please ignore this email or contact support if you suspect unauthorized access.\n\nBest regards,\nAiReview Team",
            )
        elif key == "log_in_otp":
            email = create_message(
                sender=DELEGATED_USER,
                to=recipient_email,
                subject=f"{otp} - Your AiReview Login Code",
                message_text=f"OTP Code: {otp}\n\nPlease enter this code on the AiReview login page to access your account. This OTP expires in 10 minutes.\n\nIf you did not attempt to log in, please ignore this email or contact support if you suspect unauthorized access.\n\nBest regards,\nAiReview Team",
            )

        # Send the email
        result = service.users().messages().send(userId="me", body=email).execute()
        print(f"✅ Email sent! Message ID: {result['id']}")
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")
