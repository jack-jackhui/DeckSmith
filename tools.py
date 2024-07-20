import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
import os

# Load environment variables from .env file
load_dotenv()

EMAIL_HOST_USER=os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD=os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_HOST=os.getenv("EMAIL_HOST")
EMAIL_PORT=os.getenv("EMAIL_PORT")
def send_email(subject, body, to_email):
    from_email = "jack@jackhui.com.au"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())

tools = {
    "send_email": send_email
}

def use_tool(tool_name, *args):
    if tool_name in tools:
        tools[tool_name](*args)