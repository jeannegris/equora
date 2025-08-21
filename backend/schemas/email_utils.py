import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email, subject, content):
    from_email = "jeanneio2021@gmail.com"  # já deve estar verificado no SendGrid
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    sg = SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

    response = sg.send(message)
    return response.status_code
