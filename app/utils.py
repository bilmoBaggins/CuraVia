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


load_dotenv()  # Loads variables from .env


SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")  # your email
SMTP_PASS = os.getenv("SMTP_PASS")  # app password if Gmail

FRONTEND_URL = os.getenv("FRONTEND_URL")

def save_to_txt(data: str, filename: str = "history.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = ("--- Research Output ---\n" "Timestamp: {}\n\n{}\n\n").format(
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


save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information.",
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("JWT_SECRET_KEY environment variable not set")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now() + expires_delta})
    return jwt.encode(to_encode, str(SECRET_KEY), algorithm="HS256")


def create_verification_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.now() + timedelta(hours=1)  # 1 hour expiry
    }
    return jwt.encode(payload, str(SECRET_KEY), algorithm="HS256")


def send_verification_email(to_email: str, token: str):
    """
    Send verification email to the user.
    The link now includes the email so frontend can prefill resend.
    """
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
        return{
            "message": "Verification email sent successfully.",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        return{
            "error": f"Failed to send verification email. {e}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
