import os

from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import EmailStr
from sendgrid import sendgrid
from sendgrid.helpers.mail import Mail

load_dotenv()


async def send_verification_email(email: EmailStr, subject: str, content: str):
    try:
        message = Mail(
            from_email=os.getenv("FROM_MAIL"),
            to_emails=email,
            subject=subject,
            html_content=content
        )
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")
