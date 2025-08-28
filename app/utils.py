import os
import jwt  # type: ignore
import smtplib
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from datetime import datetime, timedelta
from fastapi import status
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote
from celery import Celery  # type: ignore
from task_logger import log_background_job
from typing import Optional

load_dotenv()  # Loads variables from .env

celery = Celery(
    "tasks",
    broker="redis://redis_service:6379/0",
    backend="redis://redis_service:6379/0",
)

SMTP_SERVER_RAW = os.getenv("SMTP_SERVER")
if SMTP_SERVER_RAW is None:
    raise ValueError("SMTP_SERVER not set! Check your .env file.")
SMTP_SERVER: str = SMTP_SERVER_RAW

SMTP_PORT_RAW = os.getenv("SMTP_PORT")
if SMTP_PORT_RAW is None:
    raise ValueError("SMTP_PORT not set! Check your .env file.")
SMTP_PORT: int = int(SMTP_PORT_RAW)

SMTP_USER_RAW = os.getenv("SMTP_USER")
if SMTP_USER_RAW is None:
    raise ValueError("SMTP_USER not set! Check your .env file.")
SMTP_USER: str = SMTP_USER_RAW

SMTP_PASS_RAW = os.getenv("SMTP_PASS")
if SMTP_PASS_RAW is None:
    raise ValueError("SMTP_PASS not set! Check your .env file.")
SMTP_PASS: str = SMTP_PASS_RAW

FRONTEND_URL_RAW = os.getenv("FRONTEND_URL")
if FRONTEND_URL_RAW is None:
    raise ValueError("FRONTEND_URL not set! Check your .env file.")
FRONTEND_URL: str = FRONTEND_URL_RAW


def save_to_txt(data: str, filename: str = "history.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = ("--- Model Output ---\n" "Timestamp: {}\n\n{}\n\n").format(
        timestamp, data
    )

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)

    return {
        "message": f"Data successfully saved to {filename}",
        "status": status.HTTP_200_OK,
    }


def save_to_cache(text: str, filename="latest_response.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return {
        "message": f"Data successfully saved to {filename}",
        "status": status.HTTP_200_OK,
    }


save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured data to a text file.",
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information.",
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY") or ""
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now() + expires_delta})
    return jwt.encode(to_encode, str(SECRET_KEY), algorithm="HS256")


def create_verification_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.now() + timedelta(hours=1),  # 1 hour expiry
    }
    return jwt.encode(payload, str(SECRET_KEY), algorithm="HS256")


def send_verification_email(to_email: str, token: str):
    # Encode email for URL safety
    email_param = quote(to_email)
    verification_link = f"{FRONTEND_URL}/verify?token={token}&email={email_param}"

    subject = "Verify Your CuraVia Email"
    html = f"""
    <html>
      <body>
        <p>Hi,<br><br>
           Please verify your email by clicking the link below:<br>
           <a href="{verification_link}">Verify Email</a><br><br>
           If you did not sign up, you can ignore this email.<br><br>
           Thanks,<br>
           CuraVia Team
        </p>
      </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SMTP_USER
    message["To"] = to_email
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, message.as_string())
        return {
            "message": "Verification email sent successfully.",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        return {
            "error": f"Failed to send verification email. {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


@celery.task()
@log_background_job("Send verification email")
def send_email_task(to_email: str, token: str, job_id: Optional[int] = None):
    return send_verification_email(to_email, token)
