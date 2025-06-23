import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_email(subject, message, to):
    sender_email = os.getenv("MAIL_USERNAME")      # from Render env
    app_password = os.getenv("MAIL_PASSWORD")      # from Render env

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print("Error:", e)
