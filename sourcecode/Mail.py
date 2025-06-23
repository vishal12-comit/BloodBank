# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, message, to):
    sender_email = "vishaladepu12@gmail.com"           # Your Gmail
    app_password = "utmn tcxo jgaq shaq"               # App Password from Google

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, app_password)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print("Error:", e)
