"""Email utility class"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")

    def send_verification_email(self, to_email: str, verification_token: str):
        """Send verification email
        
        Args:
            to_email (str): Recipient email
            verification_token (str): Verification token
        """
        subject = "이메일 인증"
        verification_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"
        
        html_content = f"""
        <html>
            <body>
                <h2>이메일 인증</h2>
                <p>아래 링크를 클릭하여 이메일을 인증해주세요:</p>
                <a href="{verification_link}">이메일 인증하기</a>
                <p>이 링크는 24시간 동안 유효합니다.</p>
            </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = to_email

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")
