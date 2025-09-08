import os

from requests import session
import jwt  # type: ignore
import smtplib
import bcrypt
from fastapi import status
from models_db import User, BackgroundJobs
from memory import newUser_to_db
from database import SessionLocal, redis_client
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote
from celery import Celery  # type: ignore
from task_logger import log_background_job
from typing import Any, Dict, Optional
from passlib.context import CryptContext

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

SECRET_KEY = os.getenv("JWT_SECRET_KEY") or ""
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set")


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_job(user_id: int, title: str, payload: Dict[str, Any]):
    session = SessionLocal()
    job = BackgroundJobs(
        user_id=user_id, title=title, payload=payload, status="pending"
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    session.close()
    return job


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


def send_verification_email(to_email: str, token: str, username: str, job_id: Optional[int] = None):
    # Encode email for URL safety
    email_param = quote(to_email)
    verification_link = f"{FRONTEND_URL}/verify?token={token}&email={email_param}"

    subject = "Verify Your CuraVia Email"
    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #333333;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        p {{
            color: #555555;
            font-size: 16px;
            line-height: 1.5;
        }}
        .button {{
            display: inline-block;
            background-color: #007BFF;
            color: #ffffff !important;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 6px;
            font-weight: bold;
            margin: 20px 0;
        }}
        @media screen and (max-width: 600px) {{
            .container {{
            padding: 20px;
            margin: 10px;
            }}
            h2 {{
            font-size: 20px;
            }}
            p {{
            font-size: 15px;
            }}
            .button {{
            padding: 12px 24px;
            }}
        }}
        </style>
    </head>
    <body>
        <div class="container">
        <h2>Welcome to CuraVia!</h2>
        <p>Hi {username},<br><br>
            Please verify your email address by clicking the button below:
        </p>
        <p style="text-align:center;">
            <a href="{verification_link}" class="button">Verify Email</a>
        </p>
        <p>If you did not sign up for CuraVia, you can safely ignore this email.</p>
        <p>Thanks,<br>The CuraVia Team</p>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SMTP_USER
    message["To"] = to_email
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, message.as_string())
        return {
            "message": "Verification email sent successfully.",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        print(f"Error sending email: {e}")
        raise


def send_reset_password_email(to_email: str, token: str, username: str, job_id: int = None):
    email_param = quote(to_email)
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}&email={email_param}"

    subject = "Reset Your CuraVia Password"
    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #333333;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        p {{
            color: #555555;
            font-size: 16px;
            line-height: 1.5;
        }}
        .button {{
            display: inline-block;
            background-color: #007BFF;
            color: #ffffff !important;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 6px;
            font-weight: bold;
            margin: 20px 0;
        }}
        @media screen and (max-width: 600px) {{
            .container {{
            padding: 20px;
            margin: 10px;
            }}
            h2 {{
            font-size: 20px;
            }}
            p {{
            font-size: 15px;
            }}
            .button {{
            padding: 12px 24px;
            }}
        }}
        </style>
    </head>
    <body>
        <div class="container">
        <h2>Reset Your Password</h2>
        <p>Hi {username},<br><br>
            Please reset your password by clicking the button below:
        </p>
        <p style="text-align:center;">
            <a href="{reset_link}" class="button">Reset Password</a>
        </p>
        <p>If you did not request a password reset it is advisable to change it to avoid unauthorized access.</p>
        <p>Thanks,<br>The CuraVia Team</p>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SMTP_USER
    message["To"] = to_email
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, message.as_string())
        return {
            "message": "Reset password email sent successfully.",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        print(f"Error sending email: {e}")
        raise


async def signup_user_logic(body):
    session = SessionLocal()
    try:
        existing_user = (
            session.query(User).filter(User.email == body.email).first()
            or session.query(User).filter(User.username == body.username).first()
        )
        if existing_user:
            return {
                "error": "Username or email already used.",
                "status": status.HTTP_409_CONFLICT,
            }

        # Hash the password before storing
        hashed_password = hash_password(body.password)

        user_id = newUser_to_db(
            body.username,
            hashed_password,
            body.first_name,
            body.last_name,
            body.email,
            body.location,
        )

        if not user_id:
            return {
                "error": "Failed to create new user.",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }

        token = create_verification_token(body.email)
        job = create_job(
            user_id=user_id,
            title="Send Verification Email",
            payload={"email": body.email, "token": token, "username": body.username},
        )

        # Queue the task in Celery and attach job_id
        task = send_email_task.apply_async(
            args=[body.email, token, body.username], kwargs={"job_id": job.id}
        )

        # Update job with Celery task_id
        db = SessionLocal()
        job_record = (
            db.query(BackgroundJobs).filter(BackgroundJobs.id == job.id).first()
        )
        # Fix for possible None job_record
        if job_record is not None:
            job_record.task_id = task.id
            db.commit()
        db.close()

        return {
            "message": "User created successfully. "
            "Please check your email to verify your account.",
            "job_id": job.id,
            "task_id": task.id,
            "status": status.HTTP_201_CREATED,
        }
    except Exception as e:
        return {
            "error": f"Failed to create new user: {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    finally:
        session.close()


async def login_user_logic(body):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == body.username).first()
        if not user:
            return {
                "error": "Invalid username or password.",
                "status": status.HTTP_401_UNAUTHORIZED,
            }
        if not user.is_verified:
            return {
                "error": "Your account is not verified. "
                "Please check your email and verify your account to log in.",
                "resend_verification": True,
                "email": user.email,
                "status": status.HTTP_403_FORBIDDEN,
            }
        if verify_password(body.password, user.password):
            access_token = create_access_token(
                {"sub": user.username, "user_id": user.id}
            )
            return {
                "message": "Login successful.",
                "access_token": access_token,
                "user": {
                    "user_id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "is_verified": user.is_verified,
                },
                "status": status.HTTP_200_OK,
            }
        else:
            return {
                "error": "Invalid username or password.",
                "status": status.HTTP_401_UNAUTHORIZED,
            }
    except Exception as e:
        return {
            "error": f"Login failed: {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


async def verify_email_logic(token):
    session = SessionLocal()
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms="HS256")
        email = payload["sub"]

        # Find user and mark verified
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return {
                "error": "User not found.",
                "status": status.HTTP_404_NOT_FOUND,
            }

        if not user.is_verified:
            user.is_verified = True
            session.commit()
            return {
                "message": f"Email {email} has been verified!",
                "status": status.HTTP_200_OK,
            }
        else:
            return {
                "message": f"Email {email} is already verified!",
                "status": status.HTTP_200_OK,
            }

    except jwt.ExpiredSignatureError:
        return {
            "error": "Verification link expired.",
            "status": status.HTTP_400_BAD_REQUEST,
        }
    except jwt.InvalidTokenError:
        return {
            "error": "Invalid verification token.",
            "status": status.HTTP_400_BAD_REQUEST,
        }


async def send_verification_email_logic(request):
    data = await request.json()
    email = data.get("email")
    username = data.get("username")
    if not email or not username:
        return {"error": "Email and username are required.", "status": status.HTTP_400_BAD_REQUEST}

    token = create_verification_token(email)
    result = send_verification_email(email, token, username)
    return result


async def resend_verification_email_logic(body):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == body.email).first()
        if not user:
            return {
                "error": "Email not found.",
                "status": status.HTTP_404_NOT_FOUND,
            }
        if user.is_verified:
            return {
                "message": "Email is already verified.",
                "status": status.HTTP_200_OK,
            }

        token = create_verification_token(body.email)
        job = create_job(
            user_id=user.id,
            title="Resend Verification Email",
            payload={"email": body.email, "token": token, "username": body.username},
        )

        # Queue the task in Celery and attach job_id
        task = send_email_task.apply_async(
            args=[body.email, token, body.username], kwargs={"job_id": job.id}
        )

        # Update job with Celery task_id
        db = SessionLocal()
        job_record = (
            db.query(BackgroundJobs).filter(BackgroundJobs.id == job.id).first()
        )
        # Fix for possible None job_record
        if job_record is not None:
            job_record.task_id = task.id
            db.commit()
        db.close()

        return {
            "message": "Verification email resent. Please check your email.",
            "job_id": job.id,
            "task_id": task.id,
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        return {
            "error": f"Failed to resend verification email: {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    finally:
        session.close()


async def forgot_password_logic(request):
    data = await request.json()
    username = data.get("username")
    if not username:
        return {"error": "Username is required.", "status": status.HTTP_400_BAD_REQUEST}

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            session.close()
            return {"error": "User not found.", "status": status.HTTP_404_NOT_FOUND}
        email = user.email

        # Create a reset token (valid for 1 hour)
        payload = {
            "sub": username,
            "exp": datetime.now() + timedelta(hours=1),
            "action": "reset_password"
        }
        token = jwt.encode(payload, str(SECRET_KEY), algorithm="HS256")
        job = create_job(
            user_id=user.id,
            title="Reset Password Email",
            payload={"email": email, "token": token, "username": username},
        )

        # Queue the task in Celery and attach job_id
        task = send_reset_password_task.apply_async(
            args=[email, token, username], kwargs={"job_id": job.id}
        )

        # Update job with Celery task_id
        db = SessionLocal()
        job_record = (
            db.query(BackgroundJobs).filter(BackgroundJobs.id == job.id).first()
        )
        # Fix for possible None job_record
        if job_record is not None:
            job_record.task_id = task.id
            db.commit()
        db.close()

        return {
            "message": "Reset password email resent. Please check your email.",
            "job_id": job.id,
            "task_id": task.id,
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        return {
        "error": f"Failed to resend reset password email: {e}",
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    finally:
        session.close()



async def reset_password_logic(request):
    data = await request.json()
    token = data.get("token")
    new_password = data.get("password")
    if not token or not new_password:
        return {"error": "Token and new password required.", "status": status.HTTP_400_BAD_REQUEST}

    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=["HS256"])
        username = payload["sub"]
        if payload.get("action") != "reset_password":
            return {"error": "Invalid token action.", "status": status.HTTP_400_BAD_REQUEST}
    except Exception as e:
        return {"error": str(e), "status": status.HTTP_400_BAD_REQUEST}

    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    if not user:
        session.close()
        return {"error": "User not found.", "status": status.HTTP_404_NOT_FOUND}

    # Hash the new password
    hashed_pw = pwd_context.hash(new_password)
    user.password = hashed_pw
    session.commit()
    session.close()

    return {"message": "Password reset successful!", "status": status.HTTP_200_OK}


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls clear_redis_every_hour every hour
    sender.add_periodic_task(3600.0, clear_redis_every_hour.s(), name="Clear Redis hourly")


@celery.task()
@log_background_job("Send verification email")
def send_email_task(to_email: str, token: str, username: str, job_id: Optional[int] = None):
    return send_verification_email(to_email, token, username)


@celery.task()
@log_background_job("Send reset password email")
def send_reset_password_task(to_email: str, token: str, username: str, job_id: Optional[int] = None):
    return send_reset_password_email(to_email, token, username)


@celery.task
def clear_redis_every_hour():
    redis_client.flushall()
    print("Redis cleared by Celery task.")